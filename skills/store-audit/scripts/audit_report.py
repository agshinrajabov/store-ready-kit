#!/usr/bin/env python3
"""Combine the store-audit scans into one scored report with a prioritised fix list and a draft
of the App Review notes.

Inputs are the JSON outputs of similarity_score.py, privacy_check.py and completeness_scan.py
(any subset), plus the listing JSON for the review-notes draft.

Examples:
  audit_report.py --similarity sim.json --privacy priv.json --completeness comp.json --listing listing.json
  audit_report.py --similarity sim.json --format json

Readiness score: starts at 100; each HIGH finding costs 15, MEDIUM 5, LOW 1; a 4.3 FLAG costs 30
and a WARN 12. Floor 0, and capped by the verdict (49 for NOT READY, 79 for READY WITH FIXES) so the number
never reads better than the verdict — so under a cap the number adds nothing; read the verdict and the fix
list. The verdict follows the worst finding:
  NOT READY         any HIGH finding or a 4.3 FLAG
  READY WITH FIXES  MEDIUM findings or a 4.3 WARN
  READY             nothing above LOW
"""

import argparse
import datetime
import json
import re
import sys

DISCLAIMER = "Guidance based on public App Review Guidelines; Apple's decisions are their own."
COST = {"HIGH": 15, "MEDIUM": 5, "LOW": 1}


def load(path):
    if not path:
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def similarity_findings(sim):
    if not sim:
        return []
    sev = {"FLAG": "HIGH", "WARN": "MEDIUM", "PASS": None}[sim["verdict"]]
    out = []
    if sev:
        top = sorted([s for s in sim["signals"] if s["assessed"]], key=lambda s: -s["points"])[:3]
        out.append({
            "severity": sev, "guideline": "4.3(b)", "area": "Differentiation",
            "title": f"Clone-signal score {sim['score']}/100 ({sim['verdict']})",
            "evidence": [f"{s['key']}: {s['points']}/{s['max']} — {s['evidence'][0]}" for s in top]
                        + ([f"hard triggers: {', '.join(sim['hard_triggers'])}"] if sim["hard_triggers"] else []),
            "fix": " ".join(s["fix"] for s in top if s["fix"]),
        })
    else:
        # A pass can still carry one loud signal (a keyword-stack name, stock captions); report it as tidy-up.
        for s in sim["signals"]:
            if s["assessed"] and s["points"] >= 0.6 * s["max"]:
                out.append({"severity": "LOW", "guideline": "4.3(b) / 2.3.7", "area": "Differentiation",
                            "title": f"Strong single signal: {s['key']} ({s['points']}/{s['max']})",
                            "evidence": s["evidence"][:2], "fix": s["fix"]})
    return out


def tag(findings, area):
    for f in findings:
        f.setdefault("area", area)
    return findings


def review_notes(lst, sim, rejected=False):
    lst = lst or {}
    if not lst.get("one_line") and lst.get("description"):
        first = re.split(r"(?<=[.!?])\s", lst["description"].strip())[0]
        lst = {**lst, "one_line": f"<rewrite as one plain sentence: who it is for and what it does — the description opens: \"{first[:120]}\">"}
    demo = lst.get("demo_account") or {}
    steps = lst.get("review_steps") or ["<the shortest path to the core feature, as numbered taps>"]
    diffs = lst.get("differentiators") or []
    lines = ["Hello App Review team,", "",
             f"{lst.get('name') or '<App name>'} {lst.get('one_line') or '<one sentence: who it is for and what it lets them do>'}", ""]
    if lst.get("requires_login"):
        lines += ["Demo account (full access, no expiry):",
                  f"  Username: {demo.get('username', '<username>')}",
                  f"  Password: {demo.get('password', '<password>')}", ""]
    lines += ["How to see the core feature:"]
    lines += [f"  {i}. {s}" for i, s in enumerate(steps, 1)]
    lines.append("")
    if diffs:
        lines += ["What this app does that others in the category do not:"]
        lines += [f"  - {d}" for d in diffs]
        lines.append("")
    if lst.get("non_obvious"):
        lines += ["Things that may not be obvious:"] + [f"  - {x}" for x in lst["non_obvious"]] + [""]
    if lst.get("changes_since_rejection"):
        lines += ["Changes since the previous review:"] + [f"  - {x}" for x in lst["changes_since_rejection"]] + [""]
    elif rejected:
        lines += ["Changes since the previous review (<guideline, date>):",
                  "  - <only changes that are in this build>", "  - <TestFlight round: testers, days, what changed>", ""]
    if lst.get("iap_summary"):
        lines += [f"In-app purchases: {lst['iap_summary']}", ""]
    lines += ["Thank you for your time."]
    return "\n".join(lines)


