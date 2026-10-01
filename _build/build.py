#!/usr/bin/env python3
"""WallDockDeck static site generator.

Reads the CSVs in _build/data and writes real directories with index.html so
every page has a clean URL. Nothing in the existing repo is touched: index.html
(the live prototype) and /guides are left exactly as they are.

Run:  python3 _build/build.py
"""
import csv, html, os, re, shutil, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "_build", "data")
SITE = "https://walldockdeck.com"
TODAY = date.today().isoformat()

# Pages the generator owns. Anything else in the repo is left alone.
OWNED = ["agents", "luxury", "resources", "tools", "downloads", "guides-index",
         "directory", "glossary", "coverage", "privacy", "sms-terms"]

def load(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf8") as f:
        return list(csv.DictReader(f))

CITIES   = load("Cities.csv")
TOPICS   = load("Topics.csv")
CLUSTERS = load("Clusters.csv")
OFFERS   = {o["offer_id"]: o for o in load("Offers.csv")}
SLOTS    = {s["slot_id"]: s for s in load("Slots.csv")}
CT       = load("CityTopics.csv")

CITY  = {c["slug"]: c for c in CITIES}
TOPIC = {t["slug"]: t for t in TOPICS}
CLUS  = {c["slug"]: c for c in CLUSTERS}

# Only verified rows become pages. This is the rule the whole position rests on.
LIVE = [r for r in CT if r["status"] == "verified"]
LIVE_KEY = {(r["citySlug"], r["topicSlug"]) for r in LIVE}

# Topic slug -> cluster slug. Topics.csv carries a display cluster name; map it.
CLUSTER_OF_NAME = {
    "Compliance": "seawall-compliance",
    "Failing":    "failing-seawall",
    "Dock":       "docks-and-lifts",
    "Deck":       "decks",
}

def e(s):
    return html.escape(str(s or ""), quote=True)

def title_case(slug):
    out = " ".join(w.capitalize() for w in str(slug or "").split("-"))
    return out.replace("By The Sea", "by-the-Sea").replace("Lauderdale By-the-Sea", "Lauderdale-by-the-Sea")

MARK = ('<svg viewBox="0 0 34 34" width="28" height="28" aria-hidden="true"><rect width="34" height="34" rx="7" fill="#123549"/>'
        '<rect x="7" y="8" width="5" height="18" rx="1" fill="#7FC6CF"/>'
        '<rect x="14.5" y="14" width="12.5" height="3.5" rx="1" fill="#fff"/>'
        '<rect x="14.5" y="20" width="12.5" height="3.5" rx="1" fill="#E0701A"/>'
        '<path d="M5 28.5c3-1.6 6-1.6 9 0s6 1.6 9 0 6-1.6 7 0" stroke="#7FC6CF" stroke-width="1.6" fill="none"/></svg>')

FONTS = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Archivo:wdth,wght@75..100,400..800&family=Source+Sans+3:wght@400;600;700'
         '&family=IBM+Plex+Mono:wght@400;500&family=Cormorant+Garamond:wght@400;600&display=swap">')


def head_(title, desc, path, body_class="", body_data=""):
    canon = SITE + path
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc[:158])}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc[:158])}">
<meta property="og:url" content="{canon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="WallDockDeck">
{FONTS}
<link rel="stylesheet" href="/assets/wdd.css">
</head>
<body{(' class="'+body_class+'"') if body_class else ''}{body_data}>
<header class="site"><div class="wrap">
  <a class="brand" href="/">{MARK}<b>Wall<i>Dock</i>Deck</b></a>
  <nav>
    <a href="/resources/">Resources</a>
    <a href="/tools/">Tools</a>
    <a href="/directory/">Directory</a>
    <a href="/agents/">For Agents</a>
    <a class="cta" href="/#/start">Get a Shore Score</a>
  </nav>
</div></header>
"""


FOOT = f"""<footer class="foot"><div class="wrap">
  <div>
    <h4>Resources</h4>
    <a href="/resources/seawall-compliance/">Seawall rules</a>
    <a href="/resources/failing-seawall/">A failing seawall</a>
    <a href="/resources/docks-and-lifts/">Docks &amp; lifts</a>
    <a href="/resources/buying-and-selling/">Buying or selling</a>
  </div>
  <div>
    <h4>Tools</h4>
    <a href="/tools/">All tools</a>
    <a href="/#/start">Shore Score</a>
    <a href="/resources/what-it-costs/">What it costs</a>
    <a href="/glossary/">Glossary</a>
  </div>
  <div>
    <h4>Coverage</h4>
    <a href="/coverage/">Where we work</a>
    <a href="/directory/">Surveyors &amp; marinas</a>
    <a href="/agents/">For agents</a>
  </div>
  <div>
    <h4>Company</h4>
    <a href="/privacy/">Privacy</a>
    <a href="/sms-terms/">SMS terms</a>
  </div>
  <p class="legal"><strong style="color:#B9CCD6">WallDockDeck</strong> &middot; Seawalls, docks &amp; waterfront decks &middot; Florida Keys to Palm Beach<br>
  Shore Scores are screenings based on public data and owner answers, not engineering inspections. Inspections and construction are performed by licensed contractors.
  Local rules are published with their code section and the date we verified them; confirm with your building department before you rely on one. Updated {TODAY}.</p>
