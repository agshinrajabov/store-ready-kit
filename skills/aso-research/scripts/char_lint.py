#!/usr/bin/env python3
"""Lint App Store metadata against Apple's character limits and keyword-field hygiene (2.3.7).

Every name / subtitle / keyword-field variant the skill proposes goes through this before it is shown.
Exit code 1 if any variant breaks a hard limit or a blocking rule, so it can gate a pipeline.

Input: a JSON object, or a list of objects (variants), with any of these fields:
  name (30) · subtitle (30) · keywords (100) · promotional_text (170) · description (4000) · whats_new (4000)

Examples:
  char_lint.py --name "Leafwise" --subtitle "Keep every houseplant alive" --keywords "plant,watering,succulent"
  char_lint.py --file variants.json
  char_lint.py --file variants.json --competitors competitors.json --format md

Rules:
  LIMIT   over the character limit                                          (blocking)
  BLOCK   competitor app name or a well-known trademark in name/subtitle/keywords (blocking, 2.3.7)
  BLOCK   price or ranking claim in name/subtitle/keywords ("free", "#1", "best")  (blocking, 2.3.7)
  WARN    a single-word competitor name used as a plain word                (warning)
  WASTE   space after a comma, duplicate words, words already in name/subtitle,
          plural duplicates, filler words ("app", "the", "and")              (warning)
"""

import argparse
import json
import re
import sys

LIMITS = {"name": 30, "subtitle": 30, "keywords": 100, "promotional_text": 170, "description": 4000,
          "whats_new": 4000}
MIN_NAME = 2

# Well-known marks people try to borrow. Not exhaustive: competitor names from a snapshot are added at runtime.
TRADEMARKS = {"instagram", "tiktok", "whatsapp", "facebook", "messenger", "snapchat", "youtube", "netflix",
              "spotify", "uber", "chatgpt", "openai", "gemini", "claude", "copilot", "minecraft", "roblox",
              "fortnite", "pokemon", "tinder", "bumble", "duolingo", "candy crush", "wordle", "telegram",
              "iphone", "ipad", "apple", "siri", "airpods", "android", "google", "amazon", "alexa", "disney",
              "marvel", "lego", "nike", "strava", "zoom", "notion", "canva", "capcut"}
PRICE_RANK = [r"\bfree\b", r"\$\s?\d", r"\b\d+\s?% off\b", r"\bsale\b", r"#\s?1\b", r"\bnumber one\b", r"\bbest\b",
              r"\btop[- ]rated\b", r"\bno\.?\s?1\b"]
FILLER = {"app", "apps", "the", "and", "for", "with", "a", "an", "of", "to", "in", "on", "my", "your", "iphone",
          "ipad", "ios", "game", "games"}


def count(text):
    # Apple counts characters as the user sees them; combining marks count as typed.
    return len(text or "")


def words(text):
    return [w for w in re.split(r"[^\w'+-]+", (text or "").lower()) if w]


def singular(w):
    if len(w) > 3 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 3 and w.endswith("es") and w[-3] in "sxz":
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def competitor_names(path, own_name=None):
    """Brand parts of competitor names, split into (blocked, warn).

    blocked: multi-word brands that at most two competitor names contain ("habit rabbit") — a reference
             to a specific app.
    warn:    single-word brands ("streaks", "fabulous") — ordinary words too, so only a warning.
    Phrases many competitors share ("habit tracker") are the niche's vocabulary and are neither.
    """
    with open(path, encoding="utf-8") as fh:
        snap = json.load(fh)
    names = [(a.get("trackName") or "").lower() for a in snap.get("apps", [])]
    blocked, warn = set(), set()
    for full in names:
        brand = re.split(r"[:\-–—|(•]", full)[0].strip()
        brand = re.sub(r"[^\w\s'&+]", "", brand).strip()
        if not brand or (own_name and brand == own_name.lower()):
            continue
        shared = sum(1 for n in names if brand in n)
        if shared > 2 or len(brand) < 4:
            continue
        (blocked if len(brand.split()) > 1 else warn).add(brand)
    return blocked, warn


