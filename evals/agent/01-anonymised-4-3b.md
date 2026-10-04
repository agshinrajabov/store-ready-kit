# Agent eval 01 — the anonymised 4.3(b) rejection

**Skill:** store-audit · **Fixture:** `fixtures/unfold-puzzle-4-3b/` (listing, rejection record, frozen competitors)

## Prompt

> My puzzle game got rejected under 4.3(b) yesterday. Here is the listing (`listing.json`) and the rejection
> (`rejection.md`). The mechanic is original — nothing else on the store unfolds rides. Can I just reply that it's
> original and resubmit?

## Pass criteria (all required)

1. Runs `similarity_score.py` on the frozen snapshot (no network needed) and reports FLAG with the hard trigger.
2. Identifies the **low-effort / quality prong**, not the saturated-category prong, and explains that "it's
   original" does not answer that letter.
3. Recommends **against** resubmitting the same build, and hands the reply/resubmission plan to
   `submission-pilot`.
4. Gives 3–5 differentiation moves that name concrete screens or assets, ranked, and at least one builds on the
   idea already in the name/mechanic (unfolding, paper) rather than generic "improve the art".
5. Addresses monetisation in the first session with a specific cut (counts, not adjectives).
6. Ends with the disclaimer; never says "this will be approved".

## Fail signals

- Suggests a new bundle ID, a new account, a rename to escape history, or keyword changes as the main fix.
- Cites unsourced statistics.
- Treats the script's score as the verdict without reading the evidence.
