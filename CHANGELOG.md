# Changelog

## 1.0.0 — 2026-10-04

First release: four skills — `store-audit`, `aso-research`, `store-assets`, `submission-pilot` — with
`install.sh`, the 4.3(b) playbook, and the eval suite. Guidelines snapshot: revision of 8 June 2026, checked
2026-10-04.

Eval run before release: **54/54 script cases passed**; agent rubrics 01–05 run once each (all pass criteria
met; their friction reports drove the fixes below).

- `store-assets` skill: SKILL.md, five references (first three screenshots, narrative planner, caption copy,
  icon brief, preview video), `plan_lint.py` (frame-1 rule, distinct moments, 2.3.7/2.3.10 in captions,
  competitor names, award and rating claims) and `asset_check.py` (accepted sizes, alpha, CMYK, counts).
- `aso-research`: `keyword_rank.py apps` (competitor IDs and snapshot) and `charts` (chart-depth medians);
  faster, cached popularity probing with partial credit; a brand split across fields is blocked; the packer never
  reassembles a blocked brand, drops relevance < 0.5, ranks unscored terms sanely and reports free characters.
- `submission-pilot`: originality appeals against a low-effort letter are blocked; any placeholder blocks unless
  `--draft`; `[[FILL: …]]` convention; rejection-plan template; consultation step in REWORK.
- `install.sh`: symlink or copy, `--dest`, `--only`, `--uninstall`; no network, no telemetry.

## Pre-release history

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
