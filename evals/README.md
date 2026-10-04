# Evals

Nothing in `skills/` is released until this suite passes. Run it before every release and paste the summary into
the CHANGELOG entry.

```bash
python3 evals/run_evals.py                  # all cases
python3 evals/run_evals.py --group hard -v  # one group, with signal breakdowns
python3 evals/run_evals.py --report evals/runs/latest.md
```

Python standard library only, no network: competitor data is frozen in `fixtures/niches/*.json`
(iTunes Search API, fetched 2026-10-04).

## Two layers

**Script cases** (`cases/*.json`, run by `run_evals.py`) — deterministic checks on what the scripts output.

| Group | What it proves |
|---|---|
| `golden-rejection` | A real 4.3(b) rejection (anonymised, used with permission) is FLAGGED, for the reasons the fix has to move |
| `golden-approved` | Well-known approved listings (Railbound, Things 3, Halide, Flighty) are not flagged |
| `hard` | Boundary cases: a named category with one trivial addition, a reskin, a different app with dating vocabulary, a deeper app with generic metadata, an AI wrapper, an honest game with a stuffed name, the rejected app after its fix |
| `privacy`, `completeness` | Broken and clean mini projects produce the findings they should and no others |
| `charlimit` | (Phase 2) generated metadata never exceeds Apple's character limits |

**Agent cases** (`agent/*.md`) — the skill run end to end by an agent, judged against a rubric by a person or a
second model. These test the judgement the scripts cannot: which prong is at risk, whether the differentiation
moves are concrete, whether the report stays honest.

## What these evals do not prove

- **The 4.3 FLAG on the golden rejection rests on the trait, monetisation and content inputs**, which come from
  the developer's own audit of the running app. The text-only signals alone would not flag it — its mechanic was
  genuinely new. That is the lesson of the case, not a weakness to hide: a 4.3(b) "low-effort" judgement is about
  the package a reviewer meets, and only someone who opens the app can describe the package.
- Approved apps passing means the scorer does not punish well-made apps in crowded niches. It does not mean a
  PASS predicts approval.
- Thresholds were calibrated on these fixtures. New fixtures — especially new real rejections — are the most
  valuable contribution to this repo.

## Adding a case

1. Freeze inputs under `fixtures/` (strip screenshot URLs from snapshots; anonymise anything private).
2. Add an entry to a file in `cases/` with `expect` fields: `verdict`, `verdict_in`, `min_score`, `max_score`,
   `top_signals_include`, `hard_trigger_contains`, `findings_include`, `findings_exclude`, `max_severity`,
   `report_verdict`, `report_contains`.
3. Write in `note` why the expectation is right. A case whose expectation was chosen to match the output is not
   a test.
