#!/usr/bin/env python3
"""Pull the apps that share a niche with yours from the public iTunes Search API.

No account, no key, Python standard library only. The output is a JSON snapshot that
similarity_score.py reads, so a scan can be frozen and re-scored offline.

Examples:
  competitor_scan.py --term "screw puzzle" --term "pin puzzle" --limit 50 -o competitors.json
  competitor_scan.py --term "habit tracker" --country gb --genre 6007
  competitor_scan.py --lookup 1234567890 -o me.json        # one app by its App Store ID

What the API does not return: subtitle, keyword field, in-app purchase list, and the
"Contains ads" flag. Those come from the store page itself or from you; the snapshot leaves
them empty rather than guessing.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SEARCH_URL = "https://itunes.apple.com/search"
LOOKUP_URL = "https://itunes.apple.com/lookup"
USER_AGENT = "store-ready-kit/competitor_scan (+https://github.com/agshinrajabov/store-ready-kit)"

KEEP = (
    "trackId", "trackName", "bundleId", "artistName", "sellerName", "primaryGenreName",
    "genres", "price", "formattedPrice", "averageUserRating", "userRatingCount",
    "releaseDate", "currentVersionReleaseDate", "version", "description",
    "screenshotUrls", "ipadScreenshotUrls", "artworkUrl512", "trackViewUrl",
    "contentAdvisoryRating", "fileSizeBytes", "languageCodesISO2A",
)


def fetch(url, params, retries=3):
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{query}", headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as exc:
            # The API rate-limits at roughly 20 calls a minute and answers 403 when it does.
            if attempt == retries - 1:
                raise SystemExit(f"competitor_scan: request failed after {retries} tries: {exc}")
            time.sleep(3 * (attempt + 1))
    return {}


def slim(app, term=None):
    out = {k: app.get(k) for k in KEEP if k in app}
    out["screenshotCount"] = len(app.get("screenshotUrls") or [])
    out["subtitle"] = None          # not exposed by the API
    out["matchedTerms"] = [term] if term else []
    return out


def search(terms, country, limit, genre=None):
    apps = {}
    for term in terms:
        params = {"term": term, "entity": "software", "country": country, "limit": min(limit, 200)}
        if genre:
            params["genreId"] = genre
        data = fetch(SEARCH_URL, params)
        for rank, app in enumerate(data.get("results", []), start=1):
            if genre and str(genre) not in [str(g) for g in app.get("genreIds", [])]:
                continue
            tid = app.get("trackId")
            if tid in apps:
                apps[tid]["matchedTerms"].append(term)
                apps[tid]["ranks"][term] = rank
            else:
                entry = slim(app, term)
                entry["ranks"] = {term: rank}
                apps[tid] = entry
        time.sleep(1.0)
    ordered = sorted(apps.values(), key=lambda a: (-(a.get("userRatingCount") or 0), a["trackName"]))
    return ordered[:limit]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--term", action="append", default=[], help="search term; repeat for several (results are merged)")
    p.add_argument("--lookup", action="append", default=[], help="App Store ID to fetch directly; repeatable")
    p.add_argument("--country", default="us", help="two-letter storefront code (default: us)")
    p.add_argument("--limit", type=int, default=50, help="max apps kept after merging (default: 50)")
    p.add_argument("--genre", help="keep only apps carrying this genre ID (e.g. 6014 Games, 7012 Puzzle)")
    p.add_argument("-o", "--output", help="write JSON here instead of stdout")
    args = p.parse_args()

    if not args.term and not args.lookup:
        p.error("give at least one --term or --lookup")

    apps = []
    if args.lookup:
        data = fetch(LOOKUP_URL, {"id": ",".join(args.lookup), "country": args.country})
        apps.extend(slim(a) for a in data.get("results", []))
    if args.term:
        apps.extend(search(args.term, args.country, args.limit, args.genre))

    snapshot = {
        "source": "itunes-search-api",
        "fetchedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "country": args.country,
        "terms": args.term,
        "count": len(apps),
        "apps": apps,
    }
    text = json.dumps(snapshot, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"competitor_scan: {len(apps)} apps -> {args.output}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
