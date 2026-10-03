"""Build the four county guides from _build/guides-src/*.md.

The source is pdftotext output from the September PDFs, so table structure has to be
recovered heuristically: a short label block followed by a prose block is a row.
Everything is preserved -- when the heuristic is unsure it emits a paragraph rather
than inventing structure, because losing a fact is worse than losing a table border.
"""
import html, os, re, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_build", "guides-src")
OUT = os.path.join(ROOT, "guides")
os.makedirs(OUT, exist_ok=True)
TODAY = "October 2026"

TITLES = {
    "broward": ("Broward", "Broward County"),
    "miami": ("Miami-Dade", "Miami-Dade County"),
    "palm": ("Palm Beach", "Palm Beach County"),
    "keys": ("Florida Keys", "Monroe County"),
}


def e(s):
    return html.escape(str(s or ""))


MARK = ('<svg viewBox="0 0 34 34" width="30" height="30"><rect width="34" height="34" rx="7" fill="#0B2536"/>'
        '<rect x="7" y="8" width="5" height="18" rx="1" fill="#7FC6CF"/>'
        '<rect x="14.5" y="14" width="12.5" height="3.5" rx="1" fill="#fff"/>'
        '<rect x="14.5" y="20" width="12.5" height="3.5" rx="1" fill="#E0701A"/>'
        '<path d="M5 28.5c3-1.6 6-1.6 9 0s6 1.6 9 0 6-1.6 7 0" stroke="#7FC6CF" stroke-width="1.6" fill="none"/>'
        '</svg>')

CSS = """
@page { size: Letter; margin: 18mm 16mm 20mm; }
@page :first { margin: 0; }
*{box-sizing:border-box}
body{margin:0;font-family:"Source Sans 3",Helvetica,Arial,sans-serif;color:#10283A;
     font-size:10.4pt;line-height:1.56;-webkit-print-color-adjust:exact;print-color-adjust:exact}
h1,h2,h3{font-family:"Archivo",Arial,sans-serif;font-stretch:86%;margin:0;line-height:1.12;
     letter-spacing:-.015em}

/* ---------- cover ---------- */
.cover{height:279.4mm;display:flex;flex-direction:column;page-break-after:always}
.cover .top{background:#0B2536;color:#E8F1F5;padding:16mm 18mm 14mm;border-bottom:3pt solid #E0701A}
.brand{display:flex;align-items:center;gap:9pt;margin-bottom:14mm}
.brand b{font-family:"Archivo",sans-serif;font-stretch:80%;font-weight:800;font-size:17pt;color:#fff}
.brand b i{font-style:normal;color:#7FC6CF}
.brand .tag{font-family:"IBM Plex Mono",monospace;font-size:7pt;letter-spacing:.18em;
     text-transform:uppercase;color:#7FC6CF;border-left:1px solid #2F5266;padding-left:10pt;margin-left:5pt}
.cover h1{font-size:40pt;font-weight:800;color:#fff;max-width:150mm}
.cover .kicker{font-family:"IBM Plex Mono",monospace;font-size:8pt;letter-spacing:.2em;
     text-transform:uppercase;color:#7FC6CF;margin-bottom:5mm}
.cover .scope{font-size:12pt;color:#9FB7C4;margin-top:8mm;max-width:132mm}
.cover .mid{padding:14mm 18mm;flex:1}
.cover .inc{font-family:"IBM Plex Mono",monospace;font-size:8.4pt;letter-spacing:.12em;
     text-transform:uppercase;color:#0B5A66;background:#E0EFF1;display:inline-block;
     padding:5pt 11pt;border-radius:5pt}
.cover .note{margin-top:10mm;font-size:9.6pt;color:#41586A;max-width:140mm}
.cover .foot{background:#F4F7F8;border-top:2pt solid #E0701A;padding:7mm 18mm;
     font-size:8.2pt;color:#6E8492;display:flex;justify-content:space-between}
.cover .foot b{color:#0B2536}

/* ---------- body ---------- */
h2{font-size:17pt;font-weight:800;color:#0B2536;margin:0 0 5mm;padding-bottom:3mm;
   border-bottom:2pt solid #0F7482;page-break-after:avoid;page-break-before:always}
h2:first-of-type{page-break-before:avoid}
h3{font-size:12.2pt;font-weight:700;color:#0B2536;margin:7mm 0 2.5mm;page-break-after:avoid}
p{margin:0 0 3.6mm;max-width:172mm}
table{width:100%;border-collapse:collapse;margin:0 0 6mm}
td{padding:5.5pt 8pt;border-bottom:1px solid #EAF0F2;vertical-align:top;font-size:9.8pt}
td.k{font-family:"IBM Plex Mono",monospace;font-size:7.8pt;letter-spacing:.07em;
     text-transform:uppercase;color:#0B5A66;width:46mm;background:#FAFCFC}
ul{margin:0 0 5mm;padding-left:0;list-style:none}
ul li{position:relative;padding-left:7mm;margin-bottom:2mm;font-size:9.9pt}
ul li::before{content:"";position:absolute;left:1.5mm;top:2.4mm;width:2.2mm;height:2.2mm;
     border-radius:50%;background:#0F7482}
.src{background:#F4F7F8;border-left:2.5pt solid #0F7482;padding:4.5mm 6mm;font-size:9.1pt;
     color:#41586A;margin:0 0 6mm;page-break-inside:avoid}
tr,li{page-break-inside:avoid}
.numi{font-weight:600;color:#0B2536;margin:5mm 0 1.5mm}
"""