</div></footer>
<script src="/assets/wdd.js" defer></script>
</body></html>
"""


def slot(slot_id, city="", cluster=""):
    """Render one capture slot. The offer comes from Slots -> Offers, so the
    copy and the placement are separate variables you can move one at a time."""
    s = SLOTS.get(slot_id)
    if not s:
        return ""
    o = OFFERS.get(s["currentOffer"])
    if not o or o.get("live", "yes") == "no":
        return ""
    style = (" " + s["style"]) if s.get("style") else ""
    fields = [f for f in (o.get("fields") or "").split("|") if f]

    inputs = []
    if "first_name" in fields or "name" in fields:
        inputs.append('<input name="full_name" type="text" placeholder="First name" autocomplete="given-name" required>')
    if "email" in fields:
        inputs.append('<input name="email" type="email" placeholder="Email" autocomplete="email" required>')
    if "phone" in fields:
        inputs.append('<input name="phone" type="tel" placeholder="Phone" autocomplete="tel" required>')
    if "address" in fields:
        inputs.append('<input name="property_address" type="text" placeholder="Property address" autocomplete="street-address">')
    if "brokerage" in fields:
        inputs.append('<input name="brokerage" type="text" placeholder="Brokerage">')
    if "office" in fields:
        inputs.append('<input name="office" type="text" placeholder="Office or team">')
    if not inputs:
        inputs.append('<input name="email" type="email" placeholder="Email" autocomplete="email" required>')

    fine = f'<p class="fine">{e(o.get("fine",""))}</p>' if o.get("fine") else ""
    return f"""<div class="slot{style}" data-slot="{e(slot_id)}" data-offer="{e(o['offer_id'])}"
     data-city="{e(city)}" data-cluster="{e(cluster)}" data-action="resource_request">
  <h3>{e(o['headline'])}</h3>
  <p>{e(o['body'])}</p>
  <form novalidate>
    {''.join(inputs)}
    <button type="submit">{e(o.get('button','Send it'))}</button>
  </form>
  <p class="err"></p>
  {fine}
  <p class="done">Done &mdash; it is on the way to your inbox.</p>
</div>"""


def write(path, content):
    """path is a URL path like /agents/ ; writes <root>/agents/index.html"""
    d = os.path.join(ROOT, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf8") as f:
        f.write(content)
    return path


PAGES = []   # (path, lastmod, priority)


# ---------------------------------------------------------------- matrix pages
def detail_rows(raw):
    rows = [r.strip() for r in str(raw or "").split("|") if r.strip()]
    if not rows:
        return ""
    out = []
    for r in rows:
        parts = r.split("::")
        label = parts[0].strip()
        value = "::".join(parts[1:]).strip() if len(parts) > 1 else ""
        out.append(f'<div><b>{e(label)}</b><span>{e(value)}</span></div>')
    return f'<div class="rows">{"".join(out)}</div>'


def build_matrix():
    # county pages that exist, so a city page can link up to its own county
    region_for = {r["region"]: f'/{r["regionSlug"]}/{r["serviceSlug"]}/'
                  for r in load_regions()}
    n = 0
    for r in LIVE:
        cs, ts = r["citySlug"], r["topicSlug"]
        city, topic = CITY.get(cs), TOPIC.get(ts)
        if not city or not topic:
            continue
        cluster = CLUSTER_OF_NAME.get(r.get("cluster", ""), "seawall-compliance")
        path = f"/{cs}/{ts}/"
        q = r.get("question") or topic["question"].replace("{city}", city["city"])
        title = f'{q} | WallDockDeck'
        desc = (r.get("qualifier") or "").strip() or q

        # Rule 2 — same question, nearby. Only links to pages that exist.
        near = [s for s in (city.get("nearby") or "").split("|")
                if s and (s, ts) in LIVE_KEY][:4]
        near_html = ""
        if near:
            links = "".join(
                f'<a href="/{s}/{ts}/"><em>{e(CITY[s]["county"])}</em>{e(CITY[s]["city"])}</a>'
                for s in near)
            near_html = f"""<section class="tint"><div class="wrap">
  <div class="shead"><h2>The same question, nearby</h2>
  <p>The rule changes at the city line, not the county line.</p></div>
  <div class="strip">{links}</div>