def build(sim, priv, comp, lst, rejection=None):
    findings = []
    findings += similarity_findings(sim)
    if priv:
        findings += tag(priv["findings"], "Privacy")
    if comp:
        findings += tag(comp["findings"], "Completeness & metadata")
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    findings.sort(key=lambda f: (order[f["severity"]], f["area"]))
    score = 100
    for f in findings:
        score -= COST[f["severity"]]
    if sim and sim["verdict"] == "FLAG":
        score -= 30 - COST["HIGH"]
    elif sim and sim["verdict"] == "WARN":
        score -= 12 - COST["MEDIUM"]
    score = max(0, score)
    worst = findings[0]["severity"] if findings else None
    verdict = {"HIGH": "NOT READY", "MEDIUM": "READY WITH FIXES", "LOW": "READY", None: "READY"}[worst]
    # The number must never read better than the verdict.
    score = min(score, {"NOT READY": 49, "READY WITH FIXES": 79, "READY": 100}[verdict])
    areas = {}
    for f in findings:
        a = areas.setdefault(f["area"], {"HIGH": 0, "MEDIUM": 0, "LOW": 0})
        a[f["severity"]] += 1
    covered = [n for n, x in (("4.3 differentiation", sim), ("5.1 privacy", priv), ("2.1/2.3/2.5.2 completeness", comp)) if x]
    return {
        "tool": "audit_report", "date": datetime.date.today().isoformat(),
        "app": (lst or {}).get("name") or (sim or {}).get("app"),
        "readiness": score, "verdict": verdict, "covered": covered,
        "similarity": {k: sim[k] for k in ("score", "verdict", "coverage", "nearest_neighbours")} if sim else None,
        "areas": areas, "findings": findings,
        "not_covered": [n for n, x in (("4.3 differentiation", sim), ("5.1 privacy", priv), ("2.1/2.3/2.5.2 completeness", comp)) if not x]
                       + ["2.1 crash-surface pass on a device (manual)", "2.5.2 interview (manual)"],
        "rejection": rejection,
        "prongs": sim.get("prongs") if sim else None,
        "review_notes": review_notes(lst, sim, rejected=bool(rejection) or bool((lst or {}).get("changes_since_rejection"))),
        "disclaimer": DISCLAIMER,
    }


def to_markdown(r):
    lines = [f"# Store audit — {r['app'] or 'app'}", "",
             f"**{r['verdict']}** · readiness {r['readiness']}/100 · {r['date']}", "",
             f"Covered: {', '.join(r['covered']) or 'nothing'}",
             f"Not covered by scripts: {', '.join(r['not_covered'])} — report each as passed, failed or not checked.", ""]
    if r.get("rejection"):
        lines += ["## The rejection", "", "> " + r["rejection"].strip().replace("\n", "\n> ")[:1500], "",
                  "Which prong it names, and what that means for the fix: <read it against the table in "
                  "references/4-3-spam.md and write two or three sentences>", ""]
    if r["similarity"]:
        s = r["similarity"]
        lines += [f"4.3 clone-signal score: **{s['score']}/100 ({s['verdict']})**, signal coverage {int(s['coverage'] * 100)}%"]
        if r.get("prongs"):
            lines.append("Per prong: " + " · ".join(f"{k.replace('_', ' ')} {v if v is not None else 'n/a'}" for k, v in r["prongs"].items()))
        if s["nearest_neighbours"]:
            lines.append("Nearest: " + ", ".join(f"{n['trackName']} ({n['score']})" for n in s["nearest_neighbours"][:3]))
        lines.append("")
    if r["areas"]:
        lines += ["| Area | High | Medium | Low |", "|---|---|---|---|"]
        lines += [f"| {a} | {c['HIGH']} | {c['MEDIUM']} | {c['LOW']} |" for a, c in r["areas"].items()]
        lines.append("")
    groups = (("P0 — fix before submitting", "HIGH"), ("P1 — fix or be ready to explain", "MEDIUM"), ("P2 — tidy up", "LOW"))
    n = 0
    for label, sev in groups:
        items = [f for f in r["findings"] if f["severity"] == sev]
        if not items:
            continue
        lines += [f"## {label}", ""]
        for f in items:
            n += 1
            lines.append(f"{n}. **{f['title']}** ({f['guideline']}, {f['area']})")
            lines += [f"   - {e}" for e in f["evidence"][:4]]
            lines += [f"   - Fix: {f['fix']}", ""]
    lines += ["## App Review notes — draft", "", "```", r["review_notes"], "```", "",
              "Fill every <placeholder>. Keep it short; the reviewer reads it before opening the app.", "",
              f"_{r['disclaimer']}_"]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--similarity", help="similarity_score.py JSON output")
    p.add_argument("--privacy", help="privacy_check.py JSON output")
    p.add_argument("--completeness", help="completeness_scan.py JSON output")
    p.add_argument("--listing", help="listing JSON, used for the review-notes draft")
    p.add_argument("--rejection", help="the rejection letter as a text file, quoted in the report")
    p.add_argument("--format", choices=["json", "md"], default="md")
    args = p.parse_args()
    if not any([args.similarity, args.privacy, args.completeness]):
        p.error("give at least one scan output")
    rejection = open(args.rejection, encoding="utf-8").read() if args.rejection else None
    r = build(load(args.similarity), load(args.privacy), load(args.completeness), load(args.listing), rejection)
    print(to_markdown(r) if args.format == "md" else json.dumps(r, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
