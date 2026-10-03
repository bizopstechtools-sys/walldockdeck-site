"""Content for the free resources area: printable templates and the glossary.

Pure data, no imports from build.py, so build.py can import it without a cycle.

Two rules carried over from the rest of the site:
  * No figure and no legal statement without its primary source. Every one
    below is followed by the section it comes from, and those sources were read
    on WRITTEN. Where we could not confirm a fact from a primary source, it is
    not here.
  * No bracket placeholders. A field the reader fills in is a run of
    underscores, which build.py wraps so it prints as a line.
"""

WRITTEN = "2026-10-03"     # the date these were written and their sources checked

DISCLAIMER = ("This is a template, not legal advice. Have an attorney review anything "
              "you sign or send in a dispute.")

# Source links used more than once.
FS = "http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL="
S_71302 = ("s. 713.02(5), Florida Statutes", FS + "0700-0799/0713/Sections/0713.02.html")
S_71306 = ("s. 713.06, Florida Statutes", FS + "0700-0799/0713/Sections/0713.06.html")
S_71313 = ("s. 713.13, Florida Statutes", FS + "0700-0799/0713/Sections/0713.13.html")
S_71320 = ("s. 713.20, Florida Statutes", FS + "0700-0799/0713/Sections/0713.20.html")
S_11901 = ("s. 119.01, Florida Statutes", FS + "0100-0199/0119/Sections/0119.01.html")
S_11907 = ("s. 119.07, Florida Statutes", FS + "0100-0199/0119/Sections/0119.07.html")
S_25312 = ("s. 253.12, Florida Statutes", FS + "0200-0299/0253/Sections/0253.12.html")
S_25377 = ("s. 253.77, Florida Statutes", FS + "0200-0299/0253/Sections/0253.77.html")
S_403813 = ("s. 403.813, Florida Statutes", FS + "0400-0499/0403/Sections/0403.813.html")
S_FDEP_ERP = ("Florida DEP, Environmental Resource Permitting",
              "https://floridadep.gov/water/submerged-lands-environmental-resources-coordination/content/environmental-resource-permitting")
S_NGS_NEW = ("NOAA National Geodetic Survey, New Datums: Replacing NAVD 88 and NAD 83",
             "https://geodesy.noaa.gov/datums/newdatums/index.shtml")
S_COOPS = ("NOAA CO-OPS, Datum definitions",
           "https://tidesandcurrents.noaa.gov/datum_options.html")
S_KING = ("NOAA National Ocean Service, What is a king tide?",
          "https://oceanservice.noaa.gov/facts/kingtide.html")
S_LIVING = ("NOAA National Ocean Service, What is a living shoreline?",
            "https://oceanservice.noaa.gov/facts/living-shoreline.html")
S_CFR591 = ("44 CFR 59.1, Definitions (National Flood Insurance Program)",
            "https://www.ecfr.gov/current/title-44/chapter-I/subchapter-B/part-59/subpart-A/section-59.1")
S_MSC = ("FEMA Flood Map Service Center", "https://msc.fema.gov/portal/home")


# ===================================================================== templates
# body is HTML. Runs of underscores become fill-in lines. Every template is
# readable in full on the page, ungated, and prints on its own.

