#!/usr/bin/env python3
"""Keyword research from public App Store data — no account, no paid tool.

Subcommands:

  expand   Grow a seed list with App Store autocomplete (the hints users see while typing).
  reviews  Mine competitor reviews (public RSS) for the words users actually use.
  score    For each keyword and storefront: a popularity proxy, a difficulty estimate, relevance to
           your app, your current rank, and an opportunity score.

Examples:
  keyword_rank.py expand --seed "habit tracker" --seed "routine" --country us -o candidates.json
  keyword_rank.py expand --seed habit --alphabet --country gb
  keyword_rank.py reviews --app-id 1234567890 --app-id 2345678901 --country us --top 40
  keyword_rank.py score --keywords candidates.json --app-text listing.json --app-id 123 --country us,gb
  keyword_rank.py score --keyword "habit tracker" --keyword "streak" --country us --format md

How the numbers are made (all are proxies; say so when you report them):
  popularity  0-100. A term that autocomplete offers after fewer typed letters, and higher in the list,
              is searched more. 100 = offered after 2 letters in first place; 0 = never offered.
  difficulty  0-100. From the top 10 results: how many ratings they have (log scale), how many carry the
              exact term in their name, and how established they are.
  relevance   0-1. Share of the keyword's words found in your own name/subtitle/description, or set by hand.
  opportunity popularity x (100 - difficulty) / 100 x relevance.

Apple's real search volumes are only visible inside Apple Search Ads. These proxies rank candidates
against each other; they are not traffic forecasts.
"""

import argparse
import json
import math
import plistlib
import re
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

UA = "store-ready-kit/keyword_rank (+https://github.com/agshinrajabov/store-ready-kit)"
HINTS = "https://search.itunes.apple.com/WebObjects/MZSearchHints.woa/wa/hints"
SEARCH = "https://itunes.apple.com/search"
REVIEWS = "https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={id}/sortBy=mostRecent/json"

# Storefront IDs used by the hints endpoint (X-Apple-Store-Front).
STOREFRONTS = {"us": 143441, "gb": 143444, "de": 143443, "fr": 143442, "ca": 143455, "au": 143460,
               "jp": 143462, "it": 143450, "es": 143454, "nl": 143452, "br": 143503, "mx": 143468,
               "in": 143467, "kr": 143466, "cn": 143465, "tr": 143480, "ru": 143469, "se": 143456}

STOP = set("""a an and the for with of to in on at by from my your our you we i it is are be this that app apps
game games get got very really just so but not no yes can will would could like love great good nice best
use using used one also even much more most all any some way thing things make makes made lot lots time
please would been have has had was were do does did dont don't its it's im i'm ive i've""".split())

_last = [0.0]


