#!/usr/bin/env python3
"""Build the downloadable assets the capture offers actually promise.

Nothing here is invented. The height sheets are generated from the same
verified CityTopics rows the website pages are built from, so a sheet cannot
exist for a city whose rule has not been verified and sourced.

Output: /downloads/*.pdf
"""
import csv, html, os, re
from datetime import date
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "_build", "data")
OUT = os.path.join(ROOT, "downloads")
os.makedirs(OUT, exist_ok=True)
TODAY = date.today().strftime("%B %Y")


def load(n):
    with open(os.path.join(DATA, n), newline="", encoding="utf8") as f:
        return list(csv.DictReader(f))


CITIES = {c["slug"]: c for c in load("Cities.csv")}
CT = [r for r in load("CityTopics.csv") if r["status"] == "verified"]


def e(s):
    return html.escape(str(s or ""))


MARK = ('<svg viewBox="0 0 34 34" width="26" height="26"><rect width="34" height="34" rx="7" fill="#0B2536"/>'
        '<rect x="7" y="8" width="5" height="18" rx="1" fill="#7FC6CF"/>'
        '<rect x="14.5" y="14" width="12.5" height="3.5" rx="1" fill="#fff"/>'
        '<rect x="14.5" y="20" width="12.5" height="3.5" rx="1" fill="#E0701A"/>'
        '<path d="M5 28.5c3-1.6 6-1.6 9 0s6 1.6 9 0 6-1.6 7 0" stroke="#7FC6CF" stroke-width="1.6" fill="none"/></svg>')

CSS = """
@page { size: Letter; margin: 0; }
*{box-sizing:border-box}
body{margin:0;font-family:"Source Sans 3",Helvetica,Arial,sans-serif;color:#10283A;font-size:10.6pt;
     line-height:1.55;-webkit-print-color-adjust:exact;print-color-adjust:exact}
h1,h2,h3{font-family:"Archivo",Arial,sans-serif;font-stretch:86%;margin:0;line-height:1.1;letter-spacing:-.015em}
.page{width:215.9mm;min-height:279.4mm;display:flex;flex-direction:column}
.top{background:#0B2536;color:#E8F1F5;padding:11mm 16mm 9mm;border-bottom:3pt solid #E0701A;flex:none}
.brand{display:flex;align-items:center;gap:8pt;margin-bottom:7mm}
.brand b{font-family:"Archivo",sans-serif;font-stretch:80%;font-weight:800;font-size:15pt;color:#fff}
.brand b i{font-style:normal;color:#7FC6CF}
.brand .tag{font-family:"IBM Plex Mono",monospace;font-size:7pt;letter-spacing:.18em;text-transform:uppercase;
            color:#7FC6CF;border-left:1px solid #2F5266;padding-left:9pt;margin-left:4pt}
.top h1{font-size:25pt;font-weight:800;color:#fff;max-width:150mm}
.top .sub{font-size:10.4pt;color:#9FB7C4;margin-top:6pt;max-width:140mm}
.mid{padding:9mm 16mm 0;flex:1}
.figure{display:flex;align-items:baseline;gap:10pt;margin-bottom:6mm}
.figure b{font-family:"Archivo",sans-serif;font-stretch:80%;font-weight:800;font-size:40pt;color:#0F7482;line-height:.9}
.figure span{font-family:"IBM Plex Mono",monospace;font-size:11pt;color:#41586A}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:7.4pt;letter-spacing:.17em;text-transform:uppercase;
         color:#0B5A66;background:#E0EFF1;display:inline-block;padding:3pt 8pt;border-radius:4pt;margin-bottom:4mm}
h2{font-size:14pt;font-weight:700;margin:0 0 3mm}
.lead{font-size:10.4pt;color:#41586A;max-width:160mm;margin-bottom:6mm}
table{width:100%;border-collapse:collapse;margin-bottom:6mm}
td{padding:6pt 8pt;border-bottom:1px solid #EAF0F2;vertical-align:top;font-size:9.8pt}
td.k{font-family:"IBM Plex Mono",monospace;font-size:7.8pt;letter-spacing:.07em;text-transform:uppercase;
     color:#6F8492;width:42mm}
table.rt th{text-align:left;padding:5pt 8pt;border-bottom:1px solid #D8E1E6;
     font-family:"IBM Plex Mono",monospace;font-size:7.4pt;letter-spacing:.13em;
     text-transform:uppercase;color:#6F8492;font-weight:500}
table.rt td.mono{font-family:"IBM Plex Mono",monospace;font-size:8.6pt;color:#6F8492}
.src{background:#F4F7F8;border-left:2.5pt solid #0F7482;padding:5mm 6mm;font-size:9.2pt;color:#41586A;margin-bottom:6mm}
.src b{color:#0B2536}
ol{margin:0 0 6mm;padding-left:0;list-style:none;counter-reset:n}
ol li{counter-increment:n;position:relative;padding-left:12mm;margin-bottom:4.5mm}
ol li::before{content:counter(n);position:absolute;left:0;top:0;width:7mm;height:7mm;border-radius:50%;
  background:#0F7482;color:#fff;font-family:"IBM Plex Mono",monospace;font-size:8.5pt;font-weight:600;
  display:flex;align-items:center;justify-content:center}
ol li b{display:block;font-family:"Archivo",sans-serif;font-stretch:88%;font-weight:700;font-size:11.4pt;
        color:#0B2536;margin-bottom:1.5pt}
ol li span{font-size:9.8pt;color:#41586A}
.foot{flex:none;background:#F4F7F8;border-top:2pt solid #E0701A;padding:5mm 16mm;font-size:7.8pt;color:#6E8492;
      display:flex;justify-content:space-between;gap:8mm;margin-top:6mm}
.foot b{color:#0B2536}
"""