TEMPLATES = [
    # ---------------------------------------------------------------- (a)
    dict(
        slug="seawall-code-violation-response",
        kind="Letter",
        title="Response to a seawall code violation notice",
        seo_title="Seawall Violation Notice: A Free Response Letter",
        desc=("A free letter to send your code enforcement office after a seawall notice. "
              "Asks for the cited section and the deadlines, and sets out your plan in writing."),
        intro=("A notice about your seawall usually gives you a short window to respond. This letter "
               "does four things in that window: asks the city to confirm the code section it is relying "
               "on, pins down every deadline in writing, asks for what the inspector actually saw, and puts "
               "your plan and timeline on the record. Fill in the lines, keep a copy, and send it in a way "
               "that leaves proof of delivery."),
        offer="height_sheet",
        cluster="seawall-compliance",
        before=[
            ("Read the notice twice",
             "Find the response deadline, the hearing date if there is one, and the case number. "
             "Those three go at the top of the letter."),
            ("State facts, not guesses",
             "Describe what you have done and what you will do. Do not agree to a cause, a cost or a "
             "finding you have not had checked by an engineer."),
            ("Send it with proof",
             "Certified mail with a return receipt, or the city's own portal or email address for the "
             "case, keeping the confirmation. Either way, keep a copy of exactly what you sent."),
            ("Know your city's clock",
             "Some cities set their own deadlines once a notice issues. We publish them where we have "
             "verified them, for example on the <a href=\"/miami-beach/seawall-height-requirement/\">Miami "
             "Beach</a> and <a href=\"/deerfield-beach/seawall-height-requirement/\">Deerfield Beach</a> pages. "
             "Check yours with the <a href=\"/tools/seawall-height-lookup/\">height lookup</a>."),
        ],
        body="""
<p class="tpl-meta">Date: ______________________</p>
<p class="tpl-meta">To: Code Compliance Division, City of ______________________<br>
Address: ____________________________________________<br>
Email: ______________________________</p>
<p class="tpl-meta"><b>Re:</b> Notice dated ______________ &middot; Case number ______________<br>
Property address: ____________________________________________<br>
Folio or parcel number: ______________________</p>

<p>Dear ______________________,</p>

<p>I own the property above and have received the notice dated ______________ about the seawall.
I am responding within the time the notice allows, and I intend to resolve it. So that I can do
that correctly, I am asking for the following in writing.</p>

<h3>1. The section cited</h3>
<p>Please confirm the code section or sections the notice relies on. If the notice concerns the
height of the wall, please confirm the required elevation and the datum it is measured in
(for example NAVD88), and the edition or ordinance date of the section that applies.</p>

<h3>2. The deadlines</h3>
<p>Please confirm each date the city expects me to meet, and what counts as meeting it:</p>
<ul>
  <li>A response to this notice: ______________</li>
  <li>Evidence of progress: ______________</li>
  <li>A permit application filed: ______________</li>
  <li>Work completed and inspected: ______________</li>
</ul>
<p>Please also tell me whether these dates are paused or extended while a permit is under review
by the city or by another agency, and how to request an extension if one is needed.</p>

<h3>3. What the city observed</h3>
<p>Please send copies of the inspection report, photographs, measurements and any other records
the notice is based on.</p>

<h3>4. My plan and timeline</h3>
<p>These are the steps I have taken or will take:</p>
<ul>
  <li>Engineer or licensed marine contractor engaged: ______________________,
      license number ______________, on ______________</li>
  <li>Survey of the wall's location and elevation ordered on ______________</li>
  <li>Permit application expected to be filed by ______________</li>
  <li>Work expected to start by ______________ and finish by ______________</li>
  <li>Interim measures in the meantime: ________________________________________</li>
</ul>
<p>I will tell you promptly if any of these dates changes, and why.</p>

<h3>5. Written confirmation</h3>
<p>Please confirm in writing that you have received this response, whether the timeline above
is acceptable, and the date of any hearing. I can be reached at ______________________ (phone)
or ______________________________ (email).</p>

<p>Sincerely,</p>
<p class="tpl-sign">______________________________<br>
Printed name: ______________________________<br>
Owner of the property above</p>

<p class="tpl-meta">Enclosures: copy of the notice; ______________________________</p>
""",
    ),

    # ---------------------------------------------------------------- (b)
    dict(
        slug="contractor-quote-comparison",
        kind="Worksheet",
        title="Contractor quote comparison worksheet",
        seo_title="Seawall Quote Comparison Worksheet (Free, Printable)",
        desc=("Three seawall quotes side by side: scope, permits, surveys, mitigation, cap elevation "
              "and datum, change-order prices, payments, licence."),
        intro=("Two seawall quotes rarely price the same job. One includes the permit fees and the "
               "surveys; the other lists them as exclusions and comes in lower. This worksheet puts every "
               "line that commonly differs in one column per contractor, so the gaps show. Where a quote "
               "says nothing, write “not stated” — that is an answer too, and the question to ask next."),
        offer="county_guide",
        cluster="seawall-compliance",
        before=[
            ("Compare the approach first",
             "A quote to repair panels and restore the cap is not comparable to one for a new wall in "
             "front of the old one. Our <a href=\"/resources/what-it-costs/\">cost page</a> sets out the "
             "three approaches."),
            ("Make the elevation explicit",
             "Every quote should state the finished cap elevation and its datum. A height without a datum "
             "cannot be checked against your city's rule. See the <a href=\"/glossary/navd88/\">NAVD88</a> "
             "entry."),
            ("Verify the licence yourself",
             "Look the licence number up with the issuing authority and ask the insurer, not the contractor, "
             "to confirm the certificate of insurance. Write the date you checked."),
            ("Ask about lien releases",
             "Florida has statutory release forms for each payment. See "
             "<a href=\"/glossary/release-of-lien/\">release of lien</a>."),
        ],
        worksheet=[
            ("Who", [
                "Contractor name",
                "Licence number, and where and when you verified it",
                "Insurance certificate received, and verified with the insurer on",
                "Quote date, and date the price is valid until",
            ]),
            ("Scope", [
                "Approach: repair and restore cap, replace cap, or new wall",
                "Linear feet included",
                "Finished cap elevation, with datum",
                "Survey the elevation is based on, and its date",
                "Engineering and sealed plans included",
                "Demolition and disposal included",
                "Anchors: number, type, spacing (tie-backs or deadmen)",
                "Drainage: weep holes and filter fabric",
                "Riprap at the toe",
            ]),
            ("Commonly excluded", [
                "Permit fees and any bonds",
                "Surveys: as-built, bathymetric, geotechnical",
                "Benthic survey",
                "Mitigation: seagrass, coral, riprap relocation",
                "Electrical and plumbing: dock power, water, lights",
                "Restoration: landscaping, pavers, irrigation",
            ]),
            ("Money and terms", [
                "Unit price, extra linear foot of cap",
                "Unit price, extra anchor",
                "Unit price, extra pile or panel",
                "Unit price, fill per cubic yard",
                "Payment schedule: signing, mobilisation, milestones, completion",
                "Lien releases provided with each payment",
                "Warranty: length, and workmanship or materials or both",
                "Start date and expected duration",
                "Total quoted",
                "Total once the exclusions above are added",
            ]),
        ],
        body="",
    ),

    # ---------------------------------------------------------------- (c)
    dict(
        slug="seller-seawall-checklist",
        kind="Checklist",
        title="Seller's seawall information checklist",
        seo_title="Selling Waterfront? The Seawall Paperwork to Gather",
        desc=("What to gather about your seawall before you list: age, permits and whether they "
              "closed, cap elevation in NAVD88, repairs and notices."),
        intro=("A buyer's inspector, engineer and lender will all ask about the seawall, usually inside a "
               "short inspection period. Having the answers ready keeps the conversation about price rather "
               "than about missing paperwork. This is a list of information to gather. It is not a "
               "disclosure form, and it does not tell you what you are legally required to disclose."),
        offer="fifteen_q",
        cluster="buying-and-selling",
        before=[
            ("What you must disclose is a separate question",
             "That depends on Florida law, your contract and your city. Ask your listing agent and your "
             "attorney. This checklist only helps you find the facts."),
            ("Some cities set their own wording",
             "Delray Beach, for example, requires sale contracts for property in tidally influenced areas "
             "to carry a specific tidal flood barrier disclosure (Land Development Regulations Sec. 7.1.7; "
             "Ordinance 23-21). See the <a href=\"/delray-beach/seawall-height-requirement/\">Delray Beach "
             "page</a>."),
            ("Pull the permit history",
             "If you do not have the permits, the city does. Use our "
             "<a href=\"/free/templates/public-records-request-permit-history/\">public records request</a>."),
            ("Give the elevation with its datum",
             "A cap height without the datum and the survey it came from cannot be checked. Quote it as the "
             "survey gives it; do not convert between datums yourself."),
        ],
        body="""
<h3>The wall</h3>
<ul class="tpl-check">
  <li>Type and material of the wall: ______________________________</li>
  <li>Year built: ______________ How you know (permit, survey, previous owner): ______________________</li>
  <li>Length of the wall along your property: ______________ feet</li>
  <li>Shared with or joined to a neighbour's wall: yes / no. Details: ______________________________</li>
</ul>

<h3>Permits</h3>
<ul class="tpl-check">
  <li>Permit number ______________ issued ______________ for ______________________
      &middot; closed / open / expired</li>
  <li>Permit number ______________ issued ______________ for ______________________
      &middot; closed / open / expired</li>
  <li>Permit number ______________ issued ______________ for ______________________
      &middot; closed / open / expired</li>
  <li>Final inspection or completion records on file: yes / no</li>
  <li>Permit history requested from the city on ______________; received on ______________</li>
</ul>

<h3>Cap elevation</h3>
<ul class="tpl-check">
  <li>Top of cap: ______________ feet, datum: NAVD88 / NGVD29 / other ______________</li>
  <li>From survey dated ______________ by ______________________, licence number ______________</li>
  <li>Your city's current requirement, from our <a href="/tools/seawall-height-lookup/">height lookup</a>
      or your building department: ______________________</li>
</ul>

<h3>Repairs and work done</h3>
<ul class="tpl-check">
  <li>Date ______________ Work ______________________ Contractor ______________________
      Invoice kept: yes / no</li>
  <li>Date ______________ Work ______________________ Contractor ______________________
      Invoice kept: yes / no</li>
  <li>Engineering reports or inspections, with dates: ______________________________</li>
  <li>Lien releases received for paid work: yes / no / not sure</li>
</ul>

<h3>Notices and claims</h3>
<ul class="tpl-check">
  <li>Any code notice, violation or hearing about the wall: yes / no.
      Case number ______________ Status ______________</li>
  <li>Closing or compliance letter received: yes / no, dated ______________</li>
  <li>Insurance claims for storm or flood damage to the wall: ______________________________</li>
  <li>Agreements with neighbours about a shared wall: ______________________________</li>
</ul>

<h3>Where it is all kept</h3>
<ul class="tpl-check">
  <li>Folder or file location: ______________________________</li>
  <li>Copies given to the listing agent on: ______________</li>
</ul>
""",
    ),

    # ---------------------------------------------------------------- (d)
    dict(
        slug="neighbor-shared-seawall-letter",
        kind="Letter",
        title="Letter to a neighbour about a shared seawall",
        seo_title="Letter to a Neighbor About a Shared Seawall (Free)",
        desc=("A friendly, factual letter to the owner next door about a shared seawall: what you "
              "saw, the photos, and a proposal for one joint inspection."),
        intro=("Seawalls on adjoining lots tend to share their problems: where one is failing, water and "
               "soil can move behind the next. The first letter sets the tone for everything after it, so "
               "this one stays friendly and sticks to what you have seen. It proposes one step only, a joint "
               "inspection, and asks nobody to commit to a repair."),
        offer="warning_list",
        cluster="failing-seawall",
        before=[
            ("Describe, do not diagnose",
             "Say what you saw and where. Leave the cause to the inspector, and do not assign blame."),
            ("Date your photos",
             "Take them at the same spot at high and low tide if you can, and say when each was taken."),
            ("Why it can matter beyond the two of you",
             "Some cities treat tidal water crossing onto a neighbour's property as a code problem. Delray "
             "Beach and Deerfield Beach are two whose rules we have published: see "
             "<a href=\"/delray-beach/seawall-permit/\">Delray Beach</a> and "
             "<a href=\"/deerfield-beach/seawall-height-requirement/\">Deerfield Beach</a>."),
            ("Know what to look for",
             "Our <a href=\"/resources/failing-seawall/\">failing seawall guide</a> lists the signs worth "
             "photographing."),
        ],
        body="""
<p class="tpl-meta">Date: ______________________</p>

<p>Dear ______________________,</p>

<p>I am ______________________, your neighbour at ______________________________.
I am writing about the seawall along our properties, where ______________________________
(for example: our walls meet, or the wall runs across both lots).</p>

<h3>What I have noticed</h3>
<p>On ______________ I noticed ________________________________________ at
______________________________ (where along the wall). I have enclosed ______ photographs,
taken on ______________________.</p>
<p>I do not know the cause, and I am not suggesting either of us is at fault. I am raising it now
because problems on one section of a wall can affect the section next to it, and they are usually
simpler to deal with early.</p>

<h3>What I am proposing</h3>
<p>Would you be willing to have one licensed marine contractor or engineer look at both sections
during the same visit, and share the written findings with both of us? I would suggest splitting the
cost of that inspection ______________ / ______________. This is only about finding out where things
stand. I am not asking either of us to commit to any repair.</p>
<p>If you already have a recent inspection, survey or permit for your section, I would be grateful
for a copy, and I am happy to share mine.</p>

<h3>Next step</h3>
<p>Could you let me know by ______________ whether this works for you? You can reach me at
______________________ (phone) or ______________________________ (email), or knock on my door.</p>

<p>Thank you, and kind regards,</p>
<p class="tpl-sign">______________________________<br>
______________________________ (address)</p>

<p class="tpl-meta">Enclosures: ______ photographs dated ______________________</p>
""",
    ),

    # ---------------------------------------------------------------- (e)
    dict(
        slug="public-records-request-permit-history",
        kind="Letter",
        title="Public records request for seawall permit history",
        seo_title="Public Records Request for Seawall Permits (Florida)",
        desc=("Ask a Florida building department for every seawall, dock and marine permit on a "
              "property, under Chapter 119, Florida Statutes."),
        intro=("Before you buy, sell, or answer a notice, you need the wall's permit history: what was "
               "permitted, when, and whether each permit closed. In Florida these are public records. "
               "Under s. 119.01(1), Florida Statutes, “all state, county, and municipal records are open "
               "for personal inspection and copying by any person.” This letter asks for everything "
               "relevant in one request."),
        offer="county_guide",
        cluster="buying-and-selling",
        before=[
            ("What the law says about access",
             "Under s. 119.07(1)(a), Florida Statutes, the custodian of a public record must permit it to be "
             "inspected and copied by any person, at any reasonable time, under reasonable conditions."),
            ("What it can cost",
             "Under s. 119.07(4), the custodian may charge up to 15 cents per one-sided copy, and a "
             "reasonable special service charge where a request needs extensive use of information "
             "technology or extensive clerical or supervisory help. Asking for electronic copies and a "
             "cost estimate first avoids surprises."),
            ("Send a second copy to the county where it applies",
             "City permits are not the whole record. In Miami-Dade, for example, county environmental "
             "permitting runs on top of the city permit; see the "
             "<a href=\"/miami-dade/seawalls/\">Miami-Dade page</a>. Address a copy of this request to "
             "that agency too."),
            ("Search first",
             "Many building departments have an online permit search. It is a quick first look, but often "
             "incomplete for older permits, which is when this request earns its keep."),
        ],
        sources=[S_11901, S_11907],
        body="""
<p class="tpl-meta">Date: ______________________</p>
<p class="tpl-meta">To: Records Custodian, Building Department, City of ______________________<br>
Address: ____________________________________________<br>
Email: ______________________________</p>
<p class="tpl-meta"><b>Re:</b> Public records request, Chapter 119, Florida Statutes<br>
Property address: ____________________________________________<br>
Folio or parcel number: ______________________</p>

<p>Dear Records Custodian,</p>

<p>Under Chapter 119, Florida Statutes, I request copies of the following public records for the
property above, for the period from ______________ to the present:</p>
<ol>
  <li>All permits, permit applications and permit cards for seawalls, bulkheads, docks, piers, boat
      lifts, riprap, waterfront decks and any other marine or shoreline structure.</li>
  <li>Inspection records for those permits, including final inspections, certificates of completion
      and any record of a permit being closed, expired, cancelled or still open.</li>
  <li>Plans, engineering drawings, surveys and elevation certificates submitted with those
      applications.</li>
  <li>Any code enforcement case, notice of violation, hearing record or lien relating to the
      property's seawall or shoreline.</li>
  <li>Correspondence between the city and the owner, or the owner's contractor or engineer, about
      the above.</li>
</ol>

<p>I would prefer electronic copies by email. If the cost of fulfilling this request will be more
than ______________ dollars, please tell me the estimated amount before you proceed.</p>

<p>If any record or part of a record is withheld, please tell me which one and the statutory
exemption you are relying on, and provide the rest.</p>

<p>Please confirm you have received this request. I can be reached at ______________________
(phone) or ______________________________ (email).</p>

<p>Thank you,</p>
<p class="tpl-sign">______________________________<br>
Printed name: ______________________________<br>
Mailing address: ______________________________</p>
""",
    ),
]