</div></section>"""

        # Rule 3 — other questions about this city.
        others = [x for x in LIVE if x["citySlug"] == cs and x["topicSlug"] != ts][:7]
        others_html = ""
        if others:
            links = "".join(
                f'<a href="/{x["citySlug"]}/{x["topicSlug"]}/">'
                f'<em>{e(TOPIC[x["topicSlug"]]["topic"])}</em>{e(x["question"])}</a>'
                for x in others if x["topicSlug"] in TOPIC)
            others_html = f"""<section><div class="wrap">
  <div class="shead"><h2>Other questions about {e(city['city'])}</h2></div>
  <div class="strip">{links}</div>
</div></section>"""

        cl = CLUS.get(cluster, {})
        body = head_(title, desc, path,
                    body_data=f' data-city="{e(cs)}" data-cluster="{e(cluster)}"')
        county_url = region_for.get(city["county"])
        county_crumb = (f'<a href="{county_url}">{e(city["county"])} County</a> <span>/</span>\n  '
                        if county_url else "")
        body += f"""<nav class="crumbs"><div class="wrap">
  <a href="/">Home</a> <span>/</span>
  <a href="/resources/">Resources</a> <span>/</span>
  <a href="/resources/{e(cluster)}/">{e(cl.get('cluster','Resources'))}</a> <span>/</span>
  {county_crumb}{e(city['city'])}
</div></nav>

<div class="answer"><div class="wrap">
  <span class="eyebrow">{e(city['city'])} &middot; {e(city['county'])} County</span>
  <h1>{e(q)}</h1>
  <div class="figure"><b>{e(r.get('headline_answer',''))}</b><span>{e(r.get('unit',''))}</span></div>
  <p class="qualifier">{e(r.get('qualifier',''))}</p>
  <p class="src"><b>Source:</b> {e(r.get('source',''))}{(' &middot; <b>Verified</b> ' + e(r.get('verified_date',''))) if r.get('verified_date') else ''}</p>
</div></div>

{('<section><div class="wrap"><div class="shead"><h2>The detail</h2></div>' + detail_rows(r.get('detail_rows')) + '</div></section>') if r.get('detail_rows') else ''}

<section class="tint"><div class="wrap">{slot('H1', cs, cluster)}</div></section>

{(f'<section class="tint"><div class="wrap"><div class="shead"><h2>The county rule behind this</h2><p>What applies across {e(city["county"])} County, and where each city departs from it.</p></div><div class="strip"><a href="{county_url}"><em>{e(city["county"])} County</em>Seawall requirements county-wide</a></div></div></section>') if county_url else ''}

{near_html}
{others_html}

<section><div class="wrap">{slot('H2', cs, cluster)}</div></section>
"""
        body += FOOT
        write(path, body)
        PAGES.append((path, TODAY, "0.8"))
        n += 1
    return n


# --------------------------------------------------------------- cluster hubs
def build_clusters():
    for c in sorted(CLUSTERS, key=lambda x: int(x["order"])):
        slug = c["slug"]
        rows = [r for r in LIVE
                if CLUSTER_OF_NAME.get(r.get("cluster", "")) == slug]
        cards = "".join(
            f'<a class="card" href="/{r["citySlug"]}/{r["topicSlug"]}/">'
            f'<span class="k">{e(CITY[r["citySlug"]]["city"])} &middot; {e(CITY[r["citySlug"]]["county"])}</span>'
            f'<h3>{e(r["question"])}</h3>'
            f'<p>{e((r.get("qualifier") or "")[:150])}</p>'
            f'<span class="meta">{e(r.get("headline_answer",""))} {e(r.get("unit",""))}</span></a>'
            for r in rows if r["citySlug"] in CITY)

        guides = "".join(
            f'<a class="card" href="/guides/{g}.pdf"><span class="k">Regional guide</span>'
            f'<h3>{n}</h3><p>Permits, agencies and the order they go in, for {n}.</p>'
            f'<span class="meta">Open the guide &rarr;</span></a>'
            for g, n in (("broward", "Broward"), ("miami", "Miami-Dade"),
                         ("palm", "Palm Beach"), ("keys", "Florida Keys")))
        counties = "".join(
            f'<a class="card" href="/{r["regionSlug"]}/{r["serviceSlug"]}/">'
            f'<span class="k">{e(r["region"])} County</span><h3>{e(r["question"])}</h3>'
            f'<p>{e(r["qualifier"][:140])}</p><span class="meta">Read it &rarr;</span></a>'
            for r in load_regions())

        path = f"/resources/{slug}/"
        title = f'{c["cluster"]} | WallDockDeck Resources'
        desc = f'{c["who"]}. {c["asset"]} plus the local rule for your city.'
        body = head_(title, desc, path, body_data=f' data-cluster="{e(slug)}"')
        body += f"""<nav class="crumbs"><div class="wrap">
  <a href="/">Home</a> <span>/</span> <a href="/resources/">Resources</a> <span>/</span> {e(c['cluster'])}