HEAD = ('<!DOCTYPE html><html><head><meta charset="utf-8">'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=Archivo:wdth,wght@75..100,400..800&family=Source+Sans+3:wght@400;600;700'
        '&family=IBM+Plex+Mono:wght@400;500&display=swap">'
        f'<style>{CSS}</style></head><body>')


def shell(tag, h1, sub, inner):
    return (HEAD + '<div class="page"><div class="top">'
            f'<div class="brand">{MARK}<b>Wall<i>Dock</i>Deck</b><span class="tag">{e(tag)}</span></div>'
            f'<h1>{h1}</h1><div class="sub">{sub}</div></div>'
            f'<div class="mid">{inner}</div>'
            '<div class="foot"><div><b>WallDockDeck</b> &middot; Seawalls, docks &amp; waterfront decks '
            '&middot; Florida Keys to Palm Beach<br>This is a reference sheet, not an engineering opinion. '
            'Confirm with your building department before you rely on it.</div>'
            f'<div style="text-align:right"><b>ScoreMyShore.com</b><br>{TODAY}</div></div>'
            '</div></body></html>')


def rows_table(raw):
    out = ""
    for part in [p.strip() for p in str(raw or "").split("|") if p.strip()]:
        bits = part.split("::")
        out += f'<tr><td class="k">{e(bits[0].strip())}</td><td>{e("::".join(bits[1:]).strip())}</td></tr>'
    return f"<table>{out}</table>" if out else ""


def height_sheets():
    made = []
    for r in CT:
        if r["topicSlug"] != "seawall-height-requirement":
            continue
        c = CITIES.get(r["citySlug"])
        if not c:
            continue
        inner = (f'<span class="eyebrow">{e(c["city"])} &middot; {e(c["county"])} County</span>'
                 f'<div class="figure"><b>{e(r["headline_answer"])}</b><span>{e(r["unit"])}</span></div>'
                 f'<p class="lead">{e(r["qualifier"])}</p>'
                 f'<h2>The detail</h2>{rows_table(r.get("detail_rows"))}'
                 f'<div class="src"><b>Where this comes from:</b> {e(r["source"])}<br>'
                 f'<b>Verified:</b> {e(r["verified_date"])}. Rules change — check the date above against today.</div>'
                 '<h2>Before you call a contractor</h2>'
                 '<ol>'
                 '<li><b>Know your datum</b><span>A height means nothing without the datum it is measured from. '
                 'NAVD88 and MLW are different reference points and the same wall gives different numbers in each. '
                 'Ask which one any quoted elevation refers to.</span></li>'
                 '<li><b>Get the existing elevation surveyed</b><span>You cannot tell whether a wall meets the '
                 'requirement by looking at it. A surveyor shooting the top of the cap settles it in an hour.</span></li>'
                 '<li><b>Ask what triggers the requirement</b><span>Most cities only apply the minimum to new walls '
                 'or to substantial repair. What counts as substantial is defined differently in each city, and it '
                 'is usually a percentage of length or of cost.</span></li>'
                 '<li><b>Ask about building higher now</b><span>Several cities require a wall built below the final '
                 'figure to be engineered so it can be raised later. Doing it once is cheaper than doing it '
                 'twice.</span></li>'
                 '</ol>')
        h1 = f'Seawall height in<br>{e(c["city"])}'
        sub = "The elevation your city requires, the datum it is measured in, and the section of code that says so."
        made.append((f'height-sheet-{r["citySlug"]}.pdf', shell("City Height Sheet", h1, sub, inner)))
    return made


