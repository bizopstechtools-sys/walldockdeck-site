#!/usr/bin/env python3
"""Refuse to ship a page carrying confidential deal information.

Runs at the end of every build. If it finds anything here in a generated page,
the build fails and nothing gets committed. This exists because a previous build
put client street addresses and exact signed-contract totals on public pages.

Add to BANNED whenever a new source document is read. Never relax it.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Exact contract totals from signed proposals. Published figures must be rounded.
BANNED_FIGURES = ["468,675", "720,250", "140,099", "124,450", "350,250",
                  "98,675", "251,575", "694,750", "428,975", "12.40"]

# Street addresses and anything naming a party to a deal.
BANNED_STRINGS = [
    "1501 SE 14th", "930 Lugo", "Orchid Bay", "7400 NE 8th", "7400 NE Orchid",
    "Hunter Barrett", "Philippe Bibi", "Vona", "Castle Marine", "Atlantic Harbor",
    "Giordano", "same contractor", "signed contract", "the contractor's proposal",
]

# A street address in any page is a bug, whatever the name — with one exception:
# our own registered address, which belongs on the privacy page. Anything else
# matching this shape is a customer's property and must not ship.
ADDRESS_RE = re.compile(r"\b\d{2,5}\s+(?:N|S|E|W|NE|NW|SE|SW)\.?\s+\w+", re.I)

OWN_ADDRESS = [
    "16300 SW 137th Avenue",
    "16300 SW 137 Ave",
]

def pages():
    for d, dirs, fs in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in ("_build", "_preview", ".git", "guides", "scripts")]
        for f in fs:
            if f.endswith(".html") and d != ROOT:      # skip the untouched prototype
                yield os.path.join(d, f)

def main():
    problems = []
    for p in pages():
        text = open(p, encoding="utf8").read()
        rel = os.path.relpath(p, ROOT)
        for bad in BANNED_FIGURES + BANNED_STRINGS:
            if bad.lower() in text.lower():
                problems.append(f"{rel}: contains {bad!r}")
        for m in ADDRESS_RE.finditer(text):
            around = text[max(0, m.start() - 10): m.end() + 40]
            if any(own.lower() in around.lower() for own in OWN_ADDRESS):
                continue          # our own address, on our own page
            problems.append(f"{rel}: looks like a street address — {m.group(0)!r}")

    if problems:
        print("\nBUILD BLOCKED — confidential deal information in generated pages:\n")
        for x in sorted(set(problems)):
            print("  " + x)
        print(f"\n{len(set(problems))} problem(s). Nothing ships until these are gone.\n")
        sys.exit(1)

    print(f"guard              ok   {sum(1 for _ in pages())} pages clean")

if __name__ == "__main__":
    main()
