# The first three screenshots

Last checked: **2026-10-04** · numbers: 2.3.3, 2.3.7, 2.3.10 · specs: App Store Connect Help, "Screenshot
specifications"

## Why the first three

In search results the App Store shows the icon, name, subtitle, rating and the **first three portrait
screenshots** (or the first landscape one, or an autoplaying preview). Most people decide from that one row, and
a reviewer sees the same row before opening the app. Frames 4–10 are for people who are already interested.

## The rule

**Frame 1 is the app's best moment, in the real UI.** It shows the outcome the user comes for, or the thing only
this app does, at a size readable in a search result.

**Frames 1–3 are three different moments**, together making one story: the outcome, how you get there, and why
this app and not the others. No two frames show the same screen with a different caption.

**After a 4.3 conversation, the differentiator is in frames 1–3.** It should be visible without the caption.

## What fails

| Pattern | Problem |
|---|---|
| Logo or title art as frame 1 | Not the app in use (2.3.3). Spends the frame everyone sees. |
| Onboarding, login or a paywall as frame 1 | Same problem, and it signals friction |
| A level grid, settings or a list of features | Shows the app's structure, not its value |
| The category's standard frame (bright capture + big caption band) | Reads as one of many (a 4.3 similarity signal) |
| Prices, "free", "#1", "best" in captions | 2.3.7 |
| Android devices or other platforms | 2.3.10 |
| Mock UI that the app does not have | 2.3.1 / 2.3.3 |

## Formats (checked 2026-10-04)

- 1–10 screenshots per device class, JPEG or PNG, **no alpha channel**.
- iPhone: provide **6.9"** (1260×2736, 1290×2796 or 1320×2868 portrait). Smaller classes scale down from it.
  6.5" is accepted when 6.9" is missing.
- iPad (if the app runs on iPad): provide **13"** (2064×2752 or 2048×2732 portrait).
- Keep one orientation per set.
- `scripts/asset_check.py` checks all of this.

## Text on screenshots

Captions are allowed and usually help. Keep them to 7 words or fewer, in the app's own voice, and see
`caption-copy.md`. A frame with no caption is fine when the image says it: a strong, distinctive frame 1
often works better without one.