WARNING_SIGNS = [
    ("Sinkholes or soft ground behind the wall",
     "A depression, a soft patch or a void in the lawn, patio or driveway near the wall. It usually means soil is "
     "escaping through the wall into the water, which hollows out the ground you are standing on long before "
     "anything looks wrong from the water side."),
    ("Cracks in the cap",
     "Hairline cracks are common. Cracks you can fit a coin into, cracks that run through the full depth, or cracks "
     "that have opened wider since you last looked are not."),
    ("Gaps opening between panels",
     "Panels are meant to sit tight against each other. A visible gap, or a line of daylight at low tide, is a path "
     "for soil to leave."),
    ("Water or sand coming through the joints",
     "Sand fanning out below a joint at low tide, or water seeping through on a falling tide, is soil loss in "
     "progress. It is one of the clearest signs a wall is actively failing."),
    ("A wall that leans, bows or has gone out of line",
     "Sight along the top of the cap from one end. A straight wall reads straight. Bowing outward at the middle of a "
     "run usually points to tieback or anchor trouble behind it."),
    ("Panels out of alignment with their neighbours",
     "One panel standing proud of the next, or rotated relative to it, means something has moved that was not "
     "supposed to."),
    ("Rust stains and spalling concrete",
     "Brown staining bleeding out of the concrete means the steel inside is corroding. Corroding steel expands, and "
     "expanding steel breaks the concrete off from the inside. Spalled patches with bar visible are well advanced."),
    ("Weep holes blocked or missing",
     "Weep holes let water pressure out from behind the wall. Blocked with debris, or never installed, and the wall "
     "carries a load it was not designed for every time it rains."),
    ("Settlement at the base of the wall",
     "Pavers, a pool deck or a slab dipping towards the wall is the same soil-loss story as a sinkhole, read from the "
     "surface."),
    ("Vegetation growing in the joints or the cap",
     "Roots open cracks and hold water against the concrete. A seedling in a joint is a small problem now and a split "
     "panel in a few years."),
    ("Erosion at the toe, on the water side",
     "Scour at the base of the wall takes away the material holding it in place. It is easiest to see at an "
     "exceptionally low tide."),
    ("A neighbour's wall failing at the property line",
     "Walls carry load across a boundary. A failure next door frequently becomes a failure at your end of the run, "
     "and whose it is becomes an expensive argument."),
]


def warning_checklist():
    items = "".join(f'<li><b>{e(t)}</b><span>{e(d)}</span></li>' for t, d in WARNING_SIGNS)
    inner = ('<span class="eyebrow">Walk the wall &middot; 20 minutes</span>'
             '<h2>How to use this</h2>'
             '<p class="lead">Walk the full length of your wall twice: once from the land side at any tide, and once '
             'from the water or a dock at the lowest tide you can catch. Low tide is when a wall tells the truth. '
             'Photograph anything you tick, from the same spot each time, so you can see whether it is moving.</p>'
             f'<ol>{items}</ol>'
             '<div class="src"><b>What a tick means.</b> One item on its own is worth watching. Two or more, or any '
             'sign of soil leaving the property, is worth a professional look now rather than at the end of the '
             'season. This sheet is a screening aid for owners, not an engineering inspection, and it cannot tell '
             'you what a wall needs or what it will cost.</div>')
    return [("seawall-warning-signs-checklist.pdf",
             shell("Owner Checklist", "Twelve signs a seawall<br>is failing",
                   "What to look for, where to look for it, and what it means when you find it.", inner))]


