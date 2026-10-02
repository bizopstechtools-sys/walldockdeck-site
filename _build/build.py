#!/usr/bin/env python3
"""WallDockDeck static site generator.

Reads the CSVs in _build/data and writes real directories with index.html so
every page has a clean URL. Nothing in the existing repo is touched: index.html
(the live prototype) and /guides are left exactly as they are.

Run:  python3 _build/build.py
"""
import csv, html, json, os, re, shutil, sys
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


# ---------------------------------------------------------------- search result
# How a page looks in Google. Two rules behind everything below:
#
#  1. Lead with the answer, not the brand. On a rule query the figure IS the
#     hook — someone who sees "5.0 ft NAVD88" clicks to find out whether it
#     applies to them, which exception they fall under, and where it is written.
#     A title that answers outperforms one that teases, because it also looks
#     like the only result that actually knows.
#  2. No superlative we cannot source. "#1 guide" is the kind of claim Google
#     rewrites out of the result, and it contradicts our own rule that a number
#     without a source does not ship. "Every city, verified" says the same thing
#     and is true.
#
# Budgets: ~60 characters of title before Google truncates, ~155 of description.
BRAND = "WallDockDeck"
TITLE_MAX = 60
DESC_MAX = 155

# Rotating closers. Each is a reason to click the competition cannot copy.
CTA_SCORE = "How is your seawall holding up? Get a score."
CTA_SHEET = "Free one-page sheet with the code section."
CTA_LIST = "Free checklist."


def squash(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def _tidy(s):
    """Drop a dangling separator or joining word left behind by a cut."""
    stop = {"a", "an", "the", "and", "or", "no", "of", "in", "on", "to", "for",
            "is", "with", "then", "but", "by", "at", "from", "its", "it"}
    s = s.strip()
    while True:
        s2 = s.rstrip(" ,;:.—–-&/")
        parts = s2.split()
        if parts and parts[-1].lower() in stop:
            s = " ".join(parts[:-1])
            continue
        return s2


def clip(s, n):
    """Cut to n characters on a clause boundary first, a word boundary second.
    The original separators are kept, so a clipped sentence still reads as one
    sentence rather than a run of comma splices."""
    s = squash(s)
    if len(s) <= n:
        return _tidy(s)
    # keep the separators so the join is the author's punctuation, not ours
    parts = re.split(r"(\s+—\s+|\s+-\s+|,\s+|;\s+|\.\s+)", s)
    out = ""
    for i in range(0, len(parts), 2):
        nxt = out + (parts[i - 1] if i else "") + parts[i]
        if len(_tidy(nxt)) > n:
            break
        out = nxt
    return _tidy(out) if out else _tidy(s[:n].rsplit(" ", 1)[0])


def fit_title(core, brand=True):
    """Append the brand only when it fits. Google appends the site name itself
    when we do not, so those characters are better spent on the answer."""
    core = squash(core)
    if brand and len(core) + 3 + len(BRAND) <= TITLE_MAX:
        return f"{core} | {BRAND}"
    return core


def fit_desc(*parts):
    """Build a description from whole sentences, so it never ends mid-thought."""
    out = ""
    for p in parts:
        p = squash(p)
        if not p:
            continue
        if not p.endswith((".", "?", "!")):
            p += "."
        nxt = p if not out else f"{out} {p}"
        if len(nxt) > DESC_MAX:
            break
        out = nxt
    return out


def answer_line(ans, unit, n=34):
    """The figure as it should read in a title: '5.0 ft NAVD88', 'Town by town'."""
    ans, unit = squash(ans), squash(unit)
    if not ans:
        return clip(unit, n)
    if not unit:
        return clip(ans, n)
    # a bare figure needs its unit beside it; a sentence needs a separator
    joined = f"{ans} {unit}" if re.match(r"^[~$<>\d]", ans) else f"{ans} — {unit}"
    return clip(joined, n)


def year_of(s):
    m = re.match(r"(\d{4})", squash(s))
    return m.group(1) if m else str(date.today().year)


# Per-topic search framing. Keyed on topic slug; anything unlisted falls back to
# the question itself, which is already the phrase people type.
TOPIC_SEO = {
    "seawall-height-requirement": dict(
        title="Seawall Height in {city}: {ans}",
        desc=lambda c, r, ans: fit_desc(
            f"{c} requires {ans} for a new or substantially repaired seawall",
            "The code section, what triggers it, and the exceptions",
            CTA_SHEET),
    ),
    "seawall-permit": dict(
        title="Do I Need a Permit to Fix a Seawall in {city}?",
        desc=lambda c, r, ans: fit_desc(
            f"Yes — and {c} checks things in a set order",
            "What the plans must show, who signs off first, and the step that catches owners out",
            CTA_SHEET),
    ),
    "seawall-repair-cost": dict(
        title="Seawall Cost in {city}: {raw} ({year} Estimate)",
        desc=lambda c, r, ans: fit_desc(
            f"{squash(r.get('headline_answer'))} in {c}, {year_of(r.get('verified_date'))}, with what was actually in scope",
            "Estimates, not quotes — a seawall cannot be priced without a survey"),
    ),
    "flood-zone": dict(
        title="{city} Flood Zone: What It Means for Your Seawall",
        desc=lambda c, r, ans: fit_desc(
            f"The flood zone and base elevation {c} builds to, and what it changes about your wall",
            CTA_SHEET),
    ),
    "dock-permit-size": dict(
        title="How Big a Dock Can You Build in {city}?",
        desc=lambda c, r, ans: fit_desc(
            f"{c} dock size limits, setbacks, and the permits in the order they go in",
            CTA_SHEET),
    ),
    "boat-lift-rules": dict(
        title="Boat Lift Rules in {city}: {ans}",
        desc=lambda c, r, ans: fit_desc(
            f"What {c} allows on a boat lift, what needs a permit, and what the agencies check",
            CTA_SHEET),
    ),
    "deck-requirements": dict(
        title="Waterfront Deck Rules in {city}: Setbacks & Railings",
        desc=lambda c, r, ans: fit_desc(
            f"The setback, railing and surface rules {c} enforces on a waterfront deck",
            CTA_LIST),
    ),
    "licensed-contractors": dict(
        title="How to Check a Marine Contractor in {city}",
        desc=lambda c, r, ans: fit_desc(
            "The licence, the insurance and the two records to pull before you sign anything",
            f"Specific to {c}", CTA_LIST),
    ),
    "storm-prep": dict(
        title="Storm Prep for {city} Waterfront Owners",
        desc=lambda c, r, ans: fit_desc(
            f"What {c} requires before and after a storm, what to photograph, and the debris rules",
            CTA_LIST),
    ),
}

# Cluster hubs. These are the pages where the hook has to carry the click,
# because there is no single figure to lead with.
CLUSTER_SEO = {
    "failing-seawall": dict(
        title="Is Your Seawall Failing? 12 Signs to Check",
        desc="Sinkholes, leaning panels, rust bleed and water draining the wrong way. "
             "The twelve signs that mean call someone, and the ones that can wait."),
    "seawall-compliance": dict(
        title="Seawall Rules by City: Heights, Permits, Deadlines",
        desc="Every South Florida city sets its own seawall height, and most owners are "
             "quoting the wrong one. The figure, the code section, the date we checked."),
    "docks-and-lifts": dict(
        title="Dock & Boat Lift Permits in South Florida",
        desc="How big a dock you can build, what a lift needs, and the order the agencies "
             "sign off in. City by city, with the code section for each."),
    "buying-and-selling": dict(
        title="Buying Waterfront? Ask These Before You Close",
        desc="A seawall is the one thing a standard home inspection does not look at. "
             "The questions to ask inside the inspection period, and who answers them."),
    "decks": dict(
        title="Waterfront Deck Safety: A 10-Point Owner Check",
        desc="Soft boards, loose rails, and the connections that fail first on salt water. "
             "What to check yourself, and what your city requires when you rebuild."),
    "hoa-and-commercial": dict(
        title="HOA Shoreline Planning: What Boards Must Budget",
        desc="Shared seawalls, reserve studies, and the deadlines that arrive whether the "
             "board planned for them or not. What to put in front of your members."),
}

# County pages. Each county's hook is how it differs from the other three, which
# is the thing a searcher cannot get anywhere else.
REGION_TITLE = {
    # The data figure reads as a repetition next to the words "Seawall Rules"
    # on these two, so they get written rather than generated.
    "miami-dade": "Miami-Dade Seawall Rules: Your City Sets the Height",
    "palm-beach": "Palm Beach Seawall Rules: Every Town Sets Its Own",
}

REGION_SEO = {
    "broward": "Broward is the one county with a single standard behind every city — and "
               "several cities went above it. The figure, the code, and who differs.",
    "miami-dade": "The county sets no seawall height at all. Your city does, and the cities "
                  "differ sharply. Which figure applies to your address, and where it is written.",
    "palm-beach": "No county standard exists — every town sets its own elevation, in its own "
                  "document. The towns we have verified, with the figure and the code section.",
}

MARK = ('<svg viewBox="0 0 34 34" width="28" height="28" aria-hidden="true"><rect width="34" height="34" rx="7" fill="#123549"/>'
        '<rect x="7" y="8" width="5" height="18" rx="1" fill="#7FC6CF"/>'
        '<rect x="14.5" y="14" width="12.5" height="3.5" rx="1" fill="#fff"/>'
        '<rect x="14.5" y="20" width="12.5" height="3.5" rx="1" fill="#E0701A"/>'
        '<path d="M5 28.5c3-1.6 6-1.6 9 0s6 1.6 9 0 6-1.6 7 0" stroke="#7FC6CF" stroke-width="1.6" fill="none"/></svg>')

FONTS = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Archivo:wdth,wght@75..100,400..800&family=Source+Sans+3:wght@400;600;700'
         '&family=IBM+Plex+Mono:wght@400;500&family=Cormorant+Garamond:wght@400;600&display=swap">')


