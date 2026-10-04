# App preview video: a 15–30 second script

Last checked: **2026-10-04** · source: App Store Connect Help "App preview specifications" and Apple's App
Previews page

## The rules

- **15–30 seconds**, up to **three previews per language**, max 500 MB, H.264 or ProRes 422 (HQ), up to 30 fps.
- **Footage captured on device** from the app itself. The preview shows the app's features, functionality and
  UI. Keep live-action footage of people, hands holding phones, and anything not in the app out of it.
- Text overlays and narration are allowed. They describe what is on screen.
- The **poster frame** (default at 5 seconds) shows when the video does not autoplay. Choose it as carefully as
  screenshot 1.
- A preview autoplays muted in search results and replaces the first screenshots there. If the first 3 seconds
  are weak, it costs more than it gains.

## Structure (24 seconds as an example)

| Time | Beat | On screen | Overlay |
|---|---|---|---|
| 0–3 s | Hook | The app's most distinctive moment, mid-action | Optional, ≤ 5 words |
| 3–10 s | Core action | One continuous take of the main thing the user does | The outcome, ≤ 6 words |
| 10–17 s | The differentiator | The feature only this app has, clearly visible | ≤ 6 words |
| 17–22 s | Result | What the user has at the end (the park, the plan, the photo) | ≤ 6 words |
| 22–24 s | Close | A calm last frame of the app (no logo slate needed) | none |

## Script template

```
Preview <n> — <storefront / language> — <length> s — poster frame at <s> s: <what it shows>

0:00  SHOT: <what the screen shows, which screen, which action>   OVERLAY: <text or none>   AUDIO: <music / sfx>
0:03  SHOT: …
…
Capture notes: device <model>, OS <version>, demo data <what>, Do Not Disturb on, status bar <clean: 9:41, full battery>.
```

## Checks before export

- Works muted (most views are muted): the overlays and footage carry the story without sound.
- Every feature shown is in the current build (2.3.1).
- No prices, rankings or other platforms in overlays (2.3.7, 2.3.10).
- One preview per device class you upload. Capture at that class's resolution.
