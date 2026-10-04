# Changelog

## Unreleased

- `aso-research` skill: SKILL.md, four references (method, metadata rules, category choice, prohibited tactics),
  three scripts — `keyword_rank.py` (autocomplete expansion, review mining, per-storefront popularity proxy,
  difficulty, relevance, opportunity, competitor-name blocking), `keyword_pack.py` (100-character field, never
  over), `char_lint.py` (limits, 2.3.7 blocks, waste warnings).
- `submission-pilot` skill: SKILL.md, four references (resubmission strategy and account-risk ladder,
  Resolution Center templates, appeal, review notes), three scripts — `rejection_triage.py` (letter → path and
  account risk), `preflight.py` (checklist for this app's features), `message_lint.py` (notes, replies, appeals).
- `store-audit` fixes from the first agent eval: per-prong sub-scores, missing-field reporting, `exclude_ids`
  read from the listing, unreachable policy URL as a finding, placeholder policy URLs, content-count claims on
  generated content, rejection letter in the report, first screenshots kept in snapshots.
- Evals: 44 script cases (charlimit, triage, messages, preflight added); agent rubrics 03 and 04.

- `store-audit` skill: SKILL.md, seven references (4.3, clone signals, completeness checklist, privacy 5.1,
  runtime code download 2.5.2, listing format, review notes), five scripts — `competitor_scan.py` (iTunes Search
  API), `similarity_score.py` (nine clone signals, combination rules, PASS/WARN/FLAG), `privacy_check.py`
  (code ↔ declarations ↔ purpose strings ↔ policy, privacy manifest, 5.1.1(v), 4.8), `completeness_scan.py`
  (2.1 placeholders and endpoints, 2.3 metadata, 2.5.2, 4.2, 4.2.6), `audit_report.py` (scored report, P0–P2,
  App Review notes draft).
- Evals: harness with 20 script cases (golden rejection, golden approved, hard boundary, privacy, completeness,
  full report) and two agent rubrics. Frozen competitor snapshots for nine niches. Eval run: 20/20.
- Repository structure: four skill folders, evals, docs, install script placeholder.
