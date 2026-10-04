# Agent eval 02 — a vibe-coded Expo app before first submission

**Skill:** store-audit · **Fixture:** `fixtures/projects/vibe-expo/` (project, `listing.json`, `privacy.md`)

## Prompt

> I built this calorie app with an AI app builder in a weekend. Is it ready for the App Store?

## Pass criteria (all required)

1. Runs `completeness_scan.py` and `privacy_check.py` and opens the cited files to confirm each HIGH.
2. P0 list includes: missing camera purpose string, sign-up without in-app account deletion, localhost endpoint,
   placeholder text ("Coming soon", lorem), missing privacy policy URL, login without a demo account.
3. Explains the OTA / `eval` findings as a **2.5.2 question** (asks the interview questions) rather than declaring
   a violation.
4. Flags the "Beta", "Free" and "Android" metadata wording with the guideline numbers.
5. Raises 4.2.6/4.3 context for an app-builder scaffold without accusing the developer of spam.
6. Verdict NOT READY; App Review notes draft includes a demo-account section; disclaimer present.

## Fail signals

- Calls the app ready, or buries P0 items among P2 items.
- Recommends disabling features only for the review build (that is review manipulation).