</div></nav>
<div class="answer"><div class="wrap">
  <span class="eyebrow">Resources</span>
  <h1>{e(c['cluster'])}</h1>
  <p class="qualifier">{e(c['who'])}. Start with the rule for your own city, then the checklist.</p>
</div></div>
{('<section><div class="wrap"><div class="shead"><h2>Answers by city</h2><p>The rule where you are, with the code section and the date we checked it.</p></div><div class="cards">' + cards + '</div></div></section>') if cards else ''}

<section><div class="wrap">
  <div class="shead"><h2>Start with your county</h2>
  <p>The rule that applies across the whole county, and where the cities inside it depart from it.</p></div>
  <div class="cards">{counties}</div>
</div></section>

<section class="tint"><div class="wrap">
  <div class="shead"><h2>The guide for your area</h2>
  <p>Which agencies are involved, what they want, and the order they want it in.</p></div>
  <div class="cards">{guides}</div>
</div></section>
<section class="tint"><div class="wrap">{slot('H2', '', slug)}</div></section>
"""
        body += FOOT
        write(path, body)
        PAGES.append((path, TODAY, "0.7"))
    return len(CLUSTERS)


# ------------------------------------------------------------- resources hub
def build_resources_hub():
    cards = "".join(
        f'<a class="card" href="/resources/{e(c["slug"])}/">'
        f'<span class="k">{e(c["asset"])}</span>'
        f'<h3>{e(c["cluster"])}</h3><p>{e(c["who"])}.</p>'
        f'<span class="meta">Open &rarr;</span></a>'
        for c in sorted(CLUSTERS, key=lambda x: int(x["order"])))

    path = "/resources/"
    body = head_("Waterfront Resources | WallDockDeck",
                "Seawall, dock and deck answers for every waterfront city from the Keys to Palm Beach — the local rule, the code section, and the date we checked it.",
                path)
    body += f"""<div class="answer"><div class="wrap">
  <span class="eyebrow">Resources</span>
  <h1>Seawall answers, before anyone asks</h1>
  <p class="qualifier">The height your city requires, whether you need a permit, what a dock can be, and what real jobs have cost.
  Every rule carries its code section and the date we verified it.</p>
</div></div>
<section><div class="wrap">
  <div class="shead"><h2>Start with what applies to you</h2></div>
  <div class="cards">{cards}</div>
</div></section>
<section class="tint"><div class="wrap">{slot('H2')}</div></section>
"""
    body += FOOT
    write(path, body)
    PAGES.append((path, TODAY, "0.9"))


# ------------------------------------------------------- agents and luxury
AGENT_BENEFITS = [
    ("One", "You find out early",
     "Found at the listing appointment, it is an easy pricing conversation. Found on day nine of the inspection period, it is a dead file."),
    ("Two", "You negotiate with a number",
     "Listing side it defends the price. Buy side it wins a credit. Either way it beats &ldquo;the wall looks old&rdquo;."),
    ("Three", "You have the answer",
     "Nobody else in the room can say what the city requires, or what size boat the dock will take."),
    ("Four", "You stay relevant all year",
     "King tides in October, storm prep in June &mdash; under your name, ready to forward to your sphere."),
]
AGENT_TOOLS = [
    ("Tool 01", "Seawall Condition Check",
     "A Shore Score for the seawall, dock and deck at any address &mdash; before listing, or during the inspection period."),
    ("Tool 02", "Local Rule Sheet",
     "The height your city requires, the datum, and the code section. One page."),
    ("Tool 03", "Will It Fit?",
     "Whether your buyer&rsquo;s boat can reach that dock and tie up there."),
]


def build_agents(luxury=False):
    path = "/luxury/" if luxury else "/agents/"
    slots_shown = ["A1", "A2", "A5"] if luxury else ["A1", "A2", "A3", "A4", "A5"]
    kicker = "Luxury Real Estate" if luxury else "Waterfront Agent Tools"
    title = ("Luxury Waterfront Tools for Agents | WallDockDeck" if luxury
             else "Waterfront Tools for Agents | WallDockDeck")
    desc = ("See what shape the seawall is in, what the city requires, and what a repair would cost — "
            "on any waterfront property, listing side or buy side.")

    ben = "".join(
        f'<div class="card"><span class="k">{n}</span><h3>{t}</h3><p>{p}</p></div>'
        for n, t, p in AGENT_BENEFITS)
    tools = "".join(
        f'<div class="card"><span class="k">{n}</span><h3>{t}</h3><p>{p}</p></div>'
        for n, t, p in AGENT_TOOLS)

    body = head_(title, desc, path,
                body_class="lux" if luxury else "",
                body_data=' data-cluster="agent"')
    body += f"""<div class="answer"><div class="wrap">
  <span class="eyebrow">{kicker}</span>
  <h1>Waterfront closings are slipping on the seawall.</h1>
  <p class="qualifier">Your deals don&rsquo;t have to. See what shape the seawall is in, what your city requires,
  and what a repair would cost &mdash; on any waterfront property, listing side or buy side.</p>
