---
name: submission-pilot
description: Gets an iOS app through App Store submission and through rejections. Use before submitting (pre-flight checklist built for this app, guideline by guideline; App Review notes with demo account and test steps), and whenever App Review answers — a rejection, "Information Needed", a Guideline 4.3 spam letter, "do not resubmit until significant changes", an extended-review warning, a Code of Conduct notice. Triages the letter, decides between answering, fixing, clarifying, reworking or stopping, sizes the risk to the developer account, drafts the Resolution Center reply or the App Review Board appeal, and says plainly when NOT to resubmit.
---

# submission-pilot

Submit once, answer rejections calmly, and never turn one rejection into an account problem.

**Never promise approval.** End every output with: *Guidance based on public App Review Guidelines; Apple's
decisions are their own.* Never suggest a new bundle ID or account to escape a rejection, hiding features from
review, or pressuring the reviewer.

## Mode A: before submitting

1. Write `profile.json` (`python3 scripts/preflight.py --example`) from the app's real features. Ask about any
   flag you cannot determine from the repo.
2. `python3 scripts/preflight.py --profile profile.json > preflight.md`. Go through the items with the developer.
   Each item is marked passed, failed (with the fix) or not applicable (with the reason).
   If `store-audit` has run, link its report and don't redo its scans.
3. Draft the App Review notes (`references/review-notes.md`) and lint them:
   `python3 scripts/message_lint.py --kind notes --file notes.txt [--requires-login]`
4. Output `submission.md`: the checklist with results, the notes (lint passing), and anything still open.

## Mode B: App Review answered

0. Get the **full letter verbatim**, and ask: earlier 4.3 rejections on this concept? Other similar apps on the
   account? Any earlier removals? Can the developer show the reviewer missed something?
1. **Triage**
   ```bash
   python3 scripts/rejection_triage.py --letter letter.txt --prior-4-3 N --similar-apps N [--believe-misread]
   ```
   It returns a path (ANSWER_ONLY · FIX_AND_RESUBMIT · CLARIFY · REWORK · STOP), an account risk level, steps
   and things to avoid. Check its reading against `references/resubmission-strategy.md`. If you disagree, say
   why and follow the reference. Low confidence means reading the letter by hand.
2. **Answer the developer's question first, in plain words.** Usually: "Should I resubmit / reply / appeal?"
   Give the path, why, and the risk level in one short paragraph.
3. **Per path:**
   - ANSWER_ONLY: draft the reply (`references/resolution-center.md`), answers numbered to match.
   - FIX_AND_RESUBMIT: a fix list covering the guideline everywhere in the app, a test plan on the device named
     in the letter, and the reply.
   - CLARIFY: the evidence to gather (recording, steps, lineage facts) and the reply. The appeal draft only if a
     reply would not be enough (`references/appeal.md`).
   - REWORK: say clearly **do not resubmit this build**. Run `store-audit` for what to change (or use its
     existing report). Then a plan: changes → external TestFlight → one resubmission, with notes listing the
     changes. An optional, once-only Resolution Center reply. No appeal that argues originality.
   - STOP: no uploads. Book a Meet with Apple App Review consultation, write down the account history, and
     answer any notice once, factually.
4. **Lint every message** before showing it:
   `python3 scripts/message_lint.py --kind reply|appeal|notes --file draft.txt --letter-kind <kind_4_3>`
   Fix all BLOCKs. Explain any WARN you keep.
5. Output `rejection-plan.md`: the answer, the triage (path, risk, guidelines, flags), the steps with owners,
   the drafts (lint passing), what not to do, and when to check back.

## Judgement

- A reply in Resolution Center costs nothing and has flipped real cases. An appeal costs weeks. Rapid
  resubmissions are what have cost accounts.
- After a quality / low-effort 4.3(b), "it's original" is not an answer. Change what the reviewer meets in the
  first five minutes and on the store page.
- Calm the developer with facts: no documented case shows one appeal or one first 4.3 causing termination. The
  documented danger is repeated near-identical submissions and several similar apps on one account.
- Fix the guideline everywhere. A 5.1.1 rejection about one permission usually means checking all of them.
- Label inference as inference. Never invent statistics or appeal success rates (none are published).

## References

- `references/resubmission-strategy.md`: channels, decision tree, the 4.3(b) doctrine, account-risk ladder, never-list
- `references/resolution-center.md`: reply templates by path
- `references/appeal.md`: when to appeal, what has worked, template
- `references/review-notes.md`: review notes skeleton and special situations