def get(url, headers=None, raw=False, retries=3):
    # Gentle pacing: the public endpoints throttle at roughly 20 requests a minute.
    wait = 1.2 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                _last[0] = time.time()
                data = resp.read()
                return data if raw else json.loads(data.decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            if attempt == retries - 1:
                print(f"keyword_rank: giving up on {url[:90]}: {exc}", file=sys.stderr)
                return None
            time.sleep(4 * (attempt + 1))


def hints(term, country):
    sf = STOREFRONTS.get(country)
    if not sf:
        raise SystemExit(f"no storefront id for '{country}'; known: {', '.join(sorted(STOREFRONTS))}")
    q = urllib.parse.urlencode({"clientApplication": "Software", "term": term})
    data = get(f"{HINTS}?{q}", {"X-Apple-Store-Front": f"{sf}-1,29"}, raw=True)
    if not data:
        return []
    try:
        return [h["term"] for h in plistlib.loads(data).get("hints", [])]
    except Exception:
        return []


def popularity(term, country):
    """Shortest typed prefix at which autocomplete offers the term, and where it sits in the list."""
    term = term.lower().strip()
    for n in range(2, len(term) + 1):
        prefix = term[:n]
        if prefix.endswith(" "):
            continue
        offered = [h.lower() for h in hints(prefix, country)]
        if term in offered:
            pos = offered.index(term)
            typed = (n - 2) / max(1, len(term) - 2)        # 0 when found after 2 letters
            return round(100 * (1 - 0.85 * typed) * (1 - 0.06 * pos), 1), n, pos + 1
    return 0.0, None, None


def search(term, country, limit=25):
    q = urllib.parse.urlencode({"term": term, "entity": "software", "country": country, "limit": limit})
    data = get(f"{SEARCH}?{q}")
    return (data or {}).get("results", [])


def difficulty(term, results):
    top = results[:10]
    if not top:
        return 0.0, {}
    ratings = sorted((a.get("userRatingCount") or 0) for a in top)
    med = ratings[len(ratings) // 2]
    rating_part = min(1.0, math.log10(med + 1) / 5)           # 100k ratings -> 1.0
    words = set(term.lower().split())
    exact = sum(1 for a in top if words <= set(re.findall(r"\w+", (a.get("trackName") or "").lower())))
    title_part = exact / len(top)
    now = time.gmtime().tm_year
    years = [now - int((a.get("releaseDate") or "2026")[:4]) for a in top]
    age_part = min(1.0, (sum(years) / len(years)) / 8)
    score = round(100 * (0.55 * rating_part + 0.30 * title_part + 0.15 * age_part), 1)
    return score, {"median_ratings_top10": med, "exact_in_name_top10": exact, "mean_age_years": round(sum(years) / len(years), 1)}


def app_tokens(path):
    if not path:
        return None
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    text = " ".join(str(d.get(k) or "") for k in ("name", "subtitle", "keywords", "description"))
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def relevance(term, toks, manual):
    if term in manual:
        return manual[term]
    if toks is None:
        return 1.0
    ws = [w for w in re.findall(r"[a-z0-9]+", term.lower()) if w not in STOP]
    if not ws:
        return 0.0
    hit = sum(1 for w in ws if w in toks or w.rstrip("s") in toks)
    return round(hit / len(ws), 2)


def cmd_expand(a):
    found = {}
    for seed in a.seed:
        queue = [seed, seed + " "]
        if a.alphabet:
            queue += [f"{seed} {c}" for c in string.ascii_lowercase]
        for q in queue:
            for rank, h in enumerate(hints(q, a.country), 1):
                e = found.setdefault(h.lower(), {"term": h.lower(), "seeds": set(), "best_rank": rank})
                e["seeds"].add(seed)
                e["best_rank"] = min(e["best_rank"], rank)
    out = sorted(found.values(), key=lambda e: (e["best_rank"], e["term"]))
    for e in out:
        e["seeds"] = sorted(e["seeds"])
    res = {"tool": "keyword_rank.expand", "country": a.country, "seeds": a.seed, "count": len(out), "candidates": out,
           "note": "Autocomplete includes app names; brand terms are marked in `score` and must not be used as keywords."}
    emit(res, a)


def cmd_reviews(a):
    texts = []
    for app_id in a.app_id:
        for page in range(1, a.pages + 1):
            d = get(REVIEWS.format(country=a.country, page=page, id=app_id))
            entries = ((d or {}).get("feed") or {}).get("entry") or []
            if isinstance(entries, dict):
                entries = [entries]
            got = 0
            for e in entries:
                if "content" in e and "im:rating" in e:
                    texts.append((int(e["im:rating"]["label"]),
                                  (e.get("title", {}).get("label", "") + " " + e["content"]["label"]).lower()))
                    got += 1
            if not got:
                break
    uni, bi, low_star = Counter(), Counter(), Counter()
    for stars, t in texts:
        ws = [w for w in re.findall(r"[a-z][a-z'-]+", t) if w not in STOP and len(w) > 2]
        uni.update(set(ws))
        bi.update({f"{x} {y}" for x, y in zip(ws, ws[1:])})
        if stars <= 2:
            low_star.update(set(ws))
    res = {"tool": "keyword_rank.reviews", "apps": a.app_id, "country": a.country, "reviews": len(texts),
           "top_words": uni.most_common(a.top), "top_phrases": [p for p in bi.most_common(a.top * 2) if p[1] >= 2][:a.top],
           "complaint_words": low_star.most_common(min(20, a.top)),
           "note": "Words users use are keyword candidates; complaint words are differentiation material, not keywords."}
    emit(res, a)


def cmd_score(a):
    terms = list(a.keyword)
    if a.keywords:
        with open(a.keywords, encoding="utf-8") as fh:
            d = json.load(fh)
        items = d.get("candidates", d) if isinstance(d, dict) else d
        terms += [x["term"] if isinstance(x, dict) else x for x in items]
    terms = list(dict.fromkeys(t.lower().strip() for t in terms if t.strip()))[: a.max]
    manual = {}
    if a.relevance:
        with open(a.relevance, encoding="utf-8") as fh:
            manual = {k.lower(): float(v) for k, v in json.load(fh).items()}
    toks = app_tokens(a.app_text)
    rows = []
    for country in a.country.split(","):
        for term in terms:
            results = search(term, country)
            diff, detail = difficulty(term, results)
            pop, typed, pos = popularity(term, country) if not a.no_popularity else (None, None, None)
            rel = relevance(term, toks, manual)
            names = [(r.get("trackName") or "").lower() for r in results[:10]]
            owner = next((r.get("trackName") for r in results[:10]
                          if re.split(r"[:\-–—|(]", (r.get("trackName") or "").lower())[0].strip() == term), None)
            in_names = sum(1 for n in names if term in n)
            own_word = toks is not None and all(w in toks for w in term.split())
            # A distinctive app name (few apps use it, not a word you use for yourself) is a brand: blocked.
            # A generic phrase that happens to be an app's name ("habit tracker") is fine as a description.
            brand = bool(owner) and in_names <= 2 and not own_word
            name_note = (f"exact name of '{owner}' — use only as a description, never as a reference to that app"
                         if owner and not brand else None)
            rank = None
            if a.app_id:
                for i, r in enumerate(results, 1):
                    if str(r.get("trackId")) == str(a.app_id):
                        rank = i
                        break
            opp = round((pop or 0) * (100 - diff) / 100 * rel, 1) if pop is not None else None
            rows.append({"term": term, "country": country, "popularity": pop, "typed_letters": typed,
                         "hint_position": pos, "difficulty": diff, **detail, "relevance": rel,
                         "your_rank": rank if a.app_id else None, "opportunity": 0.0 if brand else opp,
                         "blocked": f"competitor app name '{owner}' (2.3.7)" if brand else None,
                         "note": name_note})
    rows.sort(key=lambda r: (r["country"], -(r["opportunity"] or 0)))
    res = {"tool": "keyword_rank.score", "fetchedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "countries": a.country.split(","), "rows": rows,
           "note": "Popularity and difficulty are proxies from public autocomplete and search results, not Apple volumes."}
    emit(res, a)


def emit(res, a):
    if getattr(a, "format", "json") == "md":
        if res["tool"].endswith("score"):
            print("| Keyword | Store | Popularity | Difficulty | Relevance | Opportunity | Your rank | Note |")
            print("|---|---|---|---|---|---|---|---|")
            for r in res["rows"]:
                print(f"| {r['term']} | {r['country']} | {r['popularity']} | {r['difficulty']} | {r['relevance']} | "
                      f"{r['opportunity']} | {r['your_rank'] or '—'} | {r['blocked'] or r.get('note') or ''} |")
            print(f"\n_{res['note']}_")
        elif res["tool"].endswith("expand"):
            for c in res["candidates"]:
                print(f"{c['best_rank']:>2}  {c['term']}   (from: {', '.join(c['seeds'])})")
        else:
            print(f"{res['reviews']} reviews\n\nTop phrases: " + ", ".join(f"{p} ({n})" for p, n in res["top_phrases"]))
            print("Top words: " + ", ".join(f"{w} ({n})" for w, n in res["top_words"]))
            print("Complaint words (1-2 stars): " + ", ".join(f"{w} ({n})" for w, n in res["complaint_words"]))
    else:
        text = json.dumps(res, indent=2, ensure_ascii=False)
        if getattr(a, "output", None):
            with open(a.output, "w", encoding="utf-8") as fh:
                fh.write(text + "\n")
            print(f"keyword_rank: wrote {a.output}", file=sys.stderr)
        else:
            print(text)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("expand", help="grow seeds with autocomplete")
    e.add_argument("--seed", action="append", required=True)
    e.add_argument("--country", default="us")
    e.add_argument("--alphabet", action="store_true", help="also query '<seed> a' … '<seed> z' (26 more calls per seed)")
    e.add_argument("--format", choices=["json", "md"], default="json")
    e.add_argument("-o", "--output")
    e.set_defaults(fn=cmd_expand)

    r = sub.add_parser("reviews", help="mine competitor reviews")
    r.add_argument("--app-id", action="append", required=True)
    r.add_argument("--country", default="us")
    r.add_argument("--pages", type=int, default=4, help="RSS pages per app, 50 reviews each (max 10)")
    r.add_argument("--top", type=int, default=30)
    r.add_argument("--format", choices=["json", "md"], default="json")
    r.add_argument("-o", "--output")
    r.set_defaults(fn=cmd_reviews)

    s = sub.add_parser("score", help="score keywords per storefront")
    s.add_argument("--keyword", action="append", default=[])
    s.add_argument("--keywords", help="JSON from `expand`, or a list of terms")
    s.add_argument("--country", default="us", help="comma-separated storefronts, e.g. us,gb,de")
    s.add_argument("--app-text", help="your listing JSON, for automatic relevance")
    s.add_argument("--relevance", help="JSON {term: 0..1} to set relevance by hand")
    s.add_argument("--app-id", help="your live app's ID, to report its current rank")
    s.add_argument("--max", type=int, default=60, help="score at most this many terms (default 60)")
    s.add_argument("--no-popularity", action="store_true", help="skip autocomplete probing (much faster)")
    s.add_argument("--format", choices=["json", "md"], default="json")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_score)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