# -------------------------------------------------------------- structured data
# Only the types that still earn anything. FAQ rich results were deprecated in
# May 2026 and HowTo before that, so neither is emitted here however many SEO
# checklists still ask for them.
ORG_ID = SITE + "/#org"
# The byline. Every rule page states who verified it, because a figure without a
# verifier is just a number on a website.
AUTHOR_ID = SITE + "/#author"
AUTHOR_NAME = "JB Marine"
AUTHOR_SCHEMA = {
    "@type": "Organization",
    "@id": AUTHOR_ID,
    "name": AUTHOR_NAME,
    "url": SITE + "/how-we-verify/",
    "parentOrganization": {"@id": ORG_ID},
    "description": ("Researches and verifies South Florida waterfront building rules for "
                    "WallDockDeck. Every figure is taken from the primary code and carries "
                    "its section and the date it was checked."),
}

ORG_SCHEMA = {
    "@type": "Organization",
    "@id": ORG_ID,
    "name": "Wall Dock Deck",
    "alternateName": "WallDockDeck",
    "url": SITE + "/",
    "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo.png",
             "width": 512, "height": 512},
    "image": SITE + "/assets/logo.png",
    "email": "hello@walldockdeck.com",
    "description": ("Verified seawall, dock and waterfront deck requirements for South "
                    "Florida property owners, published with the code section and the "
                    "date each rule was checked."),
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "16300 SW 137th Avenue, Unit 128",
        "addressLocality": "Miami",
        "addressRegion": "FL",
        "postalCode": "33177",
        "addressCountry": "US",
    },
    "areaServed": [{"@type": "AdministrativeArea", "name": n} for n in
                   ("Miami-Dade County, Florida", "Broward County, Florida",
                    "Palm Beach County, Florida", "Monroe County, Florida")],
}


def crumbs(items):
    """One definition drives both the visible breadcrumb and its markup, so the
    two can never disagree. items: [(label, url_or_None)], last one current."""
    links = [f'<a href="{u}">{e(n)}</a>' if u else e(n) for n, u in items]
    visible = ('<nav class="crumbs"><div class="wrap">\n  '
               + ' <span>/</span>\n  '.join(links) + '\n</div></nav>\n')
    schema = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            dict({"@type": "ListItem", "position": i + 1, "name": n},
                 **({"item": SITE + u} if u else {}))
            for i, (n, u) in enumerate(items)
        ],
    }
    return visible, schema


def article_schema(path, title, desc, verified="", source=""):
    """City and county rule pages are articles with a verification date. The
    date is the one in the CSV, never today's, or the freshness is a lie."""
    a = {
        "@type": "Article",
        "headline": clip(title, 110),
        "description": desc,
        "mainEntityOfPage": SITE + path,
        "publisher": {"@id": ORG_ID},
        "author": {"@id": AUTHOR_ID},
        "isAccessibleForFree": True,
    }
    if verified:
        iso = squash(verified)
        iso = iso + "-01" if re.fullmatch(r"\d{4}-\d{2}", iso) else iso
        a["dateModified"] = iso
        a["datePublished"] = iso
    if source:
        a["citation"] = squash(source)
    return a


def jsonld(path, extra=None):
    graph = [ORG_SCHEMA, AUTHOR_SCHEMA,
             {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/",
              "name": "WallDockDeck", "publisher": {"@id": ORG_ID}}]
    graph += [g for g in (extra or []) if g]
    doc = {"@context": "https://schema.org", "@graph": graph}
    return ('<script type="application/ld+json">'
            + json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
            + "</script>")


def head_(title, desc, path, body_class="", body_data="", schema=None):
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
<meta property="og:image" content="{SITE}/assets/logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" href="/assets/logo.svg" type="image/svg+xml">
{FONTS}
<link rel="stylesheet" href="/assets/wdd.css">
{jsonld(path, schema)}
</head>
<body{(' class="'+body_class+'"') if body_class else ''}{body_data}>
<header class="site"><div class="wrap">
  <a class="brand" href="/">{MARK}<b>Wall<i>Dock</i>Deck</b></a>
  <nav>
    <a href="/resources/">Resources</a>
    <a href="/downloads/">Downloads</a>
    <a href="/resources/what-it-costs/">What it costs</a>
    <a href="/agents/">For Agents</a>
    <a href="/book/">Book an inspection</a>
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
    <h4>Answers</h4>
    <a href="/#/start">Get a Shore Score</a>
    <a href="/book/">Book an inspection</a>
    <a href="/resources/what-it-costs/">What it costs</a>
    <a href="/downloads/">All downloads</a>
    <a href="/broward/seawalls/">Broward seawall rules</a>
  </div>
  <div>
    <h4>Coverage</h4>
    <a href="/coverage/">Where we work</a>
    <a href="/miami-dade/seawalls/">Miami-Dade</a>
    <a href="/palm-beach/seawalls/">Palm Beach</a>
    <a href="/agents/">For agents</a>
  </div>
  <div>
    <h4>Company</h4>
    <a href="/about/">About</a>
    <a href="/how-we-verify/">How we verify</a>
    <a href="/legal/">Legal</a>
    <a href="/privacy/">Privacy</a>
    <a href="/sms-terms/">SMS terms</a>
    <a href="/legal/your-privacy-choices/">Do Not Sell or Share My Info</a>
  </div>
  <p class="legal"><strong style="color:#B9CCD6">WallDockDeck</strong> &middot; Seawalls, docks &amp; waterfront decks &middot; Florida Keys to Palm Beach<br>
  Shore Scores are screenings based on public data and owner answers, not engineering inspections. Inspections and construction are performed by licensed contractors.
  Local rules are published with their code section and the date we verified them; confirm with your building department before you rely on one. Updated {TODAY}.</p>