def lint(variant, marks, soft_marks=()):
    issues = []
    for field, limit in LIMITS.items():
        if field in variant and variant[field] is not None:
            n = count(variant[field])
            if n > limit:
                issues.append(("LIMIT", field, f"{n}/{limit} characters ({n - limit} over)"))
    name = variant.get("name") or ""
    if "name" in variant and count(name.strip()) < MIN_NAME:
        issues.append(("LIMIT", "name", "name is empty or too short"))

    head = {"name": name, "subtitle": variant.get("subtitle") or "", "keywords": variant.get("keywords") or ""}
    # Apple combines words across the three fields, so a brand split into its words ("mountain,project")
    # indexes like the brand itself.
    all_words = {singular(w) for t in head.values() for w in words(t)}
    for mark in sorted(marks):
        parts = [singular(w) for w in words(mark)]
        joined = " ".join(head.values()).lower()
        whole = re.search(r"(?<![\w])" + re.escape(mark) + r"(?![\w])", joined.replace(",", " , "))
        if len(parts) > 1 and all(w in all_words for w in parts) and not whole:
            issues.append(("BLOCK", "all", f"'{mark}' is assembled from words across the fields — Apple combines "
                                           f"them, so this targets another app's name (2.3.7)"))
    for field, text in head.items():
        low = " " + text.lower().replace(",", " , ") + " "
        for mark in sorted(marks):
            if re.search(r"(?<![\w])" + re.escape(mark) + r"(?![\w])", low):
                issues.append(("BLOCK", field, f"'{mark}' is another company's app name or trademark (2.3.7)"))
        for mark in sorted(soft_marks):
            if re.search(r"(?<![\w])" + re.escape(mark) + r"(?![\w])", low):
                issues.append(("WARN", field, f"'{mark}' is also a competitor's app name — fine as a plain word, "
                                              "never as a reference to that app"))
        for pat in PRICE_RANK:
            m = re.search(pat, text, re.I)
            if m:
                issues.append(("BLOCK", field, f"'{m.group(0)}' — price, discount or ranking claim (2.3.7)"))

    kw = variant.get("keywords")
    if kw:
        if re.search(r",\s", kw):
            issues.append(("WASTE", "keywords", "space after a comma wastes characters"))
        if re.search(r"\s{2,}|^\s|\s$", kw):
            issues.append(("WASTE", "keywords", "leading/trailing or double spaces"))
        terms = [t.strip().lower() for t in kw.split(",") if t.strip()]
        seen, dup = set(), []
        for t in terms:
            if t in seen:
                dup.append(t)
            seen.add(t)
        if dup:
            issues.append(("WASTE", "keywords", f"duplicate terms: {', '.join(sorted(set(dup)))}"))
        in_head = set(words(name)) | set(words(variant.get("subtitle")))
        kw_words = [w for t in terms for w in words(t)]
        repeated = sorted({w for w in kw_words if w in in_head})
        if repeated:
            issues.append(("WASTE", "keywords", f"already in name/subtitle (indexed together): {', '.join(repeated)}"))
        sing = {}
        for w in kw_words:
            sing.setdefault(singular(w), set()).add(w)
        plur = sorted("/".join(sorted(v)) for v in sing.values() if len(v) > 1)
        if plur:
            issues.append(("WASTE", "keywords", f"singular and plural both present: {', '.join(plur)}"))
        filler = sorted({w for w in kw_words if w in FILLER})
        if filler:
            issues.append(("WASTE", "keywords", f"filler words: {', '.join(filler)}"))
        multi = [t for t in terms if " " in t]
        if multi:
            issues.append(("WASTE", "keywords", f"multi-word terms (single words combine anyway): {', '.join(multi[:5])}"))
    if name and variant.get("subtitle"):
        overlap = sorted({singular(w) for w in words(name)} & {singular(w) for w in words(variant["subtitle"])}
                         - {singular(f) for f in FILLER})
        if overlap:
            issues.append(("WASTE", "subtitle", f"repeats words from the name: {', '.join(overlap)}"))
    return issues


def evaluate(variants=None, file=None, competitors=None, extra_marks=()):
    """Entry point used by the eval harness. Returns a dict with all_within_limits and violations."""
    if file:
        with open(file, encoding="utf-8") as fh:
            variants = json.load(fh)
    if isinstance(variants, dict):
        variants = variants.get("variants", [variants])
    marks, soft = set(TRADEMARKS), set()
    if competitors:
        hard, soft = competitor_names(competitors, (variants[0].get("name") if variants else None))
        marks |= hard
    marks |= {m.lower() for m in extra_marks}
    results, violations = [], []
    for i, v in enumerate(variants):
        own = re.split(r"[:\-–—|]", v.get("name") or "")[0].strip().lower()
        issues = lint(v, {m for m in marks if m != own}, {m for m in soft if m != own})
        blocking = [x for x in issues if x[0] in ("LIMIT", "BLOCK")]
        results.append({"variant": i + 1, "label": v.get("label"), "fields": {k: f"{count(v[k])}/{LIMITS[k]}" for k in LIMITS if k in v},
                        "ok": not blocking, "issues": [{"rule": r, "field": f, "detail": d} for r, f, d in issues]})
        violations += [f"variant {i + 1} {f}: {d}" for r, f, d in blocking]
    return {"tool": "char_lint", "all_within_limits": not violations, "violations": violations, "results": results}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", help="JSON object or list of variant objects")
    for f in LIMITS:
        p.add_argument(f"--{f.replace('_', '-')}", dest=f, help=f"{f} ({LIMITS[f]} characters)")
    p.add_argument("--competitors", help="competitor snapshot JSON; its app names become blocked terms")
    p.add_argument("--format", choices=["json", "md"], default="md")
    args = p.parse_args()

    if args.file:
        res = evaluate(file=args.file, competitors=args.competitors)
    else:
        v = {f: getattr(args, f) for f in LIMITS if getattr(args, f) is not None}
        if not v:
            p.error("give --file or at least one field")
        res = evaluate(variants=[v], competitors=args.competitors)

    if args.format == "json":
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        for r in res["results"]:
            status = "OK" if r["ok"] else "BLOCKED"
            tag = f" ({r['label']})" if r.get("label") else ""
            print(f"Variant {r['variant']}{tag}: {status} — " + ", ".join(f"{k} {v}" for k, v in r["fields"].items()))
            for i in r["issues"]:
                print(f"  {i['rule']:<5} {i['field']:<10} {i['detail']}")
        print("\nAll variants within limits and rules." if res["all_within_limits"] else
              f"\n{len(res['violations'])} blocking issue(s).")
    sys.exit(0 if res["all_within_limits"] else 1)


if __name__ == "__main__":
    main()
