# Changelog

## Unreleased

- `store-audit` skill: SKILL.md, seven references (4.3, clone signals, completeness checklist, privacy 5.1,
  runtime code download 2.5.2, listing format, review notes), five scripts — `competitor_scan.py` (iTunes Search
  API), `similarity_score.py` (nine clone signals, combination rules, PASS/WARN/FLAG), `privacy_check.py`
  (code ↔ declarations ↔ purpose strings ↔ policy, privacy manifest, 5.1.1(v), 4.8), `completeness_scan.py`
  (2.1 placeholders and endpoints, 2.3 metadata, 2.5.2, 4.2, 4.2.6), `audit_report.py` (scored report, P0–P2,
  App Review notes draft).
- Evals: harness with 20 script cases (golden rejection, golden approved, hard boundary, privacy, completeness,
  full report) and two agent rubrics. Frozen competitor snapshots for nine niches. Eval run: 20/20.
- Repository structure: four skill folders, evals, docs, install script placeholder.
