#!/usr/bin/env python3
"""Run the store-ready-kit eval suite.

Every case in evals/cases/*.json names a skill script, its inputs (fixtures, all offline) and what the
output must satisfy. The suite is deterministic: frozen competitor snapshots, no network, no model.

Groups (from the spec):
  golden-rejection  real rejections that must be FLAGGED
  golden-approved   well-known approved listings that must not be flagged
  hard              near-clone boundary cases
  privacy / completeness / charlimit   per-check golden cases

Agent-level cases (judged by a person or a model against a rubric) live in evals/agent/*.md and are not
run here.

Examples:
  run_evals.py                 # everything
  run_evals.py --group hard    # one group
  run_evals.py --case a-unfold-puzzle-4-3b -v
  run_evals.py --report evals/runs/latest.md
"""

import argparse
import glob
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
SEV = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, None: 0}


def load_module(skill, script):
    path = os.path.join(REPO, "skills", skill, "scripts", script + ".py")
    spec = importlib.util.spec_from_file_location(f"{skill}_{script}".replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fx(rel):
    return os.path.join(ROOT, "fixtures", rel) if rel else None


def read_json(rel):
    with open(fx(rel), encoding="utf-8") as fh:
        return json.load(fh)


def run_case(case):
    kind = case["run"]
    if kind == "similarity":
        mod = load_module("store-audit", "similarity_score")
        listing = read_json(case["listing"])
        snap = read_json(case.get("competitors") or listing["niche_snapshot"])
        return mod.run(listing, snap, case.get("catalog"), listing.get("exclude_ids", []))
    if kind == "privacy":
        mod = load_module("store-audit", "privacy_check")
        policy = None
        if case.get("policy"):
            with open(fx(case["policy"]), encoding="utf-8") as fh:
                policy = fh.read()
        return mod.check(fx(case["project"]), policy)
    if kind == "completeness":
        mod = load_module("store-audit", "completeness_scan")
        findings = []
        if case.get("project"):
            findings += mod.scan_project(fx(case["project"]), exclude=[fx(case.get("listing"))])
        if case.get("listing"):
            findings += mod.scan_listing(read_json(case["listing"]))
        return {"findings": findings}
    if kind == "report":
        rep = load_module("store-audit", "audit_report")
        sim = priv = comp = None
        listing = read_json(case["listing"]) if case.get("listing") else None
        if listing and listing.get("niche_snapshot"):
            sim = run_case({"run": "similarity", "listing": case["listing"]})
        if case.get("project"):
            priv = run_case({"run": "privacy", "project": case["project"], "policy": case.get("policy")})
        comp = run_case({"run": "completeness", "project": case.get("project"), "listing": case.get("listing")})
        out = rep.build(sim, priv, comp, listing)
        out["report_markdown"] = rep.to_markdown(out)
        return out
    if kind == "script":
        mod = load_module(case["skill"], case["script"])
        def res(v):
            if isinstance(v, str) and v.startswith("FIX/"):
                return fx(v[4:])
            if isinstance(v, list):
                return [res(x) for x in v]
            return v
        args = {k: res(v) for k, v in case.get("args", {}).items()}
        return getattr(mod, case.get("function", "evaluate"))(**args)
    raise SystemExit(f"unknown run kind {kind}")


def check(case, out):
    exp = case["expect"]
    fails = []
    if "verdict" in exp and out.get("verdict") != exp["verdict"]:
        fails.append(f"verdict {out.get('verdict')} != {exp['verdict']}")
    if "verdict_in" in exp and out.get("verdict") not in exp["verdict_in"]:
        fails.append(f"verdict {out.get('verdict')} not in {exp['verdict_in']}")
    if "min_score" in exp and out.get("score", 0) < exp["min_score"]:
        fails.append(f"score {out.get('score')} < {exp['min_score']}")
    if "max_score" in exp and out.get("score", 100) > exp["max_score"]:
        fails.append(f"score {out.get('score')} > {exp['max_score']}")
    if "top_signals_include" in exp:
        ranked = [s["key"] for s in sorted(out["signals"], key=lambda s: -(s["points"] / s["max"]) if s["assessed"] else 1)]
        top = ranked[: exp.get("top_n", 4)]
        for k in exp["top_signals_include"]:
            if k not in top:
                fails.append(f"signal '{k}' not in top {len(top)}: {top}")
    if "hard_trigger_contains" in exp:
        joined = " | ".join(out.get("hard_triggers", []))
        for frag in exp["hard_trigger_contains"]:
            if frag not in joined:
                fails.append(f"hard triggers lack '{frag}': {joined or 'none'}")
    findings = out.get("findings", [])
    titles = [f"{f['severity']} {f['guideline']} {f['title']}" for f in findings]
    for frag in exp.get("findings_include", []):
        if not any(frag.lower() in t.lower() for t in titles):
            fails.append(f"missing finding '{frag}'")
    for frag in exp.get("findings_exclude", []):
        hit = [t for t in titles if frag.lower() in t.lower()]
        if hit:
            fails.append(f"unexpected finding '{frag}': {hit[0]}")
    if "max_severity" in exp:
        worst = max((SEV[f["severity"]] for f in findings), default=0)
        if worst > SEV[exp["max_severity"]]:
            fails.append(f"worst severity {worst} above {exp['max_severity']}: {titles[:3]}")
    if "all_within_limits" in exp and not out.get("all_within_limits"):
        fails.append(f"limit violations: {out.get('violations')}")
    if "report_verdict" in exp and out.get("verdict") != exp["report_verdict"]:
        fails.append(f"report verdict {out.get('verdict')} != {exp['report_verdict']}")
    if "report_contains" in exp:
        for frag in exp["report_contains"]:
            if frag not in out.get("report_markdown", ""):
                fails.append(f"report lacks '{frag}'")
    for frag in exp.get("violations_include", []):
        if not any(frag.lower() in str(v).lower() for v in out.get("violations", [])):
            fails.append(f"no violation mentioning '{frag}': {out.get('violations')}")
    for frag in exp.get("warnings_include", []):
        if not any(frag.lower() in w.lower() for w in out.get("warnings", [])):
            fails.append(f"no warning mentioning '{frag}': {out.get('warnings')}")
    gl = [i["guideline"] for i in out.get("items", [])]
    for g in exp.get("items_include", []):
        if g not in gl:
            fails.append(f"checklist lacks {g}")
    for g in exp.get("items_exclude", []):
        if g in gl:
            fails.append(f"checklist should not include {g}")
    for w in exp.get("pack_excludes", []):
        if w in out.get("words", []):
            fails.append(f"pack contains '{w}': {out.get('keywords')}")
    for pair in exp.get("pack_not_both", []):
        if all(w in out.get("words", []) for w in pair):
            fails.append(f"pack reassembles {pair}: {out.get('keywords')}")
    for w in exp.get("pack_includes", []):
        if w not in out.get("words", []):
            fails.append(f"pack lacks '{w}': {out.get('keywords')}")
    if "equals" in exp:
        for k, v in exp["equals"].items():
            if out.get(k) != v:
                fails.append(f"{k} = {out.get(k)!r}, expected {v!r}")
    return fails


def summary(case, out):
    if out.get("tool") == "rejection_triage":
        return f"{out['path']} / {out['risk']}"
    if out.get("tool") == "message_lint":
        return f"{'OK' if out['ok'] else 'BLOCKED'}, {len(out['warnings'])} warnings"
    if out.get("tool") in ("plan_lint", "asset_check"):
        return f"{'OK' if out['ok'] else 'BLOCKED'}, {len(out['violations'])} blocking, {len(out['warnings'])} warnings"
    if out.get("tool") == "preflight":
        return f"{out['count']} checks"
    if "readiness" in out:
        return f"{out['verdict']} {out['readiness']}"
    if "verdict" in out and "score" in out:
        return f"{out['verdict']} {out['score']}"
    if "characters" in out:
        return f"{out['characters']}/{out['limit']} chars, {len(out['words'])} words"
    if out.get("tool") == "char_lint":
        return f"{len(out['results'])} variants, {len(out['violations'])} blocking"
    if "findings" in out:
        c = {s: sum(1 for f in out["findings"] if f["severity"] == s) for s in ("HIGH", "MEDIUM", "LOW")}
        return f"H{c['HIGH']} M{c['MEDIUM']} L{c['LOW']}"
    return ""


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--group")
    p.add_argument("--case")
    p.add_argument("--skill")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--report", help="also write a markdown report to this path")
    args = p.parse_args()

    cases = []
    for path in sorted(glob.glob(os.path.join(ROOT, "cases", "*.json"))):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        cases += data if isinstance(data, list) else [data]
    if args.group:
        cases = [c for c in cases if c["group"] == args.group]
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
    if args.skill:
        cases = [c for c in cases if c.get("skill", "store-audit") == args.skill]

    rows, failed = [], 0
    for case in cases:
        try:
            out = run_case(case)
            fails = check(case, out)
        except Exception as exc:  # a crashing script is a failed case, not a crashed suite
            out, fails = {}, [f"error: {exc!r}"]
        ok = not fails
        failed += not ok
        rows.append((case, ok, summary(case, out), fails))
        mark = "PASS" if ok else "FAIL"
        print(f"{mark}  {case['group']:<17} {case['id']:<38} {summary(case, out)}")
        if fails or args.verbose:
            for f in fails:
                print(f"      - {f}")
        if args.verbose and out.get("signals"):
            for s in out["signals"]:
                if s["assessed"]:
                    print(f"      {s['key']:<18} {s['points']:>5}/{s['max']:<3} {s['evidence'][0][:100]}")
            if out.get("hard_triggers"):
                print(f"      hard: {out['hard_triggers']}")

    total = len(rows)
    print(f"\n{total - failed}/{total} passed")
    if args.report:
        os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(f"# Eval run\n\n{total - failed}/{total} passed\n\n| Result | Group | Case | Output | Notes |\n|---|---|---|---|---|\n")
            for case, ok, summ, fails in rows:
                fh.write(f"| {'PASS' if ok else 'FAIL'} | {case['group']} | {case['id']} | {summ} | {'; '.join(fails)} |\n")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
