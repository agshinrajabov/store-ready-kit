# store-ready-kit

**Your app builds. This kit gets it approved and discovered.**

Four agent skills (the SKILL.md format: Claude Code and compatible agents) that take a mobile app from "it
builds" to "it passed App Review and people can find it". Made for vibe-coders and indie developers who can
ship an app but hit the App Store wall.

| Skill | What it does |
|---|---|
| **`store-audit`** | Predicts rejections before Apple does. A Guideline 4.3(b) differentiation audit against your real competitors (iTunes Search API), completeness and placeholder scan, metadata accuracy, permissions ↔ purpose strings ↔ privacy policy, runtime code-download risk. Scored report, prioritised fixes, App Review notes draft. |
| **`submission-pilot`** | Pre-flight checklist for *your* app's features. Rejection triage: answer, fix, clarify, rework, or stop, with an account-risk level. Resolution Center replies, appeals, and when **not** to resubmit. |
| **`aso-research`** | Keyword research from public App Store data. Name, subtitle and 100-character keyword variants that always pass a character-limit and 2.3.7 linter. |
| **`store-assets`** | The first three screenshots, screenshot narrative, outcome-first captions, icon brief, a 15–30 s preview script, and a file check against Apple's sizes. |

**Guidelines snapshot:** App Review Guidelines revision of **8 June 2026**, last checked **2026-10-04**.
Guidelines change, and staleness is this kit's biggest risk. Every reference file records the guideline numbers
it summarises and the date it was last checked. If Apple has published a newer revision, treat the references
as possibly stale.

> Guidance based on public App Review Guidelines; Apple's decisions are their own. Nothing here promises
> approval, and nothing here helps anyone get around App Review. It helps you make an app that is genuinely
> complete, accurate and different, and explain that clearly to a reviewer.

## Quickstart (60 seconds)

```bash
git clone https://github.com/agshinrajabov/store-ready-kit
cd store-ready-kit && ./install.sh        # symlinks the skills into ~/.claude/skills
```

Restart your agent and ask, in your app's repo:

- *"Audit my app before I submit it to the App Store."* → `store-audit`
- *"Apple rejected my app, here's the letter. What do I do?"* → `submission-pilot`
- *"What should my App Store name, subtitle and keywords be?"* → `aso-research`
- *"Plan my App Store screenshots."* → `store-assets`

Options: `./install.sh --copy`, `--dest <project>/.claude/skills`, `--only store-audit`, `--uninstall`.

Requirements: Python 3.9+, standard library only (nothing to `pip install`). Network only for the public Apple
endpoints the research scripts call. No telemetry.

## Demo

*(A short screen recording of `store-audit` on the anonymised 4.3(b) case goes here.)*

## Why this exists

A growing share of App Store submissions now come from AI-built apps, and Guideline 4.3 (spam) is where many
of them stop. Apple tightened 4.3(b) in June 2026 with a second prong aimed at low-effort apps, and acted
against app-builder platforms the same year. The help available is blog posts and paid consultants. This kit
puts the know-how inside the agent that is already building the app.

Read the story behind it: **[The 4.3(b) playbook](docs/4-3b-playbook.md)**, a real rejection, anonymised, and
what actually works.

## How it is tested

```bash
python3 evals/run_evals.py
```

Deterministic cases, run offline on frozen data, plus agent-level rubrics. The cases include:

- a real 4.3(b) rejection that must be flagged, for the reasons the fix has to move;
- Railbound, Things 3, Halide and Flighty, which must not be flagged;
- near-clone boundary cases: a flashlight with an SOS mode, a screw-puzzle reskin, an AI chat wrapper, a
  climbing-partner app that sounds like dating, an honest game with a stuffed name, and the rejected game after
  its fix;
- rejection letters that must be triaged correctly, including the third-4.3 "stop" case;
- generated metadata that must never exceed Apple's character limits.

No skill is released without passing them. See [`evals/README.md`](evals/README.md) for what they prove
and what they don't.

## What this kit refuses to do

Keyword stuffing, competitor names or trademarks in metadata, fake or incentivised reviews, rating
manipulation, new bundle IDs or accounts to dodge a rejection, hiding features from review, and any "beat
Apple" framing. The skills say no, and explain the honest alternative.

## Related

- [no-slop-design](https://github.com/agshinrajabov/no-slop-design): the visual pass for screenshots and icons.
  `store-assets` plans, no-slop-design designs.

## Contributing

The most valuable contribution is a **real rejection**, anonymised, as an eval fixture. See
[`evals/README.md`](evals/README.md#adding-a-case). Guideline updates are next: open an issue with the
guideline number and what changed.

## License

MIT