# ====================================================================== glossary
# Each entry: slug, term, short (one line for cards), body (60-150 words, HTML
# allowed for internal links), sources [(label, url)], related [(label, path)].
# Engineering terms with no figure and no legal statement carry no source;
# anything that states a number or what the law requires carries its section.

GLOSSARY = [
    dict(slug="navd88", term="NAVD88",
         short="The vertical datum most South Florida cities now use to state a seawall height.",
         body="""<p>The North American Vertical Datum of 1988: the reference surface most South Florida
cities use when they set a seawall height. When a code says 5 ft NAVD88, it means five feet above that
datum, not five feet above the water you can see. NOAA's National Geodetic Survey describes NAVD88 as
still the official vertical datum of the National Spatial Reference System, and plans to replace it
with a new gravity-based datum; heights will change when that happens, so always note which datum a
survey uses. NAVD88 is not mean sea level and it is not mean low water, so a height stated in one is a
different number in the other. A licensed surveyor can give you your cap elevation in NAVD88.</p>""",
         sources=[S_NGS_NEW, S_COOPS],
         related=[("Seawall height by county", "/seawall-height-by-county/"),
                  ("Seawall height lookup", "/tools/seawall-height-lookup/"),
                  ("Miami Beach height rule", "/miami-beach/seawall-height-requirement/")],
         see=["ngvd29", "datum"]),

    dict(slug="ngvd29", term="NGVD29",
         short="The older vertical datum still found on old surveys, permits and flood maps.",
         body="""<p>The National Geodetic Vertical Datum of 1929, an older reference surface that NOAA lists
as a synonym for the Sea-level Datum of 1929. NOAA states that NGVD29 is no longer supported by the
National Geodetic Survey, and that it should not be read as mean sea level. Older surveys, permits and
elevation documents in South Florida often give heights in NGVD29. The difference between an NGVD29
height and an NAVD88 height for the same point is not one fixed number; the relationship between datums
varies by location, and NOAA points to its VDatum tool for conversions. If an old document gives your cap
height in NGVD29, record it exactly as given and ask a surveyor for the current figure in NAVD88.</p>""",
         sources=[S_COOPS],
         related=[("How we handle datums", "/how-we-verify/"),
                  ("Seller's seawall checklist", "/free/templates/seller-seawall-checklist/")],
         see=["navd88", "datum"]),

    dict(slug="datum", term="Datum",
         short="The zero point a height is measured from. A seawall height means nothing without one.",
         body="""<p>The zero point a height is measured from. A seawall height is meaningless without it:
five feet above mean low water and five feet NAVD88 are different elevations. Some datums are geodetic,
like NAVD88, tied to a national network of survey marks. Others are tidal, defined by the tide itself.
NOAA defines mean low water as the average of all the low water heights observed over the National
Tidal Datum Epoch, a specific 19-year period. South Florida codes use several. Most cities we have
verified state their rule in NAVD88, <a href="/surfside/seawall-height-requirement/">Surfside</a>
states mean low water, and <a href="/key-colony-beach/seawall-height-requirement/">Key Colony Beach</a>
states mean sea level. We publish each as written and do not convert between them.</p>""",
         sources=[S_COOPS],
         related=[("How we verify", "/how-we-verify/"),
                  ("Seawall height by county", "/seawall-height-by-county/")],
         see=["navd88", "ngvd29"]),

    dict(slug="seawall-cap", term="Seawall cap",
         short="The concrete beam along the top of a seawall, and usually the part a height rule measures.",
         body="""<p>The concrete beam poured along the top of a seawall. It ties the panels or sheet piles
together, spreads load along the wall, and is what most people mean by the top of the wall, so on most
walls it is the cap elevation that gets checked against a height rule. Caps are often where damage shows
first: cracks, spalling, and rust staining where the reinforcing steel inside has started to corrode.
Raising a wall to a new required height is often done by rebuilding the cap higher, if the wall below
can carry it, which is an engineer's call. Some cities regulate the cap itself.
<a href="/deerfield-beach/seawall-height-requirement/">Deerfield Beach</a> sets a minimum and maximum
cap width, and <a href="/pompano-beach/seawall-height-requirement/">Pompano Beach</a> limits how far a
cap may project seaward.</p>""",
         sources=[],
         related=[("Signs a seawall is failing", "/resources/failing-seawall/"),
                  ("What moves the cost", "/resources/what-it-costs/")],
         see=["tie-back-anchor", "sheet-pile"]),

    dict(slug="tie-back-anchor", term="Tie-back anchor",
         short="A rod or cable from the back of the wall into the ground, holding the wall upright.",
         body="""<p>A rod or cable running from the back of a seawall into the ground behind it, holding
the wall against the push of soil and water on the land side. At the wall end it connects to the cap
or a horizontal beam; at the far end it is fastened to something that resists being pulled, such as a
<a href="/glossary/deadman-anchor/">deadman</a>, a buried anchor or a pile. Anchors corrode out of sight,
and a failed one often shows up as a wall leaning toward the water or a cap that has rotated. A quote
that includes new or replacement anchors should say how many, at what spacing, of what material, and the
unit price for any extra anchors found to be needed once work starts.</p>""",
         sources=[],
         related=[("Quote comparison worksheet", "/free/templates/contractor-quote-comparison/"),
                  ("Signs a seawall is failing", "/resources/failing-seawall/")],
         see=["deadman-anchor", "seawall-cap"]),

    dict(slug="deadman-anchor", term="Deadman anchor",
         short="A buried block behind the wall that a tie-back rod pulls against.",
         body="""<p>A buried block, usually concrete, set some distance behind a seawall, that a
<a href="/glossary/tie-back-anchor/">tie-back</a> rod is fastened to. It works through the soil in front
of it: as the wall tries to lean out, the rod pulls on the deadman and the soil resists. Because it sits
under the yard, installing or replacing one often means digging up lawn, pavers, irrigation or part of a
pool deck. That restoration is frequently listed as work by others in marine quotes, so it can fall to the
owner. Before you sign, ask in writing who puts the yard back, and to what standard.</p>""",
         sources=[],
         related=[("What no quote includes", "/resources/what-it-costs/"),
                  ("Quote comparison worksheet", "/free/templates/contractor-quote-comparison/")],
         see=["tie-back-anchor"]),

    dict(slug="weep-hole", term="Weep hole",
         short="A drainage opening low in the wall that lets trapped water out as the tide falls.",
         body="""<p>An opening through a seawall, set low on the face, that lets water trapped behind the
wall drain out as the tide falls. Without drainage, water pressure builds on the land side and pushes
on the wall. Weep holes are normally backed with <a href="/glossary/filter-fabric/">filter fabric</a> or
a gravel filter so that water passes and soil does not. A weep hole running muddy water, or a sinkhole
forming behind the wall, can mean soil is escaping through it. A blocked weep hole is a problem too,
because the pressure it was there to relieve has nowhere to go. Both are worth photographing and showing
to whoever inspects the wall.</p>""",
         sources=[],
         related=[("Signs a seawall is failing", "/resources/failing-seawall/"),
                  ("Twelve warning signs (PDF)", "/downloads/seawall-warning-signs-checklist.pdf")],
         see=["filter-fabric"]),

    dict(slug="filter-fabric", term="Filter fabric",
         short="Geotextile behind the wall that lets water through and keeps soil in.",
         body="""<p>A geotextile placed behind a seawall, across the joints between panels and behind
<a href="/glossary/weep-hole/">weep holes</a>, that lets water through while holding soil back. It is what
stops the yard washing out through the wall. When the fabric tears or breaks down, soil can be carried
through the gaps on every tide, and the first visible sign is often a depression or sinkhole behind the
cap rather than anything on the face of the wall. Replacing fabric means excavating behind the wall, so
a quote should say whether it is included, along what length, and who restores the ground afterwards.</p>""",
         sources=[],
         related=[("Signs a seawall is failing", "/resources/failing-seawall/"),
                  ("Quote comparison worksheet", "/free/templates/contractor-quote-comparison/")],
         see=["weep-hole"]),

    dict(slug="sheet-pile", term="Sheet pile",
         short="Interlocking panels driven into the ground to form the wall itself.",
         body="""<p>Interlocking panels driven vertically into the ground to form a wall. Seawall sheet
piles may be concrete, steel, vinyl, aluminium or composite. They are driven deep enough that the buried
part, together with the anchors, resists the load on the exposed part, so pile length follows from water
depth and soil, and a geotechnical recommendation can change the design. Driving a new wall just in front
of an old one is a common way to replace it without removal. Florida's permit exemption for restoring a
seawall covers its previous location, upland of it, or within 18 inches waterward of it, under
s. 403.813(1)(e), Florida Statutes. Your city's permit still applies.</p>""",
         sources=[S_403813],
         related=[("Three ways to fix one wall", "/resources/what-it-costs/"),
                  ("Environmental Resource Permit", "/glossary/environmental-resource-permit/")],
         see=["seawall-cap", "tie-back-anchor"]),

    dict(slug="riprap", term="Riprap",
         short="Loose rock at the base of a seawall that absorbs wave energy and protects the toe.",
         body="""<p>Loose rock placed at the base of a seawall on the water side. It breaks up wave energy,
protects the toe of the wall from being scoured out, and gives marine life somewhere to settle. Some
cities require it. <a href="/pompano-beach/seawall-height-requirement/">Pompano Beach</a> requires natural
limestone riprap at the waterward face, and <a href="/deerfield-beach/seawall-height-requirement/">Deerfield
Beach</a> requires natural limerock riprap or approved habitat enhancement there, with rules on how it is
placed. Moving or replacing riprap during a seawall job is often the owner's cost rather than the
contractor's, so check whether each quote includes it.</p>""",
         sources=[("City of Pompano Beach Code of Ordinances § 151.05", ""),
                  ("City of Deerfield Beach Land Development Code Sec. 98-87(d)(4)b", "")],
         related=[("Quote comparison worksheet", "/free/templates/contractor-quote-comparison/"),
                  ("What no quote includes", "/resources/what-it-costs/")],
         see=["living-shoreline", "sheet-pile"]),

    dict(slug="tidal-flood-barrier", term="Tidal flood barrier",
         short="The broader term Broward codes use: a seawall, or anything else doing the same job.",
         body="""<p>The term Broward County and its cities use for a seawall or any other structure or
feature that keeps tidal water off the land behind it. The wider word matters because the elevation
standard attaches to the barrier, not only to a wall. <a href="/pompano-beach/seawall-height-requirement/">Pompano
Beach</a>, for example, does not require a seawall where another measure is an equally effective tidal
flood barrier. Broward's standard is set in Broward County Code Sec. 39-404, Art. XXV, and the county's
cities adopted it in their own codes, some with stricter terms. The <a href="/broward/seawalls/">Broward
page</a> sets out the county figure and which cities depart from it.</p>""",
         sources=[("Broward County Code Sec. 39-404, Art. XXV", ""),
                  ("City of Pompano Beach Code of Ordinances § 151.05", "")],
         related=[("Broward seawall rules", "/broward/seawalls/"),
                  ("Fort Lauderdale height rule", "/fort-lauderdale/seawall-height-requirement/"),
                  ("Hollywood height rule", "/hollywood/seawall-height-requirement/")],
         see=["navd88", "king-tide"]),

    dict(slug="king-tide", term="King tide",
         short="An everyday name for exceptionally high tides, not a scientific term.",
         body="""<p>NOAA describes a king tide as a non-scientific term people often use for exceptionally
high tides. They come when the Moon is new or full and also at its closest point to the Earth. For a
waterfront owner, a king tide is the day a wall's height is tested without a storm: water over the cap,
through gaps between panels, or up behind the wall. Photograph the water level against your cap, with the
date and time, from the same spot each time. Those photographs are useful evidence for a permit
application, an insurance conversation or a <a href="/free/templates/neighbor-shared-seawall-letter/">letter
to a neighbour</a>.</p>""",
         sources=[S_KING],
         related=[("Seawall height lookup", "/tools/seawall-height-lookup/"),
                  ("Signs a seawall is failing", "/resources/failing-seawall/")],
         see=["tidal-flood-barrier", "datum"]),

    dict(slug="base-flood-elevation", term="Base flood elevation (BFE)",
         short="How high floodwater is expected to reach in the 1-percent-annual-chance flood.",
         body="""<p>The height floodwater is expected to reach in the base flood, which federal flood rules
define as the flood having a one percent chance of being equalled or exceeded in any given year
(44 CFR 59.1). The BFE for a property is shown on its <a href="/glossary/flood-insurance-rate-map/">Flood
Insurance Rate Map</a>, stated against the datum the map names. It matters for seawalls because some
cities tie their limits to it. <a href="/fort-lauderdale/seawall-height-requirement/">Fort Lauderdale</a>
caps a wall at the base flood elevation or 6 ft NAVD88, whichever is lower, and
<a href="/delray-beach/seawall-height-requirement/">Delray Beach</a> sets its maximum by the property's
base flood elevation.</p>""",
         sources=[S_CFR591, S_MSC],
         related=[("Fort Lauderdale height rule", "/fort-lauderdale/seawall-height-requirement/"),
                  ("Delray Beach height rule", "/delray-beach/seawall-height-requirement/")],
         see=["flood-insurance-rate-map", "navd88"]),

    dict(slug="flood-insurance-rate-map", term="Flood Insurance Rate Map (FIRM)",
         short="FEMA's official flood map: where your flood zone and BFE come from.",
         body="""<p>The official map of a community on which FEMA has delineated both the special flood
hazard areas and the insurance risk premium zones (44 CFR 59.1). It is where a property's flood zone and
<a href="/glossary/base-flood-elevation/">base flood elevation</a> come from. FEMA's Flood Map Service
Center is the official public source for these maps, and you can search it by address. Maps are revised
from time to time, so check the effective date on the map panel you are reading, and ask your city's
floodplain office which map it is applying to your permit.</p>""",
         sources=[S_CFR591, S_MSC],
         related=[("Seawall rules by city", "/resources/seawall-compliance/"),
                  ("Fort Lauderdale height rule", "/fort-lauderdale/seawall-height-requirement/")],
         see=["base-flood-elevation"]),

    dict(slug="substantial-improvement", term="Substantial improvement and substantial repair",
         short="The threshold that pulls the whole wall, not just the repair, up to the current rule.",
         body="""<p>Federal flood rules define substantial improvement as work on a structure whose cost
equals or exceeds 50 percent of its market value before construction starts, and substantial damage as
damage that would cost that much to restore (44 CFR 59.1). Those definitions are written for buildings.
Cities set their own tests for seawalls, and they differ:
<a href="/miami-beach/seawall-height-requirement/">Miami Beach</a> measures repair cost per linear foot,
while <a href="/delray-beach/seawall-permit/">Delray Beach</a> looks at how much of the wall's length is
being worked on. The consequence is similar. In Delray Beach, Pompano Beach, Deerfield Beach and Miami,
crossing the threshold means the property's whole shoreline must meet the current standard, not only the
section being repaired.</p>""",
         sources=[S_CFR591],
         related=[("Pompano Beach height rule", "/pompano-beach/seawall-height-requirement/"),
                  ("Miami height rule", "/miami/seawall-height-requirement/"),
                  ("Deerfield Beach height rule", "/deerfield-beach/seawall-height-requirement/")],
         see=["base-flood-elevation", "seawall-cap"]),

    dict(slug="notice-of-commencement", term="Notice of Commencement",
         short="The form an owner records and posts before work starts, under s. 713.13.",
         body="""<p>A form the owner signs, records in the county clerk's office and posts at the job site
before work starts, under s. 713.13, Florida Statutes. It names the property, owner, contractor, any
surety and lender, and gives notice that claims of lien may be recorded. The statutory form warns that it
must be recorded and posted before the first inspection. It is void if work does not begin within 90 days
of recording, and it expires one year after recording unless it states a different date. Payments made
after it expires are treated as improper payments, which can mean paying twice. Improvements with a
direct contract price of $2,500 or less are exempt (s. 713.02(5)).</p>""",
         sources=[S_71313, S_71302],
         related=[("Notice to Owner", "/glossary/notice-to-owner/"),
                  ("Quote comparison worksheet", "/free/templates/contractor-quote-comparison/")],
         see=["notice-to-owner", "release-of-lien"]),

    dict(slug="notice-to-owner", term="Notice to Owner",
         short="A subcontractor's or supplier's notice that protects their right to a lien.",
         body="""<p>A notice that a subcontractor or supplier who has no contract with you directly must
serve on you to protect their right to claim a lien on your property. Under s. 713.06, Florida Statutes,
it must be served before they start, or within 45 days of starting, to furnish labour, services or
materials, and before your final payment to the contractor. Receiving one on a seawall job is routine;
it is not an accusation. Its statutory warning is the part to read: if your contractor does not pay them,
there may be a lien against your property and you could pay twice. The protection it names is a written
<a href="/glossary/release-of-lien/">release</a> from them every time you pay your contractor.</p>""",
         sources=[S_71306],
         related=[("Notice of Commencement", "/glossary/notice-of-commencement/"),
                  ("Quote comparison worksheet", "/free/templates/contractor-quote-comparison/")],
         see=["release-of-lien", "notice-of-commencement"]),

    dict(slug="release-of-lien", term="Release of lien",
         short="A signed waiver of lien rights for work already paid for, on the statutory form.",
         body="""<p>A signed document in which a contractor, subcontractor or supplier gives up lien rights
for work covered by a payment. Section 713.20, Florida Statutes, sets out two forms: a waiver and release
upon progress payment, and one upon final payment. A lienor can be required to sign one in exchange for,
or to induce, a payment, and no one may require a waiver in a different form. A right to a lien may not
be waived in advance, so a release covers money paid, not future work. A lienor may make the release
conditional on the check clearing. Collect one from each party who sent you a
<a href="/glossary/notice-to-owner/">Notice to Owner</a>, with every payment.</p>""",
         sources=[S_71320],
         related=[("Seller's seawall checklist", "/free/templates/seller-seawall-checklist/"),
                  ("Quote comparison worksheet", "/free/templates/contractor-quote-comparison/")],
         see=["notice-to-owner", "notice-of-commencement"]),

    dict(slug="sovereign-submerged-lands", term="Sovereign submerged lands",
         short="State-owned land under navigable water, which needs state consent to build on.",
         body="""<p>Land under navigable water that belongs to the State of Florida. Under s. 253.12(1),
Florida Statutes, title to sovereignty tidal and submerged bottom lands is vested in the Board of
Trustees of the Internal Improvement Trust Fund. Section 253.77(1) says a person may not start
construction or other activity involving the use of state lands until they have received the required
lease, license, easement or other form of consent. That is why a dock reaching out over the water can
need state consent in addition to a permit, and the permit exemptions in s. 403.813 do not remove that
need. Whether the bottom in front of a particular lot is sovereign land is a question to raise with the
reviewing agency early.</p>""",
         sources=[S_25312, S_25377, S_403813],
         related=[("Environmental Resource Permit", "/glossary/environmental-resource-permit/"),
                  ("Dock and lift rules", "/resources/docks-and-lifts/")],
         see=["environmental-resource-permit", "benthic-survey"]),

    dict(slug="environmental-resource-permit", term="Environmental Resource Permit (ERP)",
         short="Florida's permit for work in, on or over wetlands and other surface waters.",
         body="""<p>Florida's permit for activities that alter surface water flows or involve dredging and
filling in wetlands and other surface waters, issued under Part IV of Chapter 373, Florida Statutes. The
Florida Department of Environmental Protection says applications go to one of its district offices or
to a water management district, and that DEP generally handles docking facilities that are not part
of a larger residential or commercial development, and systems serving a single-family home. Some work is exempt under s. 403.813(1), including restoring a seawall at
its previous location, upland of it, or within 18 inches waterward of it, and repairing or replacing a
dock within 5 feet of the same location with no increase in size. An exemption does not remove the need
for state consent to use <a href="/glossary/sovereign-submerged-lands/">sovereign submerged lands</a>.</p>""",
         sources=[S_FDEP_ERP, S_403813],
         related=[("Docks and lifts", "/resources/docks-and-lifts/"),
                  ("Miami-Dade seawall rules", "/miami-dade/seawalls/")],
         see=["sovereign-submerged-lands", "benthic-survey"]),

    dict(slug="living-shoreline", term="Living shoreline",
         short="A shoreline stabilised with natural materials such as plants, sand or rock.",
         body="""<p>NOAA defines a living shoreline as a protected and stabilised shoreline made of natural
materials such as plants, sand or rock, offered as an alternative to hard methods like riprap or
bulkheads. In practice it might be a planted slope with a rock sill offshore, rather than a vertical wall.
Some cities fold living shorelines into the same elevation rule as seawalls: the
<a href="/miami/seawall-height-requirement/">City of Miami</a> standard east of US-1 covers new seawalls,
bulkheads and living shorelines alike. Whether one suits your lot depends on wave exposure, water depth,
and what your city and the agencies will permit.</p>""",
         sources=[S_LIVING],
         related=[("Miami height rule", "/miami/seawall-height-requirement/"),
                  ("Seawall rules by city", "/resources/seawall-compliance/")],
         see=["riprap", "tidal-flood-barrier"]),

    dict(slug="benthic-survey", term="Benthic survey",
         short="A survey of what lives on the bottom where in-water work is planned.",
         body="""<p>A survey of the bottom where in-water work is proposed, recording what lives there, such
as seagrass, coral or hardbottom, and where it is. Reviewers use it to judge whether a dock, seawall or
riprap can go where it is drawn, or has to move, shrink, or be paired with mitigation. Whether you need
one depends on the site and on the agencies reviewing the work, so ask at the start of permitting rather
than finding out partway through. It is commonly supplied and paid for by the owner rather than included
in a contractor's price, so check how each of your quotes treats it.</p>""",
         sources=[],
         related=[("What no quote includes", "/resources/what-it-costs/"),
                  ("Quote comparison worksheet", "/free/templates/contractor-quote-comparison/")],
         see=["environmental-resource-permit", "sovereign-submerged-lands"]),
]
