# Agent eval 04 — "Should I appeal?" after a low-effort 4.3(b)

**Skill:** submission-pilot · **Fixture:** `fixtures/letters/low-effort-4-3b.txt`

## Prompt

> Apple rejected my game with this letter. It's my first rejection of this kind, no other apps on my account.
> I'm furious — should I appeal to the App Review Board and tell them the game is original? Draft the appeal.

## Pass criteria

1. Runs `rejection_triage.py` → REWORK / ELEVATED; explains the low-effort prong in plain words.
2. Advises against an originality appeal **and says why**, without refusing to help: offers the rework plan and an
   optional once-only Resolution Center reply instead; if it still drafts an appeal on request, `message_lint`
   flags the originality argument and the agent says so.
3. States clearly: do not resubmit this build; TestFlight round; one resubmission.
4. Calms with facts (no documented termination from one appeal / first 4.3) and names the real danger
   (repeated near-identical resubmissions).
5. Every draft passes `message_lint` (no BLOCKs). Disclaimer present.

## Fail signals

- Drafts a hostile or originality-based appeal without warning.
- Suggests a new bundle ID/account, or resubmitting quickly with cosmetic changes.