</div></div>

<section><div class="wrap">{slot(slots_shown[0], '', 'agent')}</div></section>

<section class="tint"><div class="wrap">
  <div class="shead"><h2>What changes the day you start using our resources</h2></div>
  <div class="cards four">{ben}</div>
</div></section>

<section><div class="wrap">{slot('A2', '', 'agent')}</div></section>

<section class="tint"><div class="wrap">
  <div class="shead"><h2>Seawall answers, before anyone asks</h2>
  <p>Send your link. Your client answers a few questions and gets their Shore Score.
  The report carries your name and photo, and a copy comes to you. It is clearly our report, provided by you.</p></div>
  <div class="cards">{tools}</div>
</div></section>

{''.join(f'<section><div class="wrap">{slot(s, "", "agent")}</div></section>' for s in slots_shown[2:-1])}

<section class="tint"><div class="wrap">
  <div class="shead"><h2>Know the wall. Keep the deal.</h2></div>
  {slot('A5', '', 'agent')}
</div></section>
"""
    body += FOOT
    write(path, body)
    PAGES.append((path, TODAY, "0.9"))


# ------------------------------------------------------------- what it costs
OPTIONS = [
    ("Lightest", "Repair the panels, restore the cap",
     "Crack routing, partial-depth concrete repair, two coats of protective coating.",
     370000, "about $370,000"),
    ("Middle", "Repair the panels, replace the cap",
     "The same panel repair, but the cap is demolished and rebuilt in full.",
     470000, "about $470,000"),
    ("Heaviest", "Build a new wall in front of the old one",
     "New panels and new batter piles throughout. Needs an exemption from the city.",
     720000, "about $720,000"),
]

COMPARABLES = [
    ("Fort Lauderdale &middot; 2026", 140000, "Seawall and dock replacement",
     "Roughly 80 linear feet of new seawall and cap with nine king piles, nine batter piles and eight panels. "
     "About 660 square feet of composite dock and finger pier, plus decking over the new cap. "
     "Demolition of around 720 square feet of old dock and seventeen timber piles included.",
     "Composite decking ran around $12 per square foot. A return wall was priced separately at about $3,500, only if it proved necessary."),
    ("Coral Gables &middot; 2026", 125000, "Boat lift",
     "A single lift sized to a specific boat, with capacity, water depth, bunk spacing and decking colour all specified.",
     "The city also required a $15,000 refundable bond, on top of the contract price."),
]

EXCLUSIONS = [
    ("Permit fees and bonds", "Paid by the owner directly to the agencies. Non-refundable."),
    ("City bonds", "Coral Gables required $15,000, refundable. Other cities differ."),
    ("Surveys", "Tree, as-built, bathymetric and geotechnical surveys, including pile-length recommendations, and coral avoidance or relocation plans. All supplied and paid for by the owner."),
    ("Benthic survey", "About $2,000, if the agencies ask for one."),
    ("Electrical and plumbing", "Excluded."),
    ("Mitigation", "Moving or replacing sea grass, coral and rip rap is the owner's cost."),
    ("Landscaping", "Trees by others, pavers by others, turf not included."),
    ("Interruption costs", "Overtime, idle time and travel, if the site is not available full time."),
]

TERMS = [
    ("Warranty", "One year"),
    ("Late payment", "1.5% per month after 30 days"),
    ("Price valid for", "20 days"),
    ("Default", "15% liquidated damages"),
    ("Salvage", "The contractor keeps it"),
]


def build_costs():
    path = "/resources/what-it-costs/"
    title = "What a Seawall Actually Costs | WallDockDeck"
    desc = ("Estimated seawall, dock and lift costs from real South Florida work in 2026, rounded, "
            "with what was actually built. One 280-foot wall priced three ways. Not a quote.")
    top = max(o[3] for o in OPTIONS)

    bars = ""
    for name, head, sub, val, shown in OPTIONS:
        pct = val / top * 100
        bars += f'''<div class="barrow">
      <div class="lab"><b>{name} &mdash; {head}</b><span>{e(sub)}</span></div>
      <div class="bartrack"><div class="barfill" style="width:{pct:.1f}%"><em>{shown}</em></div></div>
    </div>'''

    comps = ""
    for where, amt, what, scope, note in COMPARABLES:
        comps += f'''<div class="comp">
      <span class="where">{where}</span>
      <span class="amt">about ${amt:,}</span>
      <h3>{e(what)}</h3>
      <p>{scope}</p>
      <p class="note">{note}</p>
    </div>'''

    excl = "".join(f'<div><b>{e(k)}</b><span>{e(v)}</span></div>' for k, v in EXCLUSIONS)
    terms = "".join(f'<div><b>{e(k)}</b><span>{e(v)}</span></div>' for k, v in TERMS)

    body = head_(title, desc, path, body_data=' data-cluster="seawall-compliance"')
    body += f'''<nav class="crumbs"><div class="wrap">
  <a href="/">Home</a> <span>/</span> <a href="/resources/">Resources</a> <span>/</span> What it costs
</div></nav>

<div class="answer"><div class="wrap">
  <span class="eyebrow">Real quotes &middot; not ranges</span>
  <h1>What a seawall actually costs</h1>
  <p class="qualifier">Everyone else publishes a range with no scope attached, which you cannot use.
  These are rounded from real South Florida jobs in 2026, each shown with what was actually built.
  They are estimates, not quotes. Yours will differ &mdash; but you can see what moves the number.</p>
</div></div>

<section><div class="wrap">
  <div class="shead"><h2>The same wall, three ways</h2>
  <p>A 280-foot seawall in Boca Raton, priced three ways in the same year, with everything else in the scope held
  the same. The difference between the three is almost entirely how far you go on the wall itself.</p></div>

  <div class="costviz">
    <p class="cap">Quoted 2026 &middot; 280 linear feet &middot; Boca Raton</p>
    <div class="bars">{bars}</div>
    <div class="scale"><span>$0</span><span>$250,000</span><span>$500,000</span><span>$750,000</span></div>
    <p class="spread">The spread is about <b>$350,000</b> on the same 280 feet of wall, in the same year.</p>
    <p class="caveat"><b>Two things to hold in mind.</b> The heaviest option also carried access ramps that the others did not, so
    part of that gap is ramps rather than wall. And putting a new wall in front of an old one needs an exemption from
    the city &mdash; a permitting risk rather than a line item, and the reason the cheapest-looking first phase sits on
    the most expensive option.</p>
  </div>
</div></section>

<section class="tint"><div class="wrap">
  <div class="shead"><h2>What the difference buys</h2>
  <p>Because the rest of the scope is identical across the three, the gaps are close to clean.</p></div>
  <div class="rows">
    <div><b>Restore the cap &rarr; replace the cap</b><span>roughly $100,000 more &mdash; on the order of $350 per linear foot</span></div>
    <div><b>Replace the cap &rarr; new wall</b><span>roughly $250,000 more &mdash; on the order of $900 per linear foot</span></div>
    <div><b>Restore the cap &rarr; new wall</b><span>roughly $350,000 more &mdash; on the order of $1,250 per linear foot</span></div>
  </div>
  <p class="caveat" style="max-width:66ch">This is where finding a problem early pays for itself. Caught in time,
  you are choosing between the first two. Left long enough, the third is the only one left.</p>
</div></section>

<section><div class="wrap">
  <div class="shead"><h2>Two more real jobs</h2>
  <p>Shown whole and rounded, never divided into a price per foot. These were lump sums, and splitting them would be a guess.</p></div>
  <div class="cards">{comps}</div>
</div></section>

<section class="tint"><div class="wrap">
  <div class="shead"><h2>What no quote includes</h2>
  <p>These exclusions turn up again and again. This is where two quotes that look alike stop being alike.</p></div>
  <div class="rows">{excl}</div>
</div></section>

<section><div class="wrap">
  <div class="shead"><h2>Terms worth comparing</h2>
  <p>None of these are standard across the industry, so they are worth reading in whatever you are handed.</p></div>
  <div class="rows">{terms}</div>
</div></section>

<section class="tint"><div class="wrap">{slot("R3", "", "seawall-compliance")}</div></section>

<section><div class="wrap">
  <div class="shead"><h2>How to read these numbers</h2></div>
  <div class="rows">
    <div><b>These are estimates, not quotes</b><span>Rounded from real work. No average, no median, and no price for your property.</span></div>
    <div><b>Three counties only</b><span>Broward, Palm Beach and Miami-Dade. We have nothing for Monroe and will not guess.</span></div>
    <div><b>No price per foot for a whole wall</b><span>We can show roughly what moving between two approaches cost on one wall. We cannot give you a base rate, and anyone who hands you one without seeing your wall is guessing.</span></div>
    <div><b>Dated on purpose</b><span>Material prices move. Every figure here carries the year it came from.</span></div>
    <div><b>Only a site visit settles it</b><span>Condition, water depth, barge access, soil, length and what the agencies ask for all move the number. No honest price exists before a survey and an engineer look at it.</span></div>
  </div>
</div></section>
'''
    body += FOOT
    write(path, body)
    PAGES.append((path, TODAY, "0.9"))


# ------------------------------------------------------- county / region pages
def load_regions():
    p = os.path.join(DATA, "Regions.csv")
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf8") as f:
        return [r for r in csv.DictReader(f) if r.get("status") == "verified"]


def build_regions():
    regions = load_regions()
    for r in regions:
        rs, ss = r["regionSlug"], r["serviceSlug"]
        path = f"/{rs}/{ss}/"

        # Every verified city page in this county, grouped by topic. This is what
        # makes the county page a hub rather than another article.
        in_county = [x for x in LIVE
                     if CITY.get(x["citySlug"], {}).get("county") == r["region"]]
        by_topic = {}
        for x in in_county:
            by_topic.setdefault(x["topicSlug"], []).append(x)

        blocks = ""
        for tslug in [t["slug"] for t in TOPICS]:
            items = by_topic.get(tslug)
            if not items:
                continue
            t = TOPIC[tslug]
            links = "".join(
                f'<a href="/{x["citySlug"]}/{x["topicSlug"]}/">'
                f'<em>{e(CITY[x["citySlug"]]["city"])}</em>'
                f'{e(x.get("headline_answer",""))} {e(x.get("unit",""))}</a>'
                for x in sorted(items, key=lambda i: CITY[i["citySlug"]]["city"]))
            blocks += f'''<div style="margin-bottom:26px">
      <div class="shead" style="margin-bottom:12px"><h3 style="font-size:19px">{e(t["topic"])}</h3></div>
      <div class="strip">{links}</div>
    </div>'''

        cities_here = sorted({CITY[x["citySlug"]]["city"] for x in in_county})
        count_line = (f'{len(in_county)} published across {len(cities_here)} cities: '
                      + ", ".join(cities_here) + ".") if in_county else \
                     "City pages for this county are still being verified."

        body = head_(f'{r["title"]} | WallDockDeck', r["qualifier"][:158], path,
                     body_data=f' data-cluster="seawall-compliance"')
        body += f'''<nav class="crumbs"><div class="wrap">
  <a href="/">Home</a> <span>/</span> <a href="/resources/">Resources</a> <span>/</span> {e(r["region"])}
</div></nav>

<div class="answer"><div class="wrap">
  <span class="eyebrow">{e(r["region"])} County &middot; {e(r["service"])}</span>
  <h1>{e(r["question"])}</h1>
  <div class="figure"><b>{e(r["headline_answer"])}</b><span>{e(r["unit"])}</span></div>
  <p class="qualifier">{e(r["qualifier"])}</p>
  <p class="src"><b>Source:</b> {e(r["source"])} &middot; <b>Verified</b> {e(r["verified_date"])}</p>
</div></div>

<section><div class="wrap">
  <div class="shead"><h2>The detail</h2></div>
  {detail_rows(r.get("detail_rows"))}
</div></section>

<section class="tint"><div class="wrap">{slot("H1", "", "seawall-compliance")}</div></section>

<section><div class="wrap">
  <div class="shead"><h2>Your city, specifically</h2><p>{count_line}</p></div>
  {blocks if blocks else '<p class="qualifier">Nothing published for this county yet.</p>'}
</div></section>

<section class="tint"><div class="wrap">{slot("H2", "", "seawall-compliance")}</div></section>
'''
        body += FOOT
        write(path, body)
        PAGES.append((path, TODAY, "0.9"))
    return len(regions)


# ------------------------------------------------------------------ downloads
def build_downloads():
    import glob
    files = sorted(os.path.basename(f) for f in glob.glob(os.path.join(ROOT, "downloads", "*.pdf")))
    if not files:
        return 0

    def label(fn):
        if fn.startswith("seawall-height-sheet-"):
            slug = fn[len("seawall-height-sheet-"):-4]
            c = CITY.get(slug, {})
            row = next((r for r in LIVE if r["citySlug"] == slug
                        and r["topicSlug"] == "seawall-height-requirement"), {})
            return ("City height sheet", f'{c.get("city", titlecase_(slug))} seawall height',
                    f'{row.get("headline_answer","")} {row.get("unit","")}'.strip()
                    or "The elevation, the datum and the code section.")
        return {
            "seawall-warning-signs-checklist.pdf":
                ("Owner checklist", "Twelve signs a seawall is failing",
                 "What to look for, where, and what it means when you find it."),
            "waterfront-buyer-questions-checklist.pdf":
                ("Buyer checklist", "Fifteen questions before you buy waterfront",
                 "For the inspection period, while you can still act on the answer."),
            "waterfront-deck-safety-checklist.pdf":
                ("Owner checklist", "Ten checks on a waterfront deck",
                 "The parts that fail first on the water, and how to find them."),
        }.get(fn, ("Download", fn, ""))

    cards = "".join(
        f'<a class="card" href="/downloads/{fn}"><span class="k">{k}</span>'
        f'<h3>{e(t)}</h3><p>{e(d)}</p><span class="meta">Open the PDF &rarr;</span></a>'
        for fn, (k, t, d) in ((f, label(f)) for f in files))

    guides = "".join(
        f'<a class="card" href="/guides/{g}.pdf"><span class="k">Regional guide</span>'
        f'<h3>{n} waterfront guide</h3><p>Which agencies are involved, what each wants, '
        f'and the order they want it in.</p><span class="meta">Open the PDF &rarr;</span></a>'
        for g, n in (("broward", "Broward"), ("miami", "Miami-Dade"),
                     ("palm", "Palm Beach"), ("keys", "Florida Keys")))

    path = "/downloads/"
    body = head_("Downloads | WallDockDeck",
                 "Every sheet, checklist and guide we publish, free to open. City height sheets, "
                 "owner checklists and the four regional waterfront guides.", path)
    body += f'''<nav class="crumbs"><div class="wrap">
  <a href="/">Home</a> <span>/</span> <a href="/resources/">Resources</a> <span>/</span> Downloads
</div></nav>
<div class="answer"><div class="wrap">
  <span class="eyebrow">Open, no email needed</span>
  <h1>Everything we publish, in one place</h1>
  <p class="qualifier">Nothing here is gated. If it is on this page it opens, and every figure in it
  carries the code section it came from and the date we checked it.</p>
</div></div>
<section><div class="wrap">
  <div class="shead"><h2>Sheets and checklists</h2></div>
  <div class="cards">{cards}</div>
</div></section>
<section class="tint"><div class="wrap">
  <div class="shead"><h2>The four regional guides</h2></div>
  <div class="cards">{guides}</div>
</div></section>
<section><div class="wrap">{slot("H1")}</div></section>
'''
    body += FOOT
    write(path, body)
    PAGES.append((path, TODAY, "0.8"))
    return len(files) + 4


def titlecase_(slug):
    return " ".join(w.capitalize() for w in str(slug or "").split("-"))


# ---------------------------------------------------------------- sitemap etc
def build_sitemap():
    urls = "".join(
        f'  <url><loc>{SITE}{p}</loc><lastmod>{m}</lastmod><priority>{pr}</priority></url>\n'
        for p, m, pr in PAGES)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f'  <url><loc>{SITE}/</loc><lastmod>{TODAY}</lastmod><priority>1.0</priority></url>\n'
           f'{urls}</urlset>\n')
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf8").write(xml)

    robots = (f"User-agent: *\nAllow: /\nDisallow: /_build/\n\n"
              f"Sitemap: {SITE}/sitemap.xml\n")
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf8").write(robots)


def main():
    n_matrix = build_matrix()
    n_clus = build_clusters()
    build_resources_hub()
    build_agents(False)
    build_agents(True)
    build_costs()
    n_reg = build_regions()
    n_dl = build_downloads()
    build_sitemap()

    held = len(CT) - len(LIVE)
    print(f"matrix pages      {n_matrix:>4}   (of {len(CT)} rows; {held} not yet verified)")
    print(f"cluster hubs      {n_clus:>4}")
    print(f"resources hub        1")
    print(f"agent pages          2   /agents/ /luxury/")
    print(f"cost page            1   /resources/what-it-costs/")
    print(f"county pages      {n_reg:>4}   /{{county}}/{{service}}/")
    print(f"downloads page       1   {n_dl} files listed")
    print(f"sitemap entries   {len(PAGES)+1:>4}")
    print(f"\nindex.html and /guides untouched.")

    import subprocess
    subprocess.run([sys.executable, os.path.join(ROOT, "_build", "guard.py")], check=True)


if __name__ == "__main__":
    main()
