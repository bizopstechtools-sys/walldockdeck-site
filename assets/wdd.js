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

  var TMG_BASE = 'https://tomonagi.com/api/public/intake/';
  var TMG_GENERAL = 'wall-dock-deck';
  /* Each offer posts to its own Tomonagi form, so the matching delivery email fires
     (height sheet, checklist, county guide...). Anything else goes to the general form.
     If an offer form ever refuses a post (4xx), the lead is re-sent to the general form
     so nobody is lost. */
  var FORM_FOR_OFFER = {
    height_sheet: 'wdd-height-sheet', warning_list: 'wdd-warning-signs',
    county_guide: 'wdd-county-guide', bid_compare: 'wdd-quote-check',
    book_inspect: 'wdd-book-inspection', agent_tools: 'wdd-agent-access',
    fifteen_q: 'wdd-buyer-checklist', deck_check: 'wdd-deck-checklist'
  };
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
  // Fable 10/5: one person = one id, whatever they type later. The id used to include the address, so a visitor who
  // asked for a sheet (no address) and later booked (address required) became two leads in the CRM, and the booking
  // never stopped their emails. A new owner has a new email, so email alone is enough. The 'noaddr' segment is kept
  // so ids for people who never gave an address are unchanged.
  function extIdFor(addr, email, phone) {
    return 'wdd:' + h('noaddr') + ':' + h(email || phone || '');
  }

  /* ---------- utm passthrough ---------- */
  /* Campaign links routinely put their tags after the fragment --
     walldockdeck.com/#/book?utm_source=... -- where location.search is EMPTY and
     the whole tag is silently lost. Read both halves. Then remember what we saw,
     so someone who lands from an email, reads two pages and converts later still
     carries the attribution that brought them. */
  function params() {
    var out = new URLSearchParams(location.search);
    var h = location.hash || '';
    var i = h.indexOf('?');
    if (i > -1) {
      new URLSearchParams(h.slice(i + 1)).forEach(function (v, k) {
        if (!out.has(k)) out.append(k, v);
      });
    }
    return out;
  }

  var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term',
                  'utm_content', 'gclid', 'fbclid'];

  function utm() {
    var out = {}, q = params();
    UTM_KEYS.forEach(function (k) {
      var v = q.get(k);
      try {
        if (v) sessionStorage.setItem('wdd_' + k, v);
        else v = sessionStorage.getItem('wdd_' + k);
      } catch (e) {}
      if (v) out[k] = v;
    });
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
      cluster:     el.dataset.cluster || d.cluster || '',
      city:        el.dataset.city || d.city || '',
      county:      el.dataset.county || d.county || '',
      county_slug: el.dataset.countySlug || d.countySlug || '',
      agent_id:    agentId()
    };
  }

  /* ---------- post ---------- */
  function postLead(p, slug) {
    slug = slug || TMG_GENERAL;
    var TMG = TMG_BASE + slug;
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
        .then(function (res) {
          if (res.status >= 500 && retry) return again();
          if (res.status >= 400 && res.status < 500 && slug !== TMG_GENERAL) return postLead(p, TMG_GENERAL);
          return res;
        })
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

    if (!p.first_name && p.full_name) p.first_name = String(p.full_name).split(/\s+/)[0];
    Object.keys(p).forEach(function (k) { if (p[k] === '' || p[k] == null) delete p[k]; });
    return postLead(p, FORM_FOR_OFFER[m.offer_id]);
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
      /* Record the exact sentence the person read, not a yes/no flag. The
         wording lives on the label, so this stays correct if the label changes. */
      if (fields.consent === 'yes') {
        var lab = el.querySelector('.consent[data-consent]');
        fields.consent_given = 'yes';
        fields.consent_timestamp = new Date().toISOString();
        fields.consent_text = (lab && lab.dataset.consent) ||
          (lab && lab.textContent.trim()) || '';
        fields.consent_page = location.pathname;
      } else if (fields.consent === 'no') {
        fields.consent_given = 'no';
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
