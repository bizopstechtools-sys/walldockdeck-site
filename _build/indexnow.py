#!/usr/bin/env python3
"""Tell Bing (and the AI assistants that read its index) that pages changed.

Google has not adopted IndexNow, so this does nothing for Google — Search
Console and the sitemap are the Google path. This is for Bing, Yandex and the
assistants that sit on Bing's index, where it is close to instant and free.

Run after a deploy:   python3 _build/indexnow.py
Dry run:              python3 _build/indexnow.py --dry-run
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://walldockdeck.com"
HOST = "walldockdeck.com"
ENDPOINT = "https://api.indexnow.org/IndexNow"


def key():
    p = os.path.join(ROOT, "_build", "data", "indexnow.key")
    if not os.path.exists(p):
        sys.exit("no _build/data/indexnow.key — run build.py first")
    k = open(p, encoding="utf8").read().strip()
    if not re.fullmatch(r"[0-9a-fA-F]{8,128}", k):
        sys.exit(f"key is not 8-128 hex characters: {k!r}")
    return k


def urls():
    """Read the sitemap rather than keeping a second list that can drift."""
    p = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(p):
        sys.exit("no sitemap.xml — run build.py first")
    found = re.findall(r"<loc>(.*?)</loc>", open(p, encoding="utf8").read())
    off = [u for u in found if not u.startswith(SITE)]
    if off:
        sys.exit(f"sitemap has URLs off {HOST}, refusing to submit: {off[:3]}")
    return found


def main():
    k, us = key(), urls()
    dry = "--dry-run" in sys.argv
    print(f"{len(us)} URLs | key {k[:8]}… | key file must be live at {SITE}/{k}.txt")

    if dry:
        for u in us:
            print("  ", u)
        return

    body = json.dumps({"host": HOST, "key": k,
                       "keyLocation": f"{SITE}/{k}.txt", "urlList": us}).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body,
        headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code = r.status
    except urllib.error.HTTPError as ex:
        code = ex.code
    except urllib.error.URLError as ex:
        sys.exit(f"could not reach IndexNow: {ex.reason}")

    # 200 accepted, 202 accepted but key not yet validated, 422 usually means
    # the key file is not reachable at keyLocation yet.
    msg = {200: "accepted", 202: "accepted, key still being validated",
           400: "bad request", 403: "key not valid for this host",
           422: "URLs do not match the host, or the key file is not reachable",
           429: "too many requests"}.get(code, "unexpected")
    print(f"HTTP {code} — {msg}")
    sys.exit(0 if code in (200, 202) else 1)


if __name__ == "__main__":
    main()
