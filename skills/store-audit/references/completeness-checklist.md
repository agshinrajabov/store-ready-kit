# Completeness and metadata accuracy — manual pass

Guidelines revision: **8 June 2026** · last checked: **2026-10-04** · numbers: 2.1, 2.2, 2.3.1, 2.3.3, 2.3.7, 2.3.10, 4.2

`completeness_scan.py` finds text patterns. It cannot tap anything. This is the pass a person (or the agent
driving a simulator) does on a **fresh install on a real device**, in the order a reviewer meets the app.

## 2.1 — App completeness: the crash surface

Run each with no save data, then again signed in. Note device, OS, build number.

| # | Check | Why it fails review |
|---|---|---|
| 1 | Cold launch, airplane mode on | Spinner forever or crash = 2.1 |
| 2 | Cold launch on the oldest supported OS and the smallest screen; iPad if the app runs there | Reviewers often test on iPad; layouts break, taps miss (a real 2.1 case: the first tap did nothing on iPad) |
| 3 | Deny every permission prompt, then use the feature that needed it | Crash or dead end after "Don't Allow" |
| 4 | Every tab, every button on the first three screens | Buttons that do nothing read as unfinished |
| 5 | Every empty state: no data, no results, no network, no account | Blank screens and raw error strings |
| 6 | Sign up, sign in, sign out, delete account | Login is where most "could not access" rejections start |
| 7 | Every purchase: buy, cancel, restore, sandbox account | Unfinished IAP flows are a 2.1 and a 3.1 problem |
| 8 | Backend on, production URLs, demo account works from another network | "Turn on your back end" is in the guideline itself |
| 9 | Background and return; rotate (if supported); low-power mode | State loss and layout crashes |
| 10 | Links: support, privacy policy, terms — all open and load | Dead URLs are named in 2.1 |

## 2.2 — Betas

No "beta", "demo", "trial version", "test" in the store build or its metadata. Betas go to TestFlight.

## 2.3 — Accurate metadata

| Check | Rule |
|---|---|
| Every feature in the description and screenshots exists in this build | 2.3.1 — hidden or promised features |
| Screenshots show the app in use; not only title art, a splash or a login screen | 2.3.3 |
| No other platform names or icons (Android, Google Play…) | 2.3.10 |
| Name ≤ 30 characters, no prices, no competitor or trademark terms, keywords that describe the app | 2.3.7 |
| What's New describes the changes in this version | 2.3.12 |
| Age rating answers match the content (UGC, chat, gambling-like mechanics, ads) | 2.3.6 |
| In-app purchases visible in the listing are the ones in the build | 2.3.2 |

## 4.2 — Minimum functionality

- If most screens are a website in a web view, the app needs native value of its own (offline use, device
  features, native navigation, notifications that matter).
- A single-feature app (one button, one list) needs a reason to exist as an app; compare with what the niche's
  top five already do.

## Report format for this section

For each failed check: what you did, what happened, on which device, screenshot path, and the fix. A check you
could not run is listed as **not checked** with the reason — never as passed.
