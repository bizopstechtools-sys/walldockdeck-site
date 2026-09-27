/* WallDockDeck — capture slots and the Tomonagi post.
 *
 * The posting logic is lifted from the working prototype so nothing regresses:
 * one person = one lead via external_id, keepalive only under 60KB, and a retry
 * on network failure or 5xx only — never on a 4xx, which would burn a slot.
 *
 * What is new: every submission carries the six hidden fields. They are the
 * whole interface between the site and the CRM, so they are built in one place.
 */
(function () {
  'use strict';

  var TMG = 'https://tomonagi.com/api/public/intake/wall-dock-deck';
  var WHO_KEY = 'wdd_who';
  var WHO_TTL = 1000 * 60 * 60 * 24 * 60;   // 60 days

  /* ---------- who this visitor is, remembered across pages ---------- */
  function loadWho() {
    try {
      var w = JSON.parse(localStorage.getItem(WHO_KEY) || '{}');
      if (w.at && Date.now() - w.at > WHO_TTL) return {};
      return w || {};
    } catch (e) { return {}; }
  }
  function saveWho(w) {
    try { w.at = Date.now(); localStorage.setItem(WHO_KEY, JSON.stringify(w)); } catch (e) {}
  }
  var who = loadWho();

  /* ---------- identity ---------- */
  function h(s) {
    s = String(s || '').trim().toLowerCase();
    var n = 5381;
    for (var i = 0; i < s.length; i++) n = ((n << 5) + n + s.charCodeAt(i)) >>> 0;
    return n.toString(36);
  }
  /* Property alone is wrong: a new owner is a new lead, and consent never
     transfers with the property. */
  function extIdFor(addr, email, phone) {
    return 'wdd:' + h(addr || 'noaddr') + ':' + h(email || phone || '');
  }

  /* ---------- utm passthrough ---------- */
  function utm() {
    var out = {}, q = new URLSearchParams(location.search);
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'fbclid']
      .forEach(function (k) { if (q.get(k)) out[k] = q.get(k); });
    var a = q.get('agent') || q.get('a');
    if (a) out.agent_id = a;
    return out;
  }

  /* An agent link (?agent=xyz) sticks for the session so the report that comes
     out the far end still carries their name. */
  (function stickAgent() {
    var a = utm().agent_id;
    try {
      if (a) sessionStorage.setItem('wdd_agent', a);
    } catch (e) {}
  })();
  function agentId() {
    try { return sessionStorage.getItem('wdd_agent') || ''; } catch (e) { return ''; }
  }

  /* ---------- the six hidden fields ---------- */
  function meta(el) {
    var d = document.body.dataset;
    return {
      slot_id:   el.dataset.slot || '',
      offer_id:  el.dataset.offer || '',
      page_path: location.pathname,
      cluster:   el.dataset.cluster || d.cluster || '',
      city:      el.dataset.city || d.city || '',
      agent_id:  agentId()
    };
  }

  /* ---------- post ---------- */
  function postLead(p) {
    var body = JSON.stringify(p);
    var keep = body.length < 60000;   // browsers reject keepalive bodies over 64KB
    function post(retry) {
      var again = function () {
        return new Promise(function (ok) { setTimeout(ok, 1500); }).then(function () { return post(false); });
      };
      return fetch(TMG, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: body, keepalive: keep, mode: 'cors'
      })
        .then(function (res) { if (res.status >= 500 && retry) return again(); return res; })
        .catch(function () { if (retry) return again(); });
    }
    return post(true);
  }

  function send(el, fields, action) {
    var m = meta(el);
    var p = Object.assign({
      full_name: fields.full_name || '',
      email: fields.email || '',
      phone: fields.phone || '',
      property_address: fields.property_address || '',
      lead_source_action: action || 'resource_request',
      page: location.pathname
    }, fields, m, utm());

    p.external_id = extIdFor(p.property_address || who.addr, p.email, p.phone);

    who.name = p.full_name || who.name;
    who.email = p.email || who.email;
    who.phone = p.phone || who.phone;
    who.addr  = p.property_address || who.addr;
    who.extId = p.external_id;
    saveWho(who);

    Object.keys(p).forEach(function (k) { if (p[k] === '' || p[k] == null) delete p[k]; });
    return postLead(p);
  }

  /* ---------- wire every slot on the page ---------- */
  var EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

  function wire(el) {
    var form = el.querySelector('form');
    if (!form) return;
    var btn = form.querySelector('button');

    /* Prefill what we already know. Nobody should type their email twice. */
    var e = form.querySelector('[name=email]');
    if (e && !e.value && who.email) e.value = who.email;
    var n = form.querySelector('[name=full_name]');
    if (n && !n.value && who.name) n.value = who.name;

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      el.classList.remove('bad');

      var fields = {};
      Array.prototype.forEach.call(form.elements, function (i) {
        if (!i.name) return;
        if (i.type === 'checkbox') { fields[i.name] = i.checked ? 'yes' : 'no'; return; }
        fields[i.name] = (i.value || '').trim();
      });

      if (fields.email !== undefined && !EMAIL.test(fields.email)) {
        el.classList.add('bad');
        var err = el.querySelector('.err');
        if (err) err.textContent = 'That email does not look right.';
        if (e) e.focus();
        return;
      }
      if (fields.consent === 'yes') {
        fields.consent_given = 'yes';
        fields.consent_timestamp = new Date().toISOString();
        fields.consent_text = el.dataset.consent || '';
      }
      delete fields.consent;

      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }

      /* Confirm regardless of what the network did. A failed post is ours to
         retry, not the visitor's problem to look at. */
      send(el, fields, el.dataset.action).then(function () {
        el.classList.add('sent');
      }).catch(function () {
        el.classList.add('sent');
      });
    });
  }

  function init() {
    document.querySelectorAll('[data-slot]').forEach(wire);

    /* Guide and download opens are a real signal and cost nothing to capture. */
    document.querySelectorAll('a[href$=".pdf"]').forEach(function (a) {
      a.addEventListener('click', function () {
        if (!who.email && !who.phone) return;
        postLead({
          full_name: who.name || '', email: who.email || '', phone: who.phone || '',
          external_id: who.extId || extIdFor(who.addr, who.email, who.phone),
          guide_opened_at: new Date().toISOString(),
          guide_opened_edition: (a.getAttribute('href').split('/').pop() || '').replace('.pdf', ''),
          page_path: location.pathname
        });
      });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  window.WDD = { send: send, extIdFor: extIdFor, who: who };
})();
