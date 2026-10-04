# App Review Board appeal — when and how

Last checked: **2026-10-04** · Apple's appeal rules: one appeal per rejection, answer outstanding questions
first, give specific reasons the app complies (developer.apple.com/distribute/app-review)

## Appeal only when all are true

1. You believe a guideline was **misapplied**, not merely that you dislike the outcome.
2. You have **facts** that show it: a recording, a document, a licence, the exact steps.
3. A Resolution Center reply did not resolve it, or the letter leaves no room for one.
4. The letter is **not** a quality / low-effort judgement that you plan to fix. Fix it instead.

Expect silence. Waits of three weeks or more are documented in 2026, and the build is locked meanwhile. Do the
rework in TestFlight in parallel if there is any.

## What has worked in documented appeals

- The developer's history in one line, a plain claim that the concept and code are their own, and a gameplay or
  usage video.
- For engine games: why binaries look alike, plus concrete things that are unique in play.
- Short and factual. A polite follow-up is fine; a second appeal is not.

## What has failed

- Arguing "my app is original" when the reviewer's issue was the category label (dating, fortune telling, party
  game) or the quality of the experience.
- An appeal contradicted by the account's own history.

## Template

```
App name: <name>    App ID: <id>    Build: <number>    Rejected under: <guideline>, <date>

Summary
<Two sentences: what the app is, and why the guideline does not apply as stated.>

Specific reasons
1. <Fact> — evidence: <link / attachment>.
2. <Fact> — evidence: <…>.
3. <Fact> — evidence: <…>.

What we already did
<Resolution Center reply on <date>; changes made, if any.>

Contact
<name, email, time zone>. We are glad to join a call.
```

Run `message_lint.py --kind appeal` before sending. If it finds an originality argument against a low-effort
letter, the appeal is the wrong tool.
