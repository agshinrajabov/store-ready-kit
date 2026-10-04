#!/usr/bin/env python3
"""Pack the 100-character keyword field from scored keywords, never exceeding the limit.

Takes the rows from `keyword_rank.py score` (or a plain list of terms, best first) plus your name and
subtitle, and fills the field greedily by opportunity per character:

  - splits phrases into single words (Apple combines words across name, subtitle and keywords),
  - drops words already in the name or subtitle, duplicates, plural twins and filler,
  - drops blocked terms (competitor names) and anything char_lint.py would block,
  - joins with commas and no spaces.

The result is re-checked with char_lint.py before it is printed; a pack that fails the lint is an error.

Examples:
  keyword_pack.py --scores scores.json --competitors apps.json --name "Leafwise" --subtitle "Keep every houseplant alive"
  keyword_pack.py --terms "plant,watering,care,succulent,repot" --name "Leafwise" --block "planta app"
"""

import argparse
import importlib.util
import json
import os
import re
import sys

LIMIT = 100
HERE = os.path.dirname(os.path.abspath(__file__))


def _lint_module():
    spec = importlib.util.spec_from_file_location("char_lint", os.path.join(HERE, "char_lint.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MIN_RELEVANCE = 0.5


def value_of(r, order):
    """Scored rows rank by opportunity; rows with no opportunity fall back to relevance and difficulty; a
    plain term list keeps its order. Each tier stays below the one above it."""
    opp = r.get("opportunity")
    if opp:
        return 10.0 + opp
    if r.get("difficulty") is not None:
        return (r.get("relevance") if r.get("relevance") is not None else 1.0) * (100 - r["difficulty"]) / 100 * 9.0 + 0.5
    return max(0.01, 0.5 - order * 0.005)


def pack(rows, name="", subtitle="", limit=LIMIT, extra_blocked=(), competitors=None):
    lint = _lint_module()
    taken = {lint.singular(w) for w in lint.words(name) + lint.words(subtitle)}
    blocked_phrases = {t.lower() for t in extra_blocked}
    if competitors:
        hard, _ = lint.competitor_names(competitors, name)
        blocked_phrases |= hard
    candidates, low_relevance = {}, []
    for order, r in enumerate(rows):
        if r.get("blocked"):
            blocked_phrases.add(r["term"].lower())
            continue
        if r.get("relevance") is not None and r["relevance"] < MIN_RELEVANCE:
            low_relevance.append(r["term"])
            continue
        value = value_of(r, order)
        for w in lint.words(r["term"]):
            if w in lint.FILLER or len(w) < 2:
                continue
            key = lint.singular(w)
            if key in taken:
                continue
            best = candidates.get(key)
            if best is None or value > best[1] or (value == best[1] and len(w) < len(best[0])):
                candidates[key] = (w, value)
    marks = set(lint.TRADEMARKS)
    clean = []
    for key, (w, value) in candidates.items():
        if w in marks or any(re.search(p, w, re.I) for p in lint.PRICE_RANK):
            continue
        clean.append((value / (len(w) + 1), value, w))
    clean.sort(key=lambda x: (-x[0], -x[1], x[2]))
    head_words = taken

    def completes_brand(words_now):
        have = head_words | {lint.singular(x) for x in words_now}
        for ph in blocked_phrases:
            parts = [lint.singular(x) for x in lint.words(ph)]
            if parts and all(p in have for p in parts):
                return ph
        return None

    chosen, used, refused = [], 0, []
    for _, value, w in clean:
        cost = len(w) + (1 if chosen else 0)
        if used + cost > limit:
            continue
        brand = completes_brand(chosen + [w])
        if brand:
            refused.append(f"{w} (would complete '{brand}')")
            continue
        chosen.append(w)
        used += cost
    field = ",".join(chosen)
    check = lint.evaluate(variants=[{"name": name or "x" * 2, "subtitle": subtitle, "keywords": field}],
                          competitors=competitors, extra_marks=blocked_phrases)
    left_out = [w for _, _, w in clean if w not in chosen and not any(r.startswith(w + " ") for r in refused)]
    return {"tool": "keyword_pack", "keywords": field, "characters": len(field), "limit": limit,
            "free": limit - len(field), "words": chosen, "left_out": left_out[:20],
            "refused_brand_words": refused, "low_relevance_dropped": low_relevance,
            "lint_ok": check["all_within_limits"], "lint": check["results"][0]["issues"]}


def evaluate(scores=None, terms=None, name="", subtitle="", limit=LIMIT, competitors=None, blocked=()):
    """Eval entry point: pack, then report whether every limit holds."""
    rows = load_rows(scores, terms)
    res = pack(rows, name, subtitle, limit, extra_blocked=blocked, competitors=competitors)
    res["all_within_limits"] = res["lint_ok"] and res["characters"] <= limit
    res["violations"] = [] if res["all_within_limits"] else [f"{res['characters']}/{limit}", res["lint"]]
    return res


def load_rows(scores=None, terms=None):
    rows = []
    if scores:
        with open(scores, encoding="utf-8") as fh:
            data = json.load(fh)
        rows = data.get("rows", data) if isinstance(data, dict) else data
        rows = [r if isinstance(r, dict) else {"term": r} for r in rows]
        rows.sort(key=lambda r: -(r.get("opportunity") or 0))
    if terms:
        rows += [{"term": t.strip()} for t in (terms.split(",") if isinstance(terms, str) else terms) if t.strip()]
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scores", help="JSON from `keyword_rank.py score`")
    p.add_argument("--terms", help="comma-separated terms, best first (alternative to --scores)")
    p.add_argument("--country", help="keep only rows for this storefront")
    p.add_argument("--name", default="")
    p.add_argument("--subtitle", default="")
    p.add_argument("--limit", type=int, default=LIMIT)
    p.add_argument("--competitors", help="competitor snapshot JSON (from `keyword_rank.py apps` or store-audit)")
    p.add_argument("--block", action="append", default=[], help="extra phrase to keep out (e.g. a brand); repeatable")
    p.add_argument("--format", choices=["json", "md"], default="md")
    a = p.parse_args()
    if not a.scores and not a.terms:
        p.error("give --scores or --terms")
    rows = load_rows(a.scores, a.terms)
    if a.country:
        rows = [r for r in rows if r.get("country") in (None, a.country)]
    res = pack(rows, a.name, a.subtitle, a.limit, extra_blocked=a.block, competitors=a.competitors)
    if a.format == "json":
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(res["keywords"])
        print(f"\n{res['characters']}/{res['limit']} characters · {len(res['words'])} words · lint {'OK' if res['lint_ok'] else 'FAILED'}")
        if res["free"] >= 5:
            print(f"{res['free']} characters free — add relevant words by hand, then re-run char_lint.py")
        if res["left_out"]:
            print("Did not fit: " + ", ".join(res["left_out"]))
        if res["refused_brand_words"]:
            print("Kept out (brand): " + ", ".join(res["refused_brand_words"]))
        if res["low_relevance_dropped"]:
            print(f"Dropped, relevance < {MIN_RELEVANCE}: " + ", ".join(res["low_relevance_dropped"]))
        for i in res["lint"]:
            print(f"  {i['rule']} {i['field']}: {i['detail']}")
    sys.exit(0 if res["lint_ok"] else 1)


if __name__ == "__main__":
    main()
