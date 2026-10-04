# Resubmission strategy — what to do after a rejection, and when not to resubmit

Guidelines revision: **8 June 2026** · last checked: **2026-10-04** · numbers: 4.3(a), 4.3(b), 5.6, "After You
Submit" (Timing, Appeals). Case patterns come from public developer cases from 2023–2026, summarised; none is
quoted at length.

## The four channels

| Channel | Cost | Use for |
|---|---|---|
| **Resolution Center reply** | Free. Fast (sometimes minutes). Keeps the thread. | Answering questions, showing a misread, a short factual account of a 4.3 |
| **New build** | A review cycle | Anything that needs a code or metadata change |
| **App Review Board appeal** (one per rejection) | Weeks of silence are documented in 2026. The build is locked meanwhile. | A guideline you believe was misapplied, with factual evidence, once a reply has not resolved it |
| **Meet with Apple: App Review consultation** (Tue/Thu) | A booked slot | Before resubmitting after a 4.3 or a repeated rejection. Ask what specifically must change. |

## Decision tree (what `rejection_triage.py` implements)

1. **Account-level notice** (Code of Conduct, "account under review", termination), **or** a third 4.3 on one
   concept, **or** a 4.3 with two or more similar apps on the account → **STOP.** Submit nothing. Book a
   consultation. Write down the account history. Answer any notice once, in writing, factually, with the
   improvements you plan.
2. **Information request** ("Information Needed", numbered questions) → **ANSWER_ONLY.** Answer in Resolution
   Center, numbered to match. Upload a build only if an answer requires one.
3. **4.3 that says "do not resubmit until significant changes"**, **or** the low-effort / quality wording,
   **or** a second 4.3 on the concept → **REWORK.** See the 4.3(b) doctrine below.
4. **4.3(a)-style similarity or terminated-account lineage** → **CLARIFY.** Reply with facts. If the lineage is
   real (a copied project or a template), fix that first.
5. **4.3(b) saturated category** → **REWORK** (name the meaningful difference and make it visible). If the
   category label is wrong, use **CLARIFY** and show what the app is.
6. **The reviewer missed or misread something** → **CLARIFY.** Reply with exact steps and a recording, and ask
   for a re-review of the same build.
7. **Everything else** (bugs, metadata, privacy, purchases) → **FIX_AND_RESUBMIT.** Fix the issue everywhere in
   the app, not just on the screen they named. Test on the device in the letter. Reply with a numbered list of
   fixes.

## The 4.3(b) doctrine: "significant changes"

Apple does not define "significant changes". Read it as follows, based on what resolved and what failed in
documented cases:

- The **store page and the first five minutes** must look and feel like a different, more finished product.
  Reviewers spend minutes, not hours. Diff size does not count. First impression does.
- **Change the product, not its label.** A rename, a new keyword set or a new icon on the same experience is
  not significant, and doing it quickly reads as evasion.
- **Pause visibly.** Run an external TestFlight round, especially if the letter names TestFlight. Record the
  tester count, how long it ran and what changed because of it.
- **Resubmit once**, with notes that list the changes. That next submission should be one you would defend as
  a different product.
- **Don't argue originality against a quality judgement.** "Nothing else does X" answers the saturated-category
  prong, not the low-effort prong.

## Account-risk ladder

| Level | Signals | Behaviour |
|---|---|---|
| LOW | Functional, metadata or privacy rejection | Fix and resubmit normally |
| ELEVATED | First 4.3, an extended-review paragraph, or "do not resubmit" | One careful resubmission after real changes. No other similar uploads. |
| HIGH | Second 4.3 on the concept, or a 4.3 + extended review + a similar app on the account | Consultation before submitting. Treat the next submission as the last. |
| CRITICAL | Third 4.3, ≥2 similar apps + 4.3, earlier removals, or an account notice | STOP. No uploads. Talk to Apple first. |

Documented terminations followed **rapid, near-identical resubmissions** or **several similar apps on one
account**. No documented case shows a single appeal or a single 4.3 on a first app causing termination. Say
so when a developer is frightened. The real danger is the resubmission loop, not the appeal.

## Never

- A new bundle ID, a new account, or a transfer to escape a rejection history. Apple tracks lineage, and
  evasion is a termination matter.
- Hiding or switching off features for the review build (manipulating review, and concept-switch schemes).
- Several appeals, or appeal plus resubmission plus reply all in the same day.
- Uploading another similar title while a 4.3 is open.
