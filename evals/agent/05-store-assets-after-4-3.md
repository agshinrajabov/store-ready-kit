# Agent eval 05 — redo the screenshots after a 4.3(b)

**Skill:** store-assets · **Fixtures:** `fixtures/plans/template-bad.json` (current frames), `fixtures/niches/unfold-puzzle.json`

## Prompt

> My unfold-puzzle game was rejected under 4.3(b); the audit says my store page looks like every hyper-casual
> game. Here are my current screenshot frames (template-bad.json). Plan new screenshots and an icon brief.

## Pass criteria

1. Runs `plan_lint.py` on the current plan and reports its BLOCKs.
2. Writes the three sentences; frame 1 is real UI showing the differentiator (the hinge unfold) — caption-free
   or ≤ 7 words; frames 1–3 are distinct moments; the new plan passes `plan_lint`.
3. Niche pattern table built from the snapshot (says plainly if images could not be viewed).
4. Icon brief that names the niche pattern and how the icon departs from it.
5. Hands the visual pass to no-slop-design; no prices/rankings/platform names; disclaimer.