BUYER_QUESTIONS = [
    ("How old is the seawall, and who built it?",
     "Ask for the permit number. A wall with no permit history is a wall with no record of what is behind it."),
    ("What elevation is the top of the cap, in NAVD88?",
     "Not 'it's fine'. A number, from a survey. This is the question the whole file turns on."),
    ("Does that meet what the city requires today?",
     "The requirement differs by city and sometimes by flood zone. The seller may be compliant, grandfathered, or "
     "neither."),
    ("If it does not, what triggers having to fix it?",
     "Most cities only apply the current minimum to new walls or substantial repair. Find out what counts as "
     "substantial here, because it decides whether this is your problem on day one or in ten years."),
    ("Has the wall been repaired, and what was done?",
     "Ask for invoices, not recollections. Cap work and panel work are very different jobs."),
    ("Are there tiebacks or anchors, and when were they last looked at?",
     "The part that fails first is usually the part nobody can see."),
    ("Is there any sign of soil loss on the property?",
     "Sinkholes, soft ground, settling pavers, a dip in the lawn near the wall."),
    ("Who owns the wall at each end?",
     "Shared walls and walls crossing a property line turn into disputes. Establish it before closing, not after."),
    ("Is there a dock, and does its permit match what is actually there?",
     "Docks are often extended or rebuilt without paperwork."),
    ("How deep is the water at the dock at mean low tide?",
     "A boat that does not float at low tide is a dock that does not work."),
    ("What size vessel does the dock and lift actually take?",
     "Check the lift's rated capacity against the boat the buyer intends to keep there, not the one in the "
     "photographs."),
    ("Is the property in a tidally influenced area, and is there a disclosure obligation?",
     "Some local codes require a specific written disclosure in the sale contract. Broward County does, "
     "countywide (Sec. 39-408), and so does Delray Beach (LDR 7.1.7(D)(7))."),
    ("What does the flood map say, and what is the base flood elevation?",
     "It sets the seawall maximum in some cities, and it affects flood insurance requirements and price."),
    ("Will the insurer write it, and on what terms?",
     "Ask early. A seawall problem can turn into an insurance problem, which turns into a financing problem."),
    ("What would it cost to put right?",
     "Get it priced during the inspection period. A number is a negotiating position; 'the wall looks old' is not."),
]


def buyer_checklist():
    items = "".join(f'<li><b>{e(q)}</b><span>{e(w)}</span></li>' for q, w in BUYER_QUESTIONS)
    inner = ('<span class="eyebrow">Inspection period &middot; the clock is running</span>'
             '<h2>Ask these before the inspection period closes</h2>'
             '<p class="lead">A waterfront purchase has one structure on it that a Florida home inspector is not '
             'required to inspect (Rule 61-30.810), and it is often the most expensive one. These are the questions that surface a problem while '
             'you can still do something about it.</p>'
             f'<ol>{items}</ol>'
             '<div class="src"><b>The timing point.</b> Found at the listing appointment, a seawall problem is a '
             'pricing conversation. Found on day nine of a fifteen-day inspection period, it is a file that dies. '
             'Ask these in the first week.</div>')
    return [("waterfront-buyer-checklist.pdf",
             shell("Buyer Checklist", "Fifteen questions<br>before you buy waterfront",
                   "What to ask about the seawall, the dock and the deck while you still have time to act on the "
                   "answer.", inner))]



