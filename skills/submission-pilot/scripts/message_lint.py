#!/usr/bin/env python3
"""Lint a message to App Review before it is sent: review notes, a Resolution Center reply, or an appeal.

Catches what makes reviewers' and the App Review Board's job harder: leftover placeholders, pleading,
arguing, claims of full compliance, deadlines, pointing at other apps, a missing demo account, a reply that
does not name the guideline, and an originality argument against a quality judgement.

Examples:
  message_lint.py --kind notes --file notes.txt --requires-login
  message_lint.py --kind reply --file reply.txt --letter-kind b-low-effort
  message_lint.py --kind appeal --file appeal.txt --competitors competitors.json --format json

Exit code 1 if anything blocking is found.
"""

import argparse
import json
import re
import sys

LIMITS = {"notes": (4000, 1200), "reply": (4000, 1500), "appeal": (4000, 3000)}   # (hard, recommended)

BLOCK = [
    (r"<[^<>\n]{2,80}>|\[(?:insert|your|app name|todo)[^\]]*\]|\bTODO\b|\bTBD\b|\bXXX\b|lorem ipsum", "placeholder left in the text"),
    (r"fully compl(y|ies|iant)|100\s?% compl|complies with all|in full compliance", "claims full compliance — show, don't assert"),
    (r"guarantee", "the word 'guarantee'"),
]
WARN = [
    (r"please (approve|accept|let (it|us|me) through)|approve (my|our|the) app|kindly approve", "asks for approval — explain instead"),
    (r"deadline|launch (date|event|day)|investors?|press (release|coverage)|marketing campaign|we are losing", "deadlines or business pressure — not a review argument"),
    (r"unfair|ridiculous|absurd|nonsense|clearly wrong|you (didn't|did not|failed to|obviously)|wasted", "hostile or blaming tone"),
    (r"other apps? (do|does|are|have) (the same|this|it)|why (was|is) (my|our) app (rejected|treated)", "points at other apps — each app is reviewed on its own"),
    (r"!{2,}|\b[A-Z]{5,}\b(?<!APPLE)", "shouting (repeated '!' or all-caps words)"),
    (r"\b(the|our) best\b|revolutionary|world[- ]class|amazing|incredible|game[- ]changer", "marketing superlatives"),
]


def lint(text, kind, requires_login=False, letter_kind=None, competitors=(), app_name=None):
    issues = []
    hard, rec = LIMITS[kind]
    n = len(text)
    if n > hard:
        issues.append(("BLOCK", f"{n} characters; the field holds {hard}"))
    elif n > rec:
        issues.append(("WARN", f"{n} characters; aim for under {rec} — reviewers read it before opening the app"))
    for pat, why in BLOCK:
        m = re.search(pat, text, re.I)
        if m:
            issues.append(("BLOCK", f"{why}: '{m.group(0)[:40]}'"))
    for pat, why in WARN:
        m = re.search(pat, text, re.I if "A-Z" not in pat else 0)
        if m:
            issues.append(("WARN", f"{why}: '{m.group(0)[:40]}'"))
    low = text.lower()
    for c in competitors:
        if c and c != (app_name or "").lower() and re.search(r"(?<!\w)" + re.escape(c) + r"(?!\w)", low):
            issues.append(("WARN", f"names another app ('{c}') — compare to the guideline, not to apps"))
    if kind == "notes":
        if requires_login and not re.search(r"(user ?name|e-?mail|login|account)\s*[:=]", low):
            issues.append(("BLOCK", "login required but no demo account (username/password) in the notes"))
        if not re.search(r"^\s*(\d+[.)]|-|•)\s+\S", text, re.M):
            issues.append(("WARN", "no numbered steps to the core feature"))
    if kind in ("reply", "appeal") and not re.search(r"\b\d\.\d+(\.\d+)?\b", text):
        issues.append(("WARN", "does not name the guideline it answers"))
    if kind == "appeal":
        if not re.search(r"(reason|because|specifically|evidence|video|recording)", low):
            issues.append(("WARN", "no specific reasons or evidence — the appeal form asks for specific reasons"))
    if letter_kind == "b-low-effort" and re.search(r"\b(original|unique|first of its kind|no other app|nothing else)\b", low):
        issues.append(("WARN", "argues originality against a quality / low-effort judgement — it does not answer the letter; "
                               "describe what changed instead"))
    return issues


def evaluate(file, kind, requires_login=False, letter_kind=None, competitors_file=None, app_name=None):
    with open(file, encoding="utf-8") as fh:
        text = fh.read()
    comps = []
    if competitors_file:
        with open(competitors_file, encoding="utf-8") as fh:
            snap = json.load(fh)
        for a in snap.get("apps", []):
            brand = re.split(r"[:\-–—|(]", (a.get("trackName") or "").lower())[0].strip()
            if len(brand) >= 5:
                comps.append(brand)
    issues = lint(text, kind, requires_login, letter_kind, comps, app_name)
    blocking = [d for s, d in issues if s == "BLOCK"]
    return {"tool": "message_lint", "kind": kind, "characters": len(text), "ok": not blocking,
            "violations": blocking, "warnings": [d for s, d in issues if s == "WARN"]}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--kind", choices=sorted(LIMITS), required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--requires-login", action="store_true")
    p.add_argument("--letter-kind", help="from rejection_triage.py kind_4_3, e.g. b-low-effort")
    p.add_argument("--competitors", help="competitor snapshot JSON; mentions of those apps are flagged")
    p.add_argument("--app-name")
    p.add_argument("--format", choices=["json", "md"], default="md")
    a = p.parse_args()
    r = evaluate(a.file, a.kind, a.requires_login, a.letter_kind, a.competitors, a.app_name)
    if a.format == "json":
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        print(f"{a.kind}: {r['characters']} characters — {'OK' if r['ok'] else 'BLOCKED'}")
        for v in r["violations"]:
            print(f"  BLOCK {v}")
        for w in r["warnings"]:
            print(f"  WARN  {w}")
    sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
