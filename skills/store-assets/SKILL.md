---
name: store-assets
description: Plans the App Store product page assets that decide whether people tap — the first three screenshots, the full screenshot narrative, caption copy, the icon brief and a 15–30 second app preview script — and checks the exported files against Apple's sizes and rules. Use when making or redoing App Store screenshots, captions, an app icon or a preview video, when conversion from search is low, or after store-audit / a 4.3 rejection says the store page looks like everyone else's. Plans in words first, lints the plan, then hands the visual pass to no-slop-design.
---

# store-assets

Decide what the product page has to say before anyone designs it, make the first three frames do the work,
and make sure the files will upload.

**Rules.** Frame 1 is the app in use, never title art. Captions describe outcomes the frame can prove. No
prices, rankings, "free", other platforms or other apps' names anywhere in the assets (2.3.7, 2.3.10). This
skill plans and checks. It does not do the visual design. For the visual pass, run `no-slop-design` with
this skill's plan and briefs.

## Inputs

1. What the app does and for whom. Its differentiator (from `store-audit` if it ran).
2. The current screenshots, icon and any preview, if they exist.
3. The competitor snapshot from `store-audit` (`competitors.json`), or run its `competitor_scan.py`.
4. Words users use, from `aso-research`'s review mining, if available.
5. Supported devices (iPhone / iPad) and languages.

## Workflow

Keep everything in `assets/<date>/` at the project root (or a scratch folder with no project). Languages: if
the user has not said, ask. If there is no answer, plan for the primary market's language and say so.

0. **Current assets** (if any): describe the current frames as a plan, run `plan_lint.py` on it, and list what
   fails. That is the before picture.
1. **Three sentences**: core outcome, differentiator, the user's doubt
   (`references/screenshot-narrative.md`, step 1).
2. **Niche pattern**: take the 10 apps that rank highest on the app's most relevant search terms (not by rating
   count). Leave out apps from other categories. Describe their first three frames and icons as concepts, not
   pixels, and write down what they share. You need image URLs: `firstScreenshots` and `artworkUrl512` in a
   snapshot from the current `competitor_scan.py`. If the snapshot is older and lacks them, re-run the scan, or
   ask the user for screenshots. If neither is possible, infer from descriptions, label every visual claim
   **not observed**, and have the user confirm the pattern by eye before the visual pass.
3. **Narrative plan**: the moment map → frame order → captions (`references/caption-copy.md`). Write it as
   `plan.json` and run:
   `python3 scripts/plan_lint.py --plan plan.json`
   Fix every BLOCK. Rewrite captions that get a stock-phrase or feature-list warning.
4. **Icon brief**: `references/icon-brief.md`. Include the niche pattern and how this icon departs from it.
5. **Preview script** (optional, only if the first 3 seconds can be strong): `references/preview-video.md`.
6. **Visual pass**: write the hand-over to `no-slop-design` (plan, niche pattern, icon brief). Run it only once
   real captures from the build exist. Otherwise the hand-over is the output. Say so plainly if it is not
   installed.
7. **File check** after export. In a planning turn, write "not run, no exports yet" and the command:
   `python3 scripts/asset_check.py <screens…> --icon icon-1024.png --platform iphone [--platform ipad]`

## Output: `store-assets.md`

1. The three sentences.
2. Niche pattern table (what competitors' first frames and icons share) and the one-line "how we differ".
3. Screenshot plan: one row per frame with job, what it shows, real UI yes/no, caption, and word count. Then
   the `plan_lint` result line.
4. Caption alternatives for frames 1–3 (two each), all passing the caption tests.
5. Icon brief.
6. Preview script, or the reason to skip a preview for now.
7. Hand-over to the visual pass, and after export the `asset_check` result.
8. Footer: *Guidance based on public App Review Guidelines; Apple's decisions are their own.*

## Judgement

- Frames that depend on UI you have not seen (a highlight, a locked state) are **conditions the user must
  confirm in the build**. List them. Never plan a frame showing UI the build does not have (2.3.1).
- Caption test 4 (the user's words) needs review mining from `aso-research`. Without it, mark that test
  "not run".
- If the differentiator cannot be seen in a frame, the problem is the product or the UI, not the screenshots.
  Say so, and send it back to `store-audit`.
- Prefer a caption-free frame 1 when the image is distinctive. Use a caption when the outcome needs words.
- Converge on what the market needs to see (readable outcome, real UI). Diverge in how it looks.
- Localise captions per supported language in the user's words. Never add a language the app does not support.

## References

- `references/first-three-screenshots.md`: why three, what fails, formats and sizes
- `references/screenshot-narrative.md`: the planner, step by step, and the plan format
- `references/caption-copy.md`: outcome over feature, tests, voice
- `references/icon-brief.md`: brief fields, niche comparison, review test
- `references/preview-video.md`: Apple's rules, a 24-second structure, script template