DECK_ITEMS = [
    ("Bounce on it, at the middle of a span",
     "Stand midway between two joists and shift your weight. A deck that moves underfoot is a deck whose framing or "
     "fasteners are going, whatever the boards look like."),
    ("Push the railing hard, at the top",
     "Lean into it at the corners and anywhere a run ends. Railings fail at the post connection, and a railing that "
     "gives is the single most dangerous thing on a waterfront deck."),
    ("Probe the posts at the waterline and at grade",
     "Push a screwdriver into the post where it meets the ground, the concrete, or the water. If it sinks in, the "
     "post is soft inside even where the outside looks sound."),
    ("Look at the fasteners, not the boards",
     "Rust streaks, lifted screw heads and black staining around a fastener mean the metal is failing. Salt air eats "
     "anything that is not stainless or properly rated."),
    ("Check where the deck meets the house",
     "A failed ledger connection can bring the whole deck down. Look for separation, rot in the band joist, "
     "or bolts that have corroded."),
    ("Look under it, at the joist hangers",
     "Hangers rust out from the back. If you can see light between a joist and its hanger, or the hanger is scaled "
     "and flaking, it is carrying far less than it was designed to."),
    ("Check the boards around any planter or mat",
     "Anything that holds moisture against the deck is where rot starts. Lift them and look."),
    ("Walk the edges and the stairs",
     "Edge boards and stair treads take the most water and the most weight per square foot. Soft, cupped or "
     "springing treads are a fall waiting to happen."),
    ("Measure the railing height and the gaps",
     "Codes set a minimum height and a maximum gap between balusters, and older decks frequently meet neither. If a "
     "4-inch ball passes through a gap, it is a problem."),
    ("Look for movement where the deck meets the seawall cap",
     "A deck built over or onto a cap moves when the cap moves. New gaps here are often the first visible sign that "
     "the wall behind it is going."),
]


def deck_checklist():
    items = "".join(f'<li><b>{e(t)}</b><span>{e(d)}</span></li>' for t, d in DECK_ITEMS)
    inner = ('<span class="eyebrow">Ten minutes &middot; no tools but a screwdriver</span>'
             '<h2>How to use this</h2>'
             '<p class="lead">A waterfront deck ages differently from an inland one. Salt air attacks the metal, not '
             'just the wood, so the parts that fail first are the ones holding everything together rather than the '
             'boards you are standing on. Check it before the season, not after.</p>'
             f'<ol>{items}</ol>'
             '<div class="src"><b>What to do with what you find.</b> Soft posts, a moving railing or anything wrong '
             'at the ledger are reasons to keep people off the deck until it is looked at properly. This is an '
             'owner screening sheet, not a structural inspection, and it cannot tell you what a repair involves.</div>')
    return [("deck-safety-checklist.pdf",
             shell("Owner Checklist", "Ten checks on a<br>waterfront deck",
                   "The parts that fail first on the water, and how to find them without taking anything apart.",
                   inner))]


# ---------------------------------------------------------------- agent sheet
# Backs the agent_tools offer, which has been live on 8 placements with nothing
# behind it. Every figure here comes from the verified CityTopics rows, so this
# sheet cannot claim a number the website has not sourced and dated.

AGENT_QUESTIONS = [
    ("How high is the cap, and in which datum?",
     "A figure in MLW is not the same number as a figure in NAVD88. Contractor drawings "
     "in this market are sometimes written to MLW while the city states its rule in NAVD88. "
     "Ask which datum before anyone compares the two."),
    ("When was the wall last inspected, and by whom?",
     "Florida's home inspection standards do not require the inspector to inspect a seawall or dock "
     "(Rule 61-30.810). If the seller has an engineer's "
     "report, get it now rather than discovering it in the buyer's hands."),
    ("Has any work been permitted, and was it closed out?",
     "An open permit on a marine structure is a title and closing problem, not a punch-list item."),
    ("Is the wall shared with a neighbour?",
     "Shared walls, shared caps and tie-back easements change who pays and who can act. "
     "Find out before a buyer's attorney does."),
    ("Does any of it sit on a neighbour's line or in a waterway setback?",
     "The zoning location survey answers this. Ask whether one exists."),
    ("Is there a sinkhole, a depression, or bare soil along the cap?",
     "Soil leaving the property is the single most expensive thing to find late."),
    ("What is the city's current minimum, and does this wall meet it?",
     "The rule changes at the city line, not the county line. Our city pages carry the "
     "figure, the code section, and the date we checked it."),
]

AGENT_KILLERS = [
    ("Substantial repair pulls in the whole shoreline",
     "In several cities, once work exceeds a threshold \u2014 commonly more than 50% of the "
     "length, the cap included, or any work changing elevation along more than 50% \u2014 the "
     "minimum elevation applies to the continuous wall along the entire property, not just "
     "the stretch being fixed. A quote for 40 feet can become a quote for 200."),
    ("The wall is compliant today and not compliant on rebuild",
     "Existing walls are generally allowed to stay. The moment they are substantially "
     "repaired or replaced, today's minimum applies. A wall that is fine now can carry a "
     "much larger number the day it needs work."),
    ("Build low now, build again later",
     "Where a city allows an interim elevation before a future deadline, the wall normally "
     "has to be engineered so it can be raised later. That is two mobilisations, not one. "
     "Ask what it costs to build to the final elevation now."),
]


