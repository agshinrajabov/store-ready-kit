# Agent eval 03 — keyword research for a new app

**Skill:** aso-research · **Network:** yes (public iTunes endpoints)

## Prompt

> I'm launching Belayer, an app that helps climbers find a belay partner at their gym tonight (verified belay
> certification, session planning, safety check-in). US and UK first. What should my name, subtitle and keywords
> be? Can I put "Mountain Project" in the keywords since climbers search for it?

## Pass criteria

1. Runs expand → score (both storefronts) → pack → char_lint; the recommendation's `char_lint` line passes.
2. Refuses "Mountain Project" (competitor name, 2.3.7) and offers the job-based alternative.
3. Name is brand-first with at most one descriptor; subtitle is a promise; no word repeats across the three fields.
4. Keyword table labels popularity/difficulty as proxies; includes per-storefront differences.
5. Category recommendation with chart-depth numbers and the fetch date.
6. Disclaimer present.

## Fail signals

- Any variant over a limit or containing a competitor name, price or "best".
- Presents proxies as search volumes.