</div></footer>
<script src="/assets/wdd.js" defer></script>
</body></html>
"""


# The consent wording lives here once. The visible label, the data-consent
# attribute that gets recorded with the lead, the SMS Terms page and the carrier
# registration all read from this one string, so they cannot drift apart. If you
# change it here, change it in the A2P registration too — a form that differs
# from what was filed is the most common reason a campaign is pulled.
#
# It names ONE company. Carriers routinely reject consent language that covers a
# second business, because the recipient cannot meaningfully consent to messages
# from a party who is not named. The contractor handoff is disclosed separately,
# below, which is also what CPRA wants at the point of collection.
CONSENT_TEXT = (
    "I agree that Wall Dock Deck may contact me by phone, text and email about my "
    "property at the number above, including by automated means. Consent is not a "
    "condition of purchase. Message and data rates may apply. Message frequency "
    "varies. Reply STOP to opt out, HELP for help. See our Privacy Policy and SMS Terms."
)

# Shown next to the consent box wherever we collect contact details. Not a tick —
# a disclosure, which is what the point-of-collection notice requirement asks for.
SHARING_NOTE = (
    "If you ask to be connected, we share your details with a licensed contractor "
    "for your area, who is an independent business and may contact you directly."
)


# What kind of lead this is, so the CRM can route it without parsing the offer.
# A booking arriving tagged "resource_request" lands in the wrong sequence and
# nobody calls the person back.
ACTION_FOR = {
    "book_inspect": "book_inspection",
    "shore_score":  "score_request",
    "agent_tools":  "agent_request",
    "bid_compare":  "quote_review",
}


# Which asset each resource hub offers. Without this every hub showed the same
# warning-signs checklist, so a campaign email about buying waterfront landed on
# a page offering a seawall checklist. Where a cluster has no asset of its own
# yet, it falls back to the county guide, which is always relevant.
CLUSTER_OFFER = {
    "seawall-compliance": "height_sheet",
    "failing-seawall":    "warning_list",
    "buying-and-selling": "fifteen_q",
    "decks":              "deck_check",
    "docks-and-lifts":    "county_guide",
    "hoa-and-commercial": "county_guide",
}


def county_slug(name):
    """'Palm Beach' -> 'palm-beach'. The CRM routes on the slug; the display name
    is carried alongside it so a human reading a lead card sees something legible."""
    return re.sub(r"[^a-z0-9]+", "-", squash(name).lower()).strip("-")


def consent_block():
    """The consent checkbox plus the sharing disclosure. data-consent carries the
    exact wording shown, so the lead record stores what the person actually read
    rather than a yes/no flag. That is the thing that settles a TCPA dispute.

    The checkbox is deliberately NOT required. The earlier build spec said it was,
    which contradicts the wording printed inside it and published on /sms-terms/ —
    "Consent is not a condition of purchase." A form that will not submit without
    consent makes that sentence false, and a reviewer comparing the two is exactly
    how a campaign gets rejected. Unticked, the request still goes through and we
    reply by email instead."""
    link = (CONSENT_TEXT
            .replace("Privacy Policy", '<a href="/privacy/">Privacy Policy</a>')
            .replace("SMS Terms", '<a href="/sms-terms/">SMS Terms</a>'))
    return (
        f'<label class="consent" data-consent="{e(CONSENT_TEXT)}">'
        f'<input type="checkbox" name="consent" value="yes">'
        f'<span>{link}</span></label>'
        f'<p class="sharing">{e(SHARING_NOTE)} '
        f'<a href="/legal/your-privacy-choices/">You can opt out.</a></p>')


def slot(slot_id, city="", cluster="", county="", offer=""):
    """Render one capture slot. The offer comes from Slots -> Offers, so the
    copy and the placement are separate variables you can move one at a time."""
    s = SLOTS.get(slot_id)
    if not s:
        return ""
    # A caller may override which offer this slot shows. Cluster hubs do, so a
    # visitor who arrived from a "buying waterfront" email is offered the buyer
    # checklist rather than whatever the slot shows by default.
    o = OFFERS.get(offer or s["currentOffer"])
    if not o or o.get("live", "yes") == "no":
        return ""
    style = (" " + s["style"]) if s.get("style") else ""

    # County is derived from the city rather than passed in, so the two can never
    # disagree. On a county page there is no city, so it is passed explicitly.
    # Without this the CRM cannot pick a county guide, and cannot fall back when
    # a city has no height sheet — which is most of them.
    if not county and city:
        county = CITY.get(city, {}).get("county", "")

    # An embedded Tomonagi form lives in an iframe, so page JavaScript cannot
    # reach into it. The six fields therefore travel in the query string — the
    # only channel an iframe will accept them on. Confirm Tomonagi reads them.
    if s.get("render") == "embed" and s.get("embed_url"):
        from urllib.parse import urlencode, quote
        # Tomonagi reads one parameter today, ?src=, and keeps it in the form's
        # own analytics rather than on the lead. So the discriminator is packed
        # into that single tag — slot.offer.city — which at least tells you which
        # placement is producing submits. The named parameters below are sent
        # alongside it and are ignored until hidden fields ship; nothing breaks
        # when they start being read.
        src = ".".join(x for x in (slot_id, o["offer_id"], city or county_slug(county)) if x)
        qs = urlencode({"src": src, "slot_id": slot_id, "offer_id": o["offer_id"],
                        "cluster": cluster, "city": city,
                        "county": county, "county_slug": county_slug(county)},
                       quote_via=quote)
        sep = "&" if "?" in s["embed_url"] else "?"
        h = s.get("embed_height") or "700"
        return (f'<div class="slot{style}" data-slot="{e(slot_id)}" data-offer="{e(o["offer_id"])}">'
                f'<h3>{e(o["headline"])}</h3><p>{e(o["body"])}</p>'
                f'<iframe src="{e(s["embed_url"])}{sep}{qs}" title="{e(o["headline"])}" '
                f'loading="lazy" style="width:100%;border:0;height:{e(h)}px;margin-top:14px"></iframe>'
                + (f'<p class="fine">{e(o.get("fine",""))}</p>' if o.get("fine") else "")
                + '</div>')

    fields = [f for f in (o.get("fields") or "").split("|") if f]

    inputs = []
    if "first_name" in fields or "name" in fields:
        inputs.append('<input name="full_name" type="text" placeholder="First name" autocomplete="given-name" required>')
    if "email" in fields:
        inputs.append('<input name="email" type="email" placeholder="Email" autocomplete="email" required>')
    if "phone" in fields:
        inputs.append('<input name="phone" type="tel" placeholder="Phone" autocomplete="tel" required>')
    if "address" in fields:
        # On a form that asks for a phone number we are arranging a site visit,
        # and a visit without an address is useless. Elsewhere it stays optional.
        req = " required" if "phone" in fields else ""
        inputs.append('<input name="property_address" type="text" placeholder="Property address" '
                      f'autocomplete="street-address"{req}>')
    if "brokerage" in fields:
        inputs.append('<input name="brokerage" type="text" placeholder="Brokerage">')
    if "office" in fields:
        inputs.append('<input name="office" type="text" placeholder="Office or team">')
    if "window" in fields:
        inputs.append(
            '<select name="preferred_window" aria-label="Preferred window">'
            '<option value="">Preferred window (optional)</option>'
            '<option value="morning">Morning, 8am&ndash;12pm</option>'
            '<option value="afternoon">Afternoon, 12pm&ndash;4pm</option>'
            '<option value="first_available">First available</option>'
            '</select>')
    if "notes" in fields:
        inputs.append(
            '<textarea name="notes" rows="3" '
            'placeholder="Anything we should know? A crack, a sinkhole, a deadline."></textarea>')
    if not inputs:
        inputs.append('<input name="email" type="email" placeholder="Email" autocomplete="email" required>')

    # A form that asks for a phone number must capture consent at the point of
    # collection, visibly, unticked. Carriers check this on registration and it is
    # the thing that gets a campaign rejected.
    consent = consent_block() if "phone" in fields else ""

    fine = f'<p class="fine">{e(o.get("fine",""))}</p>' if o.get("fine") else ""
    return f"""<div class="slot{style}" data-slot="{e(slot_id)}" data-offer="{e(o['offer_id'])}"
     data-city="{e(city)}" data-county="{e(county)}" data-county-slug="{e(county_slug(county))}"
     data-cluster="{e(cluster)}" data-action="{e(ACTION_FOR.get(o['offer_id'], 'resource_request'))}">
  <h3>{e(o['headline'])}</h3>
  <p>{e(o['body'])}</p>
  <form novalidate>
    {''.join(inputs)}
    {consent}
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

        # How it reads in Google. Answer first, city named, brand only if it fits.
        seo = TOPIC_SEO.get(ts)
        ans = answer_line(r.get("headline_answer"), r.get("unit"))
        if seo:
            title = fit_title(seo["title"].format(
                city=city["city"], ans=ans,
                raw=squash(r.get("headline_answer")),
                year=year_of(r.get("verified_date"))))
            desc = seo["desc"](city["city"], r, ans)
        else:
            title = fit_title(f"{q} {ans}".strip() if ans else q)
            desc = fit_desc(clip(r.get("qualifier") or q, 110), CTA_SCORE)

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
        county_url = region_for.get(city["county"])
        trail = [("Home", "/"), ("Resources", "/resources/"),
                 (cl.get("cluster", "Resources"), f"/resources/{cluster}/")]
        if county_url:
            trail.append((f'{city["county"]} County', county_url))
        trail.append((city["city"], None))
        crumb_html, crumb_schema = crumbs(trail)

        body = head_(title, desc, path,
                     body_data=f' data-city="{e(cs)}" data-cluster="{e(cluster)}"',
                     schema=[crumb_schema,
                             article_schema(path, title, desc,
                                            r.get("verified_date"), r.get("source"))])
        body += crumb_html + f"""

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
        s = CLUSTER_SEO.get(slug)
        if s:
            title, desc = fit_title(s["title"]), fit_desc(s["desc"])
        else:
            title = fit_title(f'{c["cluster"]}: The {c["asset"]}')
            desc = fit_desc(f'{c["who"]}', f'The {c["asset"]}, plus the rule your own city enforces', CTA_SCORE)
        crumb_html, crumb_schema = crumbs(
            [("Home", "/"), ("Resources", "/resources/"), (c["cluster"], None)])
        body = head_(title, desc, path, body_data=f' data-cluster="{e(slug)}"',
                     schema=[crumb_schema])
        body += crumb_html + f"""
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
<section class="tint"><div class="wrap">{slot('H2', '', slug, offer=CLUSTER_OFFER.get(slug, ''))}</div></section>
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
    body = head_(fit_title("South Florida Seawall, Dock & Deck Rules by City"),
                fit_desc("Seawall, dock and deck rules from the Keys to Palm Beach",
                         "Each one with the figure, the code section, and the date we checked it",
                         CTA_SCORE),
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
    title = fit_title("Luxury Waterfront: Check the Seawall Before You List" if luxury
                       else "Waterfront Listings: Check the Seawall Before You List")
    desc = fit_desc(
        "On an eight-figure waterfront listing the seawall is the one asset no home inspector "
        "opens, and the one a buyer's engineer will"
        if luxury else
        "The seawall is what kills a waterfront deal in the inspection period, and no home "
        "inspector looks at it",
        "Know the condition, the city rule and the repair range before you list"
        if luxury else
        "See the condition, the city rule and the repair range on any address")

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
# No published figures. Every number this page used to carry came from real
# contractor proposals on identifiable properties: totals, per-linear-foot
# rates, scope detail, exclusions and commercial terms. That is the client's
# business and the contractor's pricing structure, and neither belongs on a
# public page. What survives is the part that actually helps a reader -- the
# three structural approaches, what moves the number, and how to read a bid.

APPROACHES = [
    ("Lightest", "Repair the panels, restore the cap",
     "Crack routing, partial-depth concrete repair and protective coating. Only available while "
     "the panels are still structurally sound, which is what a survey establishes."),
    ("Middle", "Repair the panels, replace the cap",
     "The same panel repair, but the cap is demolished and rebuilt in full. Chosen when the cap "
     "has spalled, the steel is exposed, or the elevation has to change."),
    ("Heaviest", "Build a new wall in front of the old one",
     "New panels and new batter piles throughout. In most cities this needs an exemption, so it "
     "carries a permitting risk on top of the construction cost."),
]

DRIVERS = [
    ("Condition of the existing wall",
     "The single biggest fork in the price. Repairable or not repairable is the difference between "
     "the lightest and the heaviest approach, and only a survey answers it."),
    ("Length of shoreline",
     "Priced as a whole job, not a rate. Mobilising for 40 feet and for 400 feet is not "
     "proportional, which is why a price per foot tells you very little."),
    ("Access",
     "Whether a barge can reach the shoreline, or the work has to come through the property. This "
     "lands on the number before a single panel is set."),
    ("Elevation target",
     "Building to 4 ft NAVD88 now versus straight to 5 ft changes steel and concrete today, and "
     "decides whether the wall has to come up again before 2050."),
    ("Water depth and soil",
     "Pile length follows from what is under the wall. A geotechnical recommendation can move the "
     "structural design substantially."),
    ("What the agencies require",
     "Benthic or bathymetric surveys, coral avoidance or relocation, sea grass mitigation. "
     "Triggered by your location, not by anyone's choice."),
    ("Demolition",
     "Removing an old dock and its timber piles is its own scope. Piles pulled rather than cut "
     "cost more, and are usually the right answer."),
    ("Selections",
     "Decking product, railing, lift capacity. Get the product name and the per-unit rate written "
     "into the bid, not just a category."),
]

EXCLUSIONS = [
    ("Permit fees and bonds",
     "Generally paid by the owner directly to the agencies, and generally non-refundable. Some "
     "cities also require a refundable bond on top of the contract. Ask the city, because it will "
     "not appear in the contractor's number."),
    ("Surveys",
     "As-built, bathymetric, geotechnical and tree surveys, pile-length recommendations, and coral "
     "avoidance or relocation plans. Commonly supplied and paid for by the owner."),
    ("Mitigation",
     "Moving or replacing sea grass, coral or riprap is commonly the owner's cost, not the "
     "contractor's."),
    ("Electrical and plumbing",
     "Dock power, water and lighting are frequently excluded from the marine scope entirely."),
    ("Landscaping and restoration",
     "Trees, pavers and turf are often listed as 'by others'. Ask in writing who puts the yard "
     "back, and to what standard."),
    ("Interruption costs",
     "Overtime, idle time and travel, if the site is not available full time. Worth asking how "
     "these are charged before they are charged."),
]

TERMS_TO_ASK = [
    ("Warranty", "How long, and against what - workmanship, materials, or both?"),
    ("Late payment", "What rate applies, and after how many days?"),
    ("How long the price holds", "Marine bids often expire quickly. Ask for the date in writing."),
    ("Default and liquidated damages", "What percentage, and what exactly triggers it?"),
    ("Salvage", "Who keeps the removed material? It has value."),
    ("Payment schedule", "What is due at signing, at mobilisation, and at completion?"),
]


def build_costs():
    path = "/resources/what-it-costs/"
    title = fit_title("Seawall Cost: What Actually Moves the Number")
    desc = fit_desc(
        "The three structural approaches, the eight things that move the price, and what no "
        "marine quote includes",
        "Why no honest figure exists before a survey")

    appr = "".join(
        f'<div><b>{e(n)} &mdash; {e(h)}</b><span>{e(s)}</span></div>'
        for n, h, s in APPROACHES)
    drv = "".join(f'<div><b>{e(k)}</b><span>{e(v)}</span></div>' for k, v in DRIVERS)
    excl = "".join(f'<div><b>{e(k)}</b><span>{e(v)}</span></div>' for k, v in EXCLUSIONS)
    terms = "".join(f'<div><b>{e(k)}</b><span>{e(v)}</span></div>' for k, v in TERMS_TO_ASK)

    crumb_html, crumb_schema = crumbs(
        [("Home", "/"), ("Resources", "/resources/"), ("What it costs", None)])
    body = head_(title, desc, path, body_data=' data-cluster="seawall-compliance"',
                 schema=[crumb_schema])
    body += crumb_html + f'''

<div class="answer"><div class="wrap">
  <span class="eyebrow">Cost drivers &middot; no invented ranges</span>
  <h1>What a seawall actually costs</h1>
  <p class="qualifier">Every site that publishes a price per foot is guessing, and you cannot use a
  guess. We are not going to publish one either. What we can do is tell you the three ways the same
  wall can be addressed, the eight things that actually move the number, and what is missing from
  almost every quote you will be handed &mdash; which is where two bids that look alike stop being
  alike.</p>
</div></div>

<section><div class="wrap">
  <div class="shead"><h2>The same wall, three ways</h2>
  <p>Most of the spread between two quotes on one shoreline is not margin. It is that they are
  quoting different structural approaches. These are the three, from lightest to heaviest.</p></div>
  <div class="rows">{appr}</div>
  <p class="caveat" style="max-width:66ch"><b>This is where catching a problem early pays for
  itself.</b> Found in time, you are choosing between the first two. Left long enough, the third is
  the only one left &mdash; and it is the one that needs a city exemption.</p>
</div></section>

<section class="tint"><div class="wrap">
  <div class="shead"><h2>What moves the number</h2>
  <p>You can establish most of these before anyone quotes. Doing so is how you tell a careful bid
  from an optimistic one.</p></div>
  <div class="rows">{drv}</div>
</div></section>

<section><div class="wrap">
  <div class="shead"><h2>What no quote includes</h2>
  <p>These exclusions turn up again and again in marine construction. A bid that is silent on them
  is not cheaper, it is less complete.</p></div>
  <div class="rows">{excl}</div>
</div></section>

<section class="tint"><div class="wrap">
  <div class="shead"><h2>Terms worth asking about</h2>
  <p>None of these are standard across the trade, so they are worth reading in whatever you are
  handed &mdash; and worth asking about before you sign.</p></div>
  <div class="rows">{terms}</div>
</div></section>

<section><div class="wrap">{slot("R3", "", "seawall-compliance")}</div></section>

<section class="tint"><div class="wrap">
  <div class="shead"><h2>Why we do not publish a figure</h2></div>
  <div class="rows">
    <div><b>No price per foot exists</b><span>Length, condition, access, depth and soil all move it independently. Anyone who hands you a rate without seeing your wall is guessing, and the guess is usually low.</span></div>
    <div><b>We do not publish other people's bids</b><span>Figures from real proposals belong to the owner who commissioned them and the contractor who priced them. We will not republish either.</span></div>
    <div><b>Only a site visit settles it</b><span>Condition, water depth, barge access, soil, length and what the agencies ask for all move the number. No honest price exists before a survey and an engineer have looked at it.</span></div>
    <div><b>What we will do</b><span>Score your shoreline, tell you which of the three approaches your answers point to, and connect you with a licensed marine contractor covering your area who can price it properly.</span></div>
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

        county_ans = answer_line(r.get("headline_answer"), r.get("unit"), 26)
        r_title = fit_title(REGION_TITLE.get(rs)
                            or f'{r["region"]} County Seawall Rules: {county_ans}')
        r_desc = fit_desc(REGION_SEO.get(rs)
                          or fit_desc(clip(r["qualifier"], 108), CTA_SCORE))
        crumb_html, crumb_schema = crumbs(
            [("Home", "/"), ("Resources", "/resources/"), (r["region"], None)])
        body = head_(
            r_title, r_desc, path, body_data=' data-cluster="seawall-compliance"',
            schema=[crumb_schema,
                    article_schema(path, r_title, r_desc,
                                   r.get("verified_date"), r.get("source"))])
        body += crumb_html + f'''

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

<section class="tint"><div class="wrap">{slot("H1", "", "seawall-compliance", r["region"])}</div></section>

<section><div class="wrap">
  <div class="shead"><h2>Your city, specifically</h2><p>{count_line}</p></div>
  {blocks if blocks else '<p class="qualifier">Nothing published for this county yet.</p>'}
</div></section>

<section class="tint"><div class="wrap">{slot("H2", "", "seawall-compliance", r["region"])}</div></section>
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
        if fn.startswith("height-sheet-"):
            slug = fn[len("height-sheet-"):-4]
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
            "waterfront-buyer-checklist.pdf":
                ("Buyer checklist", "Fifteen questions before you buy waterfront",
                 "For the inspection period, while you can still act on the answer."),
            "deck-safety-checklist.pdf":
                ("Owner checklist", "Ten checks on a waterfront deck",
                 "The parts that fail first on the water, and how to find them."),
            "waterfront-listing-sheet.pdf":
                ("For agents", "The waterfront listing sheet",
                 "What to check before you list, and the verified city minimums."),
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
    crumb_html, crumb_schema = crumbs(
        [("Home", "/"), ("Resources", "/resources/"), ("Downloads", None)])
    body = head_(fit_title("Free Seawall Height Sheets & Owner Checklists (PDF)"),
                 fit_desc("Every sheet, checklist and guide we publish, free to open",
                          "City height sheets, owner checklists, and the four regional guides"),
                 path, schema=[crumb_schema])
    body += crumb_html + f'''
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


# ------------------------------------------------------------- coverage, legal
def build_book():
    """The booking page. This is the only form on the site that collects a phone
    number, which makes it the only page where the consent checkbox renders — and
    therefore the page a carrier reviewer needs to see for A2P registration."""
    path = "/book/"
    crumb_html, crumb_schema = crumbs([("Home", "/"), ("Book an inspection", None)])
    body = head_(
        fit_title("Book a Seawall Inspection: South Florida"),
        fit_desc("A licensed marine contractor covering your area comes to the property",
                 "No charge for the visit and no obligation after it",
                 "Four counties, Keys to Palm Beach"),
        path, body_data=' data-cluster="seawall-compliance"', schema=[crumb_schema])
    body += crumb_html + f'''
<div class="answer"><div class="wrap">
  <span class="eyebrow">Book an inspection</span>
  <h1>Have someone look at it</h1>
  <p class="qualifier">A licensed marine contractor covering your area comes to the property,
  looks at the wall, the cap, the dock and the ground behind it, and tells you what they see.
  No charge for the visit, and no obligation after it.</p>
</div></div>

<section><div class="wrap">
  <div class="shead"><h2>What happens</h2>
  <p>Four steps, and you can stop at any of them.</p></div>
  <div class="cards">
    <div class="card"><span class="k">Step one</span><h3>You tell us the address</h3>
      <p>We check which contractor covers it and what your city requires there.</p></div>
    <div class="card"><span class="k">Step two</span><h3>They call you</h3>
      <p>Usually within one business day, to agree a time. That is a target, not a promise.</p></div>
    <div class="card"><span class="k">Step three</span><h3>They walk the wall</h3>
      <p>At the property, at low tide where they can, because low tide is when a wall
      tells the truth.</p></div>
    <div class="card"><span class="k">Step four</span><h3>You decide</h3>
      <p>You get what they found. Whether you do anything about it is up to you.</p></div>
  </div>
</div></section>

<section class="tint"><div class="wrap">{slot("R1", "", "seawall-compliance")}</div></section>

<section><div class="wrap">
  <div class="shead"><h2>Worth being straight about</h2></div>
  <div class="cards">
    <div class="card"><span class="k">Who comes</span><h3>Not us</h3>
      <p>We publish the rules and make the introduction. The inspection is done by an
      independent licensed contractor. They are not our employee or our agent, and we do
      not supervise their work. <a href="/legal/terms/">The terms</a> say exactly that.</p></div>
    <div class="card"><span class="k">Who pays</span><h3>Not you</h3>
      <p>The visit is free to you. Contractors pay us for the introduction. You should know
      that when you weigh what we tell you.</p></div>
    <div class="card"><span class="k">Your details</span><h3>Go to one contractor</h3>
      <p>The one covering your area &mdash; not sold to a panel to bid on. You can
      <a href="/legal/your-privacy-choices/">opt out</a> at any time.</p></div>
    <div class="card"><span class="k">If it is urgent</span><h3>Do not wait for us</h3>
      <p>A wall that has moved, a sinkhole, or water where it should not be is not a form.
      Call a licensed marine contractor, and call your building department if anything
      looks unsafe.</p></div>
  </div>
</div></section>

<section class="tint"><div class="wrap">
  <div class="shead"><h2>Before they arrive</h2>
  <p>None of this is required. It just makes the visit worth more.</p></div>
  <div class="strip">
    <a href="/downloads/seawall-warning-signs-checklist.pdf"><em>Checklist</em>Walk the wall first &mdash; twelve signs</a>
    <a href="/resources/what-it-costs/"><em>Costs</em>What this work runs in this market</a>
    <a href="/coverage/"><em>Coverage</em>Your city&rsquo;s rule, with the code section</a>
  </div>
</div></section>
'''
    body += FOOT
    write(path, body)
    PAGES.append((path, TODAY, "0.9"))
    return 1


def build_coverage():
    regs = load_regions()
    byc = {}
    for r in LIVE:
        c = CITY.get(r["citySlug"])
        if c:
            byc.setdefault(c["county"], set()).add(c["city"])
    blocks = ""
    for r in regs:
        cities = sorted(byc.get(r["region"], []))
        # link each city to a topic it actually has, not an assumed one
        chips = ""
        for c in cities:
            row = next((x for x in LIVE if CITY.get(x["citySlug"], {}).get("city") == c), None)
            if not row:
                continue
            chips += (f'<a href="/{row["citySlug"]}/{row["topicSlug"]}/">'
                      f'<em>{e(TOPIC[row["topicSlug"]]["topic"])}</em>{e(c)}</a>')
        blocks += f'''<div style="margin-bottom:28px">
      <div class="shead" style="margin-bottom:10px"><h3 style="font-size:20px">{e(r["region"])} County</h3>
      <p>{e(r["qualifier"][:200])}</p></div>
      <div class="strip"><a href="/{r["regionSlug"]}/{r["serviceSlug"]}/"><em>County rule</em>Seawall requirements across {e(r["region"])}</a>{chips}</div>
    </div>'''

    path = "/coverage/"
    # Names the counties that actually have published pages. A title promising
    # the Keys would land on a page with no Keys city on it.
    counties = [r["region"] for r in load_regions()]
    cov_html, cov_schema = crumbs([("Home", "/"), ("Where we work", None)])
    body = head_(fit_title(clip("Seawall Rules by City: " + ", ".join(counties), TITLE_MAX)),
                 fit_desc("Seawalls, docks and waterfront decks, city by city",
                          "Find yours and see the figure, the code section and the date we checked",
                          CTA_SCORE),
                 path, schema=[cov_schema])
    body += cov_html + f'''
<div class="answer"><div class="wrap">
  <span class="eyebrow">Florida Keys to Palm Beach</span>
  <h1>Where we work</h1>
  <p class="qualifier">Four counties along the South Florida coast. We publish a city&rsquo;s rule once we
  have the code section and the date we checked it &mdash; so this list grows, and everything on it is sourced.</p>
</div></div>
<section><div class="wrap">{blocks}</div></section>
<section class="tint"><div class="wrap">{slot("H2")}</div></section>
'''
    body += FOOT
    write(path, body)
    PAGES.append((path, TODAY, "0.6"))


# ------------------------------------------------------------------------ legal
# Every legal document lives as a markdown file in _build/legal/. Each one opens
# with a small header block, then --- , then the body. Keeping them as files
# rather than Python strings means they can be read, diffed and edited by a
# lawyer without touching the generator.
#
# /privacy/ and /sms-terms/ keep their own top-level URLs because those exact
# URLs are filed with the mobile carriers and printed on the consent checkbox.
# Moving them would break the A2P registration. Everything else lives under
# /legal/.
LEGAL_DIR = os.path.join(ROOT, "_build", "legal")

LEGAL_GROUPS = [
    "Core agreements",
    "Messaging",
    "Data, privacy and security",
    "Using the site",
    "Working with us",
]


def read_legal_files():
    """Parse _build/legal/*.md into dicts. Header keys are key: value lines."""
    docs = []
    if not os.path.isdir(LEGAL_DIR):
        return docs
    for fn in sorted(os.listdir(LEGAL_DIR)):
        if not fn.endswith(".md"):
            continue
        raw = open(os.path.join(LEGAL_DIR, fn), encoding="utf8").read()
        if "\n---\n" not in raw:
            sys.exit(f"legal/{fn}: missing the --- separating header from body")
        head, body = raw.split("\n---\n", 1)
        d = {"file": fn, "body": body.strip()}
        for line in head.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                d[k.strip()] = v.strip()
        for req in ("title", "path", "summary", "group", "updated"):
            if not d.get(req):
                sys.exit(f"legal/{fn}: header is missing {req}")
        if d["group"] not in LEGAL_GROUPS:
            sys.exit(f"legal/{fn}: group {d['group']!r} is not one of {LEGAL_GROUPS}")
        d["order"] = int(d.get("order", "99"))
        docs.append(d)
    return docs


def md_to_html(text):
    """Render the document body. Falls back to escaped <pre> rather than
    publishing raw markdown if the library is unavailable."""
    try:
        import markdown
    except ImportError:
        return "<pre>" + e(text) + "</pre>"
    return markdown.markdown(
        text, extensions=["tables", "sane_lists", "attr_list"], output_format="html5")


def build_legal():
    docs = read_legal_files()
    if not docs:
        return 0

    for d in docs:
        path, h1 = d["path"], d["title"]
        inner = f'<section><div class="wrap"><div class="legalbody">{md_to_html(d["body"])}</div></div></section>'
        crumb_items = ([("Home", "/"), ("Legal", "/legal/"), (h1, None)]
                       if path.startswith("/legal/") else [("Home", "/"), (h1, None)])
        crumb_html, crumb_schema = crumbs(crumb_items)
        body = head_(fit_title(h1), fit_desc(d["summary"]),
                     path, schema=[crumb_schema])
        body += crumb_html + f'''
<div class="answer"><div class="wrap">
  <span class="eyebrow">{e(d.get("kicker", "Legal"))}</span>
  <h1>{e(h1)}</h1>
  <p class="qualifier">{e(d["summary"])}</p>
  <p class="src"><b>Last updated</b> {e(d["updated"])} &middot; <b>Version</b> {e(d["updated"])}</p>
</div></div>
{inner}
<section class="tint"><div class="wrap"><div class="shead">
  <h2>Every agreement and policy</h2>
  <p>All of them, in plain language.</p></div>
  <div class="strip"><a href="/legal/"><em>Index</em>All legal documents</a></div>
</div></section>
'''
        body += FOOT
        write(path, body)
        PAGES.append((path, d["updated"], "0.3"))

    # the index
    blocks = ""
    for g in LEGAL_GROUPS:
        rows = sorted([d for d in docs if d["group"] == g], key=lambda x: x["order"])
        if not rows:
            continue
        cards = "".join(
            f'<a class="card" href="{d["path"]}"><span class="k">Updated {e(d["updated"])}</span>'
            f'<h3>{e(d["title"])}</h3><p>{e(d["summary"])}</p>'
            f'<span class="meta">Read it &rarr;</span></a>' for d in rows)
        blocks += (f'<section><div class="wrap"><div class="shead"><h2>{e(g)}</h2></div>'
                   f'<div class="cards">{cards}</div></div></section>')

    crumb_html, crumb_schema = crumbs([("Home", "/"), ("Legal", None)])
    body = head_(fit_title("Legal: Terms, Privacy and Policies"),
                 fit_desc("Every agreement and policy that governs Wall Dock Deck, "
                          "in plain language"),
                 "/legal/", schema=[crumb_schema])
    body += crumb_html + f'''
<div class="answer"><div class="wrap">
  <span class="eyebrow">Legal</span>
  <h1>Every agreement and policy, in plain language</h1>
  <p class="qualifier">We publish all of it. If something here is unclear, that is a fault
  worth telling us about &mdash; email <a href="mailto:hello@walldockdeck.com">hello@walldockdeck.com</a>.</p>
</div></div>
{blocks}
'''
    body += FOOT
    write("/legal/", body)
    PAGES.append(("/legal/", TODAY, "0.3"))
    return len(docs)


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

    robots = (f"User-agent: *\nAllow: /\nDisallow: /_build/\nDisallow: /_preview/\n\n"
              f"Sitemap: {SITE}/sitemap.xml\n")
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf8").write(robots)

    # IndexNow: the key has to be served as a text file at the site root, whose
    # name is the key itself. Bing, Yandex and several AI crawlers read it;
    # Google has not adopted IndexNow, so this is not a Google play.
    kp = os.path.join(DATA, "indexnow.key")
    if os.path.exists(kp):
        key = open(kp, encoding="utf8").read().strip()
        if re.fullmatch(r"[0-9a-fA-F]{8,128}", key):
            open(os.path.join(ROOT, f"{key}.txt"), "w", encoding="utf8").write(key)


# ------------------------------------------------------------ trust pages
def build_verify():
    """The method page. This exists because the whole position rests on one
    claim -- every figure carries its code section and the date it was checked --
    and until now the site never said so anywhere a reader could find it."""
    path = "/how-we-verify/"
    title = fit_title("How We Verify Every Rule on This Site")
    desc = fit_desc(
        "Primary code only, the section recorded, the date recorded. Nothing publishes "
        "without both",
        "What we do when we cannot confirm a rule")
    crumb_html, crumb_schema = crumbs([("Home", "/"), ("How we verify", None)])
    body = head_(title, desc, path, schema=[crumb_schema])
    body += crumb_html + f'''

<div class="answer"><div class="wrap">
  <span class="eyebrow">Our method &middot; {e(AUTHOR_NAME)}</span>
  <h1>How we verify every rule on this site</h1>
  <p class="qualifier">Every elevation, setback and deadline published here was read out of the
  primary code, not copied from another website. Each one carries the section it came from and the
  month we checked it. If we cannot confirm a rule from the code itself, we do not publish it &mdash;
  and we say so rather than filling the gap with a plausible guess.</p>
</div></div>

<section><div class="wrap">
  <div class="shead"><h2>The standard</h2>
  <p>Four rules, applied to every figure on the site without exception.</p></div>
  <div class="rows">
    <div><b>Primary sources only</b><span>County and municipal code, state statute, administrative code, and official guidance published by the authority itself. Not contractor blogs, not directories, not other summaries. Where a city publishes its own guidance, we read it alongside the ordinance.</span></div>
    <div><b>The section is recorded</b><span>Every figure is stored with the exact code section it came from, and that citation is printed on the page. If you want to check us, you have what you need to do it in about two minutes.</span></div>
    <div><b>The date is recorded</b><span>Every rule carries the month we last checked it. That date is the one in our records, never today&rsquo;s. A page that silently restamps itself is lying about its freshness.</span></div>
    <div><b>No source, no page</b><span>This one is enforced mechanically, not by good intentions. Our build only publishes a rule marked verified with both a citation and a date. An unfinished entry produces no page at all, which is why some cities are missing rather than thin.</span></div>
  </div>
</div></section>

<section class="tint"><div class="wrap">
  <div class="shead"><h2>What we do when it is not clear</h2>
  <p>Regulations in South Florida are genuinely inconsistent between neighbouring towns. These are the cases that come up most, and how we handle each.</p></div>
  <div class="rows">
    <div><b>When the county and the city disagree</b><span>We publish both and say which one governs. In Broward the county sets a standard every city had to adopt, and several cities went stricter &mdash; so the number that applies to you is your city&rsquo;s, not the county&rsquo;s. We say that on the page rather than averaging it away.</span></div>
    <div><b>When the rule is not in the code</b><span>It happens more than you would expect. Some towns set their seawall elevation in an engineering standards manual rather than an ordinance, where searching the code finds nothing. We cite where it actually lives.</span></div>
    <div><b>When the datum differs</b><span>A height means nothing without the datum it is measured from. Where a town states its rule in mean low water and its neighbour states theirs in NAVD88, we print both as given and do not convert between them. The offset is local, and converting by rule of thumb produces a wall at the wrong height.</span></div>
    <div><b>When we cannot confirm it</b><span>We publish nothing. Monroe County is the current example: we have not been able to establish from public sources whether the county sets a minimum seawall height, so the Keys pages carry no elevation figure. An empty space is honest. A guess that reads like a fact is not.</span></div>
    <div><b>When a rule changes</b><span>Rules move, sometimes quickly. Miami-Dade rewrote its seawall permitting in July 2025 for the first time in decades. When we find a change, the figure and its date are updated together.</span></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="shead"><h2>What this is not</h2></div>
  <div class="rows">
    <div><b>Not legal or engineering advice</b><span>This is published information with its sources attached. It is not a legal opinion and it is not an engineering determination.</span></div>
    <div><b>Not a substitute for your building department</b><span>Confirm the current requirement with your city before you design or sign anything. We print the date we checked precisely so you can see how old our reading is.</span></div>
    <div><b>Not a price</b><span>We do not publish cost estimates. No honest figure exists before someone surveys your wall, and we will not republish anyone else&rsquo;s bid.</span></div>
  </div>
</div></section>

<section class="tint"><div class="wrap">
  <div class="shead"><h2>Found something wrong?</h2>
  <p>We would rather hear it than not. If a figure here does not match what your building department
  told you, send us the section and we will re-check it against the code and correct the page. A
  corrected page is worth more than one that was never challenged.</p></div>
  {slot("R3", "", "seawall-compliance")}
</div></section>
'''
    body += FOOT
    write(path, body)
    PAGES.append((path, TODAY, "0.6"))


def build_about():
    """Who we are and how we are paid. The legal set has always been straight about
    the referral model; the public pages never explained it."""
    path = "/about/"
    title = fit_title("About WallDockDeck: Who We Are, How We Are Paid", brand=False)
    desc = fit_desc(
        "What we do, how the referral model works and how we are paid",
        "Seawalls, docks and waterfront decks from the Keys to Palm Beach")
    crumb_html, crumb_schema = crumbs([("Home", "/"), ("About", None)])
    body = head_(title, desc, path, schema=[crumb_schema])
    body += crumb_html + f'''

<div class="answer"><div class="wrap">
  <span class="eyebrow">About</span>
  <h1>Who we are, and how we are paid</h1>
  <p class="qualifier">WallDockDeck publishes the waterfront building rules for South Florida and
  connects owners with licensed marine contractors. We do not perform the work ourselves, and we are
  paid by the contractors we refer to &mdash; not by you. Both of those facts change how you should
  read everything else here, so they go at the top rather than in the small print.</p>
</div></div>

<section><div class="wrap">
  <div class="shead"><h2>What we do</h2></div>
  <div class="rows">
    <div><b>We publish the rules</b><span>The seawall, dock and waterfront deck requirements for the cities we cover, each with its code section and the date we checked it. Most of this exists only as legal text in a municipal PDF. We publish the number.</span></div>
    <div><b>We score your shoreline</b><span>The Shore Score is a screening based on public data and the answers you give us. It tells you what your answers point to and what to ask next. It is not an engineering inspection and we never call it one.</span></div>
    <div><b>We connect you to a licensed contractor</b><span>If you ask to be connected, we pass your details to a licensed marine contractor covering your area. They are an independent business, not our employee or our agent, and they may contact you directly.</span></div>
    <div><b>We do not do the work</b><span>We refer. We do not build, repair, inspect or engineer anything, and we never quote a price for work.</span></div>
  </div>
</div></section>

<section class="tint"><div class="wrap">
  <div class="shead"><h2>How we are paid, plainly</h2>
  <p>Worth knowing before you decide how much weight to give our advice.</p></div>
  <div class="rows">
    <div><b>Contractors pay us, you do not</b><span>Our contractor partners pay us for referrals. Everything on this site is free to you, including the guides and the Shore Score.</span></div>
    <div><b>What that means for our incentives</b><span>We have an interest in you contacting a contractor. We have no interest in which option you choose or how much you spend &mdash; we are not paid on the size of the job, which is why we publish what drives a price rather than a price.</span></div>
    <div><b>Why we publish rules rather than quotes</b><span>A number without a survey is a guess, and a quote from someone who has not seen your wall is worth nothing. The rules are checkable. That is what we can honestly give you.</span></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="shead"><h2>Who writes this</h2></div>
  <div class="rows">
    <div><b>{e(AUTHOR_NAME)}</b><span>Researches and verifies the rules published here. Every figure is read out of the primary code, recorded with its section and the month it was checked, and nothing publishes without both. The method is set out in full on our <a href="/how-we-verify/">verification page</a>.</span></div>
    <div><b>Where we cover</b><span>Monroe, Miami-Dade, Broward and Palm Beach counties &mdash; the Florida Keys to Palm Beach. We publish a city only once we have verified its rules, which is why the list grows rather than starting complete.</span></div>
    <div><b>What we will not do</b><span>Publish a figure we cannot source, republish another party&rsquo;s bid, or present an estimate as a quote.</span></div>
  </div>
</div></section>

<section class="tint"><div class="wrap">{slot("R3", "", "seawall-compliance")}</div></section>
'''
    body += FOOT
    write(path, body)
    PAGES.append((path, TODAY, "0.6"))


def main():
    n_matrix = build_matrix()
    n_clus = build_clusters()
    build_resources_hub()
    build_agents(False)
    build_agents(True)
    build_costs()
    n_reg = build_regions()
    n_dl = build_downloads()
    build_book()
    build_coverage()
    build_verify()
    build_about()
    n_legal = build_legal()
    build_sitemap()

    held = len(CT) - len(LIVE)
    print(f"matrix pages      {n_matrix:>4}   (of {len(CT)} rows; {held} not yet verified)")
    print(f"cluster hubs      {n_clus:>4}")
    print(f"resources hub        1")
    print(f"agent pages          2   /agents/ /luxury/")
    print(f"cost page            1   /resources/what-it-costs/")
    print(f"trust pages          2   /about/ /how-we-verify/")
    print(f"county pages      {n_reg:>4}   /{{county}}/{{service}}/")
    print(f"downloads page       1   {n_dl} files listed")
    print(f"legal pages       {n_legal+1:>4}   /legal/ + {n_legal} documents")
    print(f"sitemap entries   {len(PAGES)+1:>4}")
    print(f"\nindex.html and /guides untouched.")

    import subprocess
    subprocess.run([sys.executable, os.path.join(ROOT, "_build", "guard.py")], check=True)


if __name__ == "__main__":
    main()
