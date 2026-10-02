#!/usr/bin/env python3
"""Refuse to ship a page carrying confidential deal information.

Runs at the end of every build. If it finds anything here in a generated page,
the build fails and nothing gets committed. This exists because a previous build
put client street addresses and exact signed-contract totals on public pages.

Add to _build/guard-banned.txt whenever a new source document is read.
Never relax it, and never commit that file.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The confidential list is NOT stored here. This file is committed to a public
# repo, and a ban list of secrets is still a list of secrets — an earlier version
# of this guard leaked exactly the data it exists to block, by carrying it.
#
# Entries live in _build/guard-banned.txt, which is gitignored.
BAN_FILE = os.path.join(ROOT, "_build", "guard-banned.txt")


def banned_terms():
    """Read the confidential list. Missing is survivable but must be loud —
    failing silently would leave the build unprotected and looking fine."""
    if not os.path.exists(BAN_FILE):
        print("guard            WARN   _build/guard-banned.txt is missing — name and\n"
              "                        figure matching is OFF. Structural checks still\n"
              "                        run. Restore it from 'Wall Dock Deck/00 Plan/'.",
              file=sys.stderr)
        return []
    out = []
    with open(BAN_FILE, encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line)
    return out

# A street address in any page is a bug, whatever the name — with one exception:
# our own registered address, which belongs on the privacy page. Anything else
# matching this shape is a customer's property and must not ship.
ADDRESS_RE = re.compile(r"\b\d{2,5}\s+(?:N|S|E|W|NE|NW|SE|SW)\.?\s+\w+", re.I)

OWN_ADDRESS = [
    "16300 SW 137th Avenue",
    "16300 SW 137 Ave",
]

TERMS = banned_terms()


def pages():
    for d, dirs, fs in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in ("_build", "_preview", ".git", "guides", "scripts")]
        for f in fs:
            if f.endswith(".html") and d != ROOT:      # skip the untouched prototype
                yield os.path.join(d, f)

def extra_docs():
    """The guides were excluded from this scan until October 2026, which meant the four
    documents we actually email were the only ones never checked. Their text source is
    checked here, and the built PDFs too when pdftotext is available."""
    src = os.path.join(ROOT, "_build", "guides-src")
    if os.path.isdir(src):
        for f in sorted(os.listdir(src)):
            if f.endswith(".md"):
                yield os.path.join(src, f)
    import shutil, subprocess, tempfile
    if not shutil.which("pdftotext"):
        return
    for sub in ("guides", "downloads"):
        d = os.path.join(ROOT, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".pdf"):
                continue
            t = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
            t.close()
            subprocess.run(["pdftotext", os.path.join(d, f), t.name],
                           capture_output=True)
            yield t.name + "\x00" + os.path.join(d, f)


def read_doc(p):
    if "\x00" in p:
        tmp, real = p.split("\x00")
        try:
            return open(tmp, encoding="utf8", errors="replace").read(), real
        finally:
            os.unlink(tmp)
    return open(p, encoding="utf8", errors="replace").read(), p


def main():
    problems = []
    for p in list(pages()) + list(extra_docs()):
        text, p = read_doc(p)
        rel = os.path.relpath(p, ROOT)
        for bad in TERMS:
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
