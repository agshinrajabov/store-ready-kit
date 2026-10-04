# store-ready-kit

**Your app builds. This kit gets it approved and discovered.**

A set of four agent skills (SKILL.md format — Claude Code and compatible agents) that take a mobile app from
"it builds" to "it passed App Review and people can find it":

| Skill | What it does |
|---|---|
| `store-audit` | Rejection prevention: 4.3(b) differentiation audit against your niche, completeness, metadata accuracy, privacy consistency, runtime code download risk |
| `aso-research` | Keyword research from public App Store data, title / subtitle / keyword-field variants that respect the character limits |
| `store-assets` | Screenshot narrative, caption copy, icon brief, preview video script |
| `submission-pilot` | Pre-flight checklist, App Review notes, Resolution Center replies, resubmission strategy, appeal template |

> Status: **pre-release.** `store-audit` is built and passes its evals; the other three skills are in progress.

**Guidelines snapshot:** App Review Guidelines revision of **8 June 2026**, last checked **2026-10-04**. Every
reference file records the guideline numbers it summarises and the date it was last checked. Guidelines change;
if Apple has published a newer revision, treat the references as possibly stale.

## Requirements

Python 3.9+ (standard library only — nothing to `pip install`). Network access only for the iTunes Search API
calls in `competitor_scan.py`.

## Evals

```bash
python3 evals/run_evals.py
```

Golden cases include a real Guideline 4.3(b) rejection (anonymised), four well-known approved apps, and
near-clone boundary cases. See [`evals/README.md`](evals/README.md) for what they do and do not prove.

## What this kit does not do

It does not promise approval, and it does not help anyone get around App Review. It helps you make an app that is
genuinely complete, accurate and different from what is already in the store, and explain that clearly to a reviewer.

*Guidance based on public App Review Guidelines; Apple's decisions are their own.*

## License

MIT