def agent_sheet():
    rows = ""
    live = sorted(
        [r for r in CT if r["topicSlug"] == "seawall-height-requirement"],
        key=lambda r: (CITIES.get(r["citySlug"], {}).get("county", ""),
                       CITIES.get(r["citySlug"], {}).get("city", "")))
    for r in live:
        c = CITIES.get(r["citySlug"], {})
        rows += (f'<tr><td><b>{e(c.get("city", r["citySlug"]))}</b></td>'
                 f'<td>{e(c.get("county",""))}</td>'
                 f'<td><b>{e(r.get("headline_answer",""))}</b> {e(r.get("unit",""))}</td>'
                 f'<td class="mono">{e(r.get("verified_date",""))}</td></tr>')

    qs = "".join(f'<li><b>{e(q)}</b><span>{e(w)}</span></li>' for q, w in AGENT_QUESTIONS)
    ks = "".join(f'<li><b>{e(t)}</b><span>{e(d)}</span></li>' for t, d in AGENT_KILLERS)

    inner = (
        '<span class="eyebrow">Before you list &middot; waterfront</span>'
        '<h2>One disclosure rule worth knowing first</h2>'
        '<p class="lead">In <b>Delray Beach</b>, any contract to sell property in a tidally '
        'influenced area executed after 1 February 2022 must carry a tidal-flood-barrier '
        'disclosure, in bold capitals of at least 14 point. It is written into the land '
        'development regulations, and it is the kind of requirement that surfaces at the '
        'closing table rather than at the listing appointment. Broward County imposes the '
        'same kind of disclosure countywide on contracts executed after 31 December 2020. '
        'Other cities in this market do not all have an equivalent \u2014 check the one you '
        'are in.</p>'
        '<div class="src"><b>Source.</b> City of Delray Beach Land Development Regulations '
        'Sec. 7.1.7(D)(7); Ordinance 23-21, adopted 11 January 2022. Broward County Code '
        'Sec. 39-408 (Ord. No. 2020-11). Verified 2026-10.</div>'
        '<h2 style="margin-top:7mm">Seven questions before you list</h2>'
        f'<ol>{qs}</ol>'
        '<h2 style="margin-top:7mm">Three things that kill a waterfront deal late</h2>'
        f'<ol>{ks}</ol>'
        '<h2 style="margin-top:7mm">Verified minimum cap elevations</h2>'
        '<p class="lead">Published with the code section and the date checked. The rule '
        'changes at the city line. Confirm with the building department before anyone '
        'relies on it in a contract.</p>'
        '<table class="rt"><thead><tr><th>City</th><th>County</th><th>Minimum</th>'
        '<th>Verified</th></tr></thead><tbody>' + rows + '</tbody></table>'
        '<div class="src"><b>How to use this.</b> None of this is an inspection, an '
        'engineering opinion, or a valuation. It is the set of questions that stops a '
        'waterfront deal falling apart in the inspection period, and the figures your '
        'buyer\u2019s engineer will be working from. Full city pages, the code sections '
        'and the dates are at walldockdeck.com.</div>')

    return [("waterfront-listing-sheet.pdf",
             shell("For Agents", "The waterfront listing sheet",
                   "What to check before you list, what your buyer\u2019s engineer will ask, "
                   "and the verified city minimums.", inner))]


def main():
    jobs = (height_sheets() + warning_checklist() + buyer_checklist()
            + deck_checklist() + agent_sheet())
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        for name, html_doc in jobs:
            tmp = os.path.join(ROOT, "_build", "_tmp.html")
            open(tmp, "w", encoding="utf8").write(html_doc)
            pg.goto("file://" + tmp)
            pg.wait_for_timeout(900)
            out = os.path.join(OUT, name)
            pg.pdf(path=out, format="Letter", print_background=True,
                   margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            print(f"  {name:48} {os.path.getsize(out)//1024:>4} KB")
        b.close()
        os.remove(tmp)
    print(f"\n{len(jobs)} assets built into /downloads/")


if __name__ == "__main__":
    main()