HEAD = ('<!DOCTYPE html><html><head><meta charset="utf-8">'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=Archivo:wdth,wght@75..100,400..800&family=Source+Sans+3:wght@400;600;700'
        '&family=IBM+Plex+Mono:wght@400;500&display=swap">'
        f'<style>{CSS}</style></head><body>')

RUNHDR = re.compile(r"^(?:[A-Z]\s){3,}")           # letter-spaced running header
ALLCAPS = re.compile(r"^[A-Z0-9 &'/().,·-]{2,44}$")
CHAPTER = re.compile(r"^(CHAPTER\b.*|START HERE|BEFORE YOU PAY)$")
NUMITEM = re.compile(r"^\d{1,2}\.\s+[A-Z]")
CITELINE = re.compile(r"(Code|Statute|Chapter|Section|Sec\.|Ordinance|Policy|Rule|Administrative Code|"
                      r"ULDR|ULDC|LDR|§)\s*[\w\.\-]", re.I)


def blocks(text):
    """Split into blank-line separated blocks, dropping running headers."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out, cur = [], []
    for raw in text.split("\n"):
        s = raw.strip()
        if RUNHDR.match(s) and s.upper() == s:
            continue
        if not s:
            if cur:
                out.append(cur)
                cur = []
            continue
        cur.append(s)
    if cur:
        out.append(cur)
    return out


def is_label(b):
    """A table label: one short line, no terminal full stop, not a citation."""
    if len(b) != 1:
        return False
    s = b[0]
    if NUMITEM.match(s):
        return False
    return (len(s) <= 46 and not s.endswith(".") and not CITELINE.search(s)
            and not CHAPTER.match(s) and not s.endswith(":"))


def is_heading(b):
    """A sub-heading: one line, sentence-like, no terminal full stop."""
    if len(b) != 1:
        return False
    s = b[0]
    return 8 <= len(s) <= 95 and not s.endswith(".") and not ALLCAPS.match(s)


def render(name):
    label, county = TITLES[name]
    text = open(os.path.join(SRC, f"{name}.md"), encoding="utf-8").read()
    bs = blocks(text)

    # ---- cover: everything before the first chapter marker
    start = next((i for i, b in enumerate(bs) if CHAPTER.match(b[0])), 0)
    # pdftotext hard-wraps the cover, so take the whole block, not the first line
    scope = inc = ""
    for b in bs[:start]:
        joined = " ".join(b)
        if "Written for" in joined and not scope:
            scope = joined[joined.index("Written for"):]
        if "Includes:" in joined and not inc:
            inc = next(l for l in b if "Includes:" in l)
    cover_src = [l for b in bs[:start] for l in b]
    subtitle = next((l for l in cover_src if "Boat Lift" in l or "Boat lift" in l),
                    "Seawalls · Docks & Boat Lifts · Waterfront Decks")
    body = bs[start:]

    cover = f'''<div class="cover">
  <div class="top">
    <div class="brand">{MARK}<b>Wall<i>Dock</i>Deck</b>
      <span class="tag">{e(label)} Edition</span></div>
    <div class="kicker">Waterfront Owner&rsquo;s Guide</div>
    <h1>{e(subtitle)}</h1>
    <div class="scope">{e(scope)}</div>
  </div>
  <div class="mid">
    {f'<span class="inc">{e(inc)}</span>' if inc else ''}
    <p class="note">Waterfront work is among the most expensive and most heavily permitted
    work you can buy for your home, and among the least transparent. This guide gives you the part nobody
    hands you: who has to approve the job, which paperwork protects your money, how to check
    a company in about ten minutes, and what to ask before you sign.</p>
    <p class="note"><b>Every local rule in this guide carries its code section, and the figures were
    checked against the primary sources in October 2026.</b> Rules change. Confirm with your building department before you rely on one.</p>
  </div>
</div>'''

    # ---- body
    out, i, n = [], 0, len(body)
    while i < n:
        b = body[i]
        first = b[0]

        if CHAPTER.match(first):
            out.append(f"<h2>{e(first.title() if first.isupper() else first)}</h2>")
            i += 1
            continue

        # a label/value run becomes a table
        if is_label(b) and i + 1 < n and not is_label(body[i + 1]) and not CHAPTER.match(body[i + 1][0]):
            rows = ""
            while (i < n and is_label(body[i]) and i + 1 < n
                   and not is_label(body[i + 1]) and not CHAPTER.match(body[i + 1][0])):
                k = body[i][0]
                v = " ".join(body[i + 1])
                rows += f'<tr><td class="k">{e(k)}</td><td>{e(v)}</td></tr>'
                i += 2
            out.append(f"<table>{rows}</table>")
            continue

        # a run of short lines with no terminal stop is a list
        if len(b) >= 3 and all(len(l) <= 110 and not l.endswith(".") for l in b):
            out.append("<ul>" + "".join(f"<li>{e(l)}</li>" for l in b) + "</ul>")
            i += 1
            continue

        if CITELINE.search(first) and len(" ".join(b)) < 400 and len(b) <= 3:
            txt = re.sub(r"^Source[:.]\s*", "", " ".join(b))
            out.append(f'<p class="src"><b>Source.</b> {e(txt)}</p>')
            i += 1
            continue

        if is_heading(b):
            out.append(f"<h3>{e(first)}</h3>")
            i += 1
            continue

        if ALLCAPS.match(first) and len(b) == 1:
            i += 1          # orphaned table column header from the old layout
            continue

        # pdftotext often runs a heading into the paragraph beneath it, and leaves the
        # old table's column header stranded at the end of a block. Split and strip.
        lines = list(b)
        head = ""
        if len(lines) > 1 and len(lines[0]) <= 95 and not lines[0].endswith(".") \
                and not ALLCAPS.match(lines[0]) and lines[1][:1].isupper() \
                and not NUMITEM.match(lines[0]):
            head = lines.pop(0)
        while lines and ALLCAPS.match(lines[-1]) and len(lines[-1]) <= 30:
            lines.pop()
        if head:
            out.append(f"<h3>{e(head)}</h3>")
        body_txt = " ".join(lines).strip()
        body_txt = re.sub(r"\s+(WHAT|LAYER|PROJECT|CITY|DOCUMENT|REQUIREMENT|SIZE|"
                          r"THE LIMIT|WHEN IT APPLIES|WHY YOU CARE|BEFORE YOU PAY)$", "", body_txt)
        if NUMITEM.match(body_txt):
            out.append(f"<p class=\"numi\">{e(body_txt)}</p>")
        elif body_txt:
            out.append(f"<p>{e(body_txt)}</p>")
        i += 1

    return HEAD + cover + "".join(out) + "</body></html>"


def main():
    names = sys.argv[1:] or list(TITLES)
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page()
        for name in names:
            doc = render(name)
            tmp = os.path.join(ROOT, "_build", f"_g_{name}.html")
            open(tmp, "w", encoding="utf8").write(doc)
            pg.goto("file://" + tmp)
            pg.wait_for_timeout(1400)
            out = os.path.join(OUT, f"{name}.pdf")
            pg.pdf(path=out, format="Letter", print_background=True,
                   display_header_footer=True,
                   header_template='<div></div>',
                   footer_template=(
                       '<div style="width:100%;font:7.6pt \'Helvetica\';color:#8aa0ad;'
                       'padding:0 16mm;display:flex;justify-content:space-between">'
                       '<span>WallDockDeck &middot; Edition ' + TODAY +
                       ' &middot; confirm current rules with your city before you sign</span>'
                       '<span class="pageNumber"></span></div>'),
                   margin={"top": "18mm", "bottom": "20mm", "left": "16mm", "right": "16mm"})
            print(f"  {name+'.pdf':20} {os.path.getsize(out)//1024:>4} KB")
            os.remove(tmp)
        br.close()


if __name__ == "__main__":
    main()
