# App Review notes — how to write them

Last checked: **2026-10-04** · relates to 2.1 (demo accounts, back end on), 4.3(b) (stating the difference)

The notes field is read before the app is opened. It is the only place you can tell the reviewer what to look
at. Keep it under ~150 words unless the app genuinely needs more.

## Structure

1. **One sentence:** who the app is for and what it lets them do.
2. **Access:** demo account with full access and no expiry, or how to use the app without one. Say if the account
   has data pre-loaded and what.
3. **Path to the core feature:** 3–6 numbered taps from launch.
4. **What is different** (only if the category is crowded or the app could be mistaken for one): two or three
   things the reviewer can see, in plain words. No marketing.
5. **Non-obvious things:** hardware needed, region limits, features needing two accounts, why a permission is
   asked.
6. **After a rejection:** what changed, in a short list, with the guideline it answers.

## Do

- Write like a colleague handing over a build. Plain, short, specific.
- Point to evidence: a 60–90 second screen recording link of the core flow is often the fastest way to show it.
- Mention TestFlight testing if a rejection letter asked for it: tester count, length, what changed because of it.

## Don't

- Argue with the guidelines or claim the app "fully complies".
- Use superlatives, the app's marketing copy, or competitor names.
- Promise features that are not in this build.
- Ask for approval, mention deadlines or launches, or plead.

`audit_report.py` drafts the notes from the listing JSON; fill every `<placeholder>` and cut what does not apply.
