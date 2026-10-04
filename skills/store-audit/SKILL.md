---
name: store-audit
description: Pre-submission App Store audit that predicts rejections before Apple does. Use when an iOS app is about to be submitted or resubmitted, after a rejection (especially Guideline 4.3 spam / "similar to other apps", 2.1 completeness, 5.1 privacy, 2.5.2), when an app was vibe-coded or built from a template or app builder, or when asked "will this pass review", "is my app ready for the App Store", "why was my app rejected". Runs a 4.3(b) differentiation audit against the app's real competitors from the iTunes Search API, a completeness and placeholder scan, a metadata accuracy check, a permissions / purpose-string / privacy-policy consistency check, and a runtime code-download risk interview, then writes a scored report, a prioritised fix list and an App Review notes draft.
---

# store-audit

Find what App Review will object to, while it is still cheap to fix. The heart of it is Guideline 4.3(b):
does this app look like something the store already has, or like a low-effort package?

**Never promise approval.** Every report ends with: *Guidance based on public App Review Guidelines; Apple's
decisions are their own.* Never suggest hiding anything from review, rotating bundle IDs or accounts, or
keyword tricks — the fix is always making the app genuinely complete, accurate and different.

## Inputs to gather first

1. The project repo (path).
2. The store listing draft: name, subtitle, keywords, description, screenshot captions and what each frame
   shows, privacy policy URL, IAP list, login requirement. Write it as `listing.json`
   (format: `references/listing-format.md`). Ask for what is missing; don't invent it.
3. Any rejection letter, verbatim.
4. Whether you can run the build (simulator or device). If not, the manual checks are marked **not checked**.

Work in `store-audit/<date>/` inside the project (or any scratch folder when there is no repo) and keep the
full set there: `listing.json`, `competitors.json`, `similarity.json`, `completeness.json`, `privacy.json`,
`store-audit.md`.

**No repo?** Run steps 0–3 and the listing part of step 4; mark step 5 and the project scans **not checked**.

## Workflow

### 0. Read the letter (only after a rejection)
Match its wording to the table "Reading a 4.3 letter" in `references/4-3-spam.md`: which prong, and what kind
of answer it needs. Update `listing.json` from it — the rejection you are answering counts in
`account.prior_4_3_rejections`. Often this step alone answers the user's question; say so first in the report.

### 1. Competitors (4.3)
Pick 2–6 search terms a user would type for the app's *job*, plus the category's generic term.

```bash
python3 scripts/competitor_scan.py --term "climbing partner" --term "belay partner" --term "climbing app" \
  --country us --limit 50 -o competitors.json
```

Open the top 10 by rating count. For each, note the first three screenshots (`firstScreenshots` URLs in the
snapshot) as concepts — what is shown, not pixels — the icon pattern and the business model. If you cannot open
images, write "screenshots not checked". Drop off-niche results by listing their IDs in `exclude_ids` in
`listing.json` (or `--exclude-id`), and record which and why.

### 2. Template traits
Choose the catalogue that fits (`hypercasual-game`, `utility-app`, `ai-wrapper`;
`python3 scripts/similarity_score.py --list-catalogs`). Fill `traits` in `listing.json` **from the running
app on a fresh install**, plus `monetisation`, `content`, `account`. If no catalogue fits, write the niche's
shared traits as a table in the report and skip the trait signal — do not invent a score.

### 3. Score
```bash
python3 scripts/similarity_score.py --listing listing.json --competitors competitors.json --format md
python3 scripts/similarity_score.py --listing listing.json --competitors competitors.json > similarity.json
```
Read `references/clone-signals.md` for what each signal means and the verdict rules. Below 60% coverage,
say the score is weak and why.

### 4. Completeness, metadata, code download
```bash
python3 scripts/completeness_scan.py --project . --listing listing.json > completeness.json
```
Then the manual crash-surface pass in `references/completeness-checklist.md` (fresh install, iPad, permissions
denied, airplane mode, empty states, login, purchases). Run the 2.5.2 interview in
`references/code-download-2-5-2.md` with the developer and record the answers.

### 5. Privacy
```bash
python3 scripts/privacy_check.py --project . --policy privacy.html > privacy.json   # offline
python3 scripts/privacy_check.py --project . --policy-url https://… > privacy.json # fetches the URL live
```
Confirm every HIGH by opening the file it cites. Remind the developer to compare App Privacy answers in App
Store Connect by hand (`references/privacy-5-1.md`).

### 6. Report
```bash
python3 scripts/audit_report.py --similarity similarity.json --completeness completeness.json \
  --privacy privacy.json --listing listing.json [--rejection letter.txt] > store-audit.md
```
The script writes the header, findings and a notes draft. Keep its structure and add the sections it cannot
write:

- **The answer to the user's question**, first, in plain words (e.g. "No — reply-and-resubmit does not answer
  this letter, because…").
- **Differentiation section (the core).** The nearest neighbours, the niche's shared package as a short table,
  where this app matches it, and **3–5 concrete differentiation moves** ranked by impact ÷ effort. Each move names
  a screen or asset and what changes on it ("frame 1 shows the ride mid-unfold on paper", not "improve visuals").
  Start from the idea that is already the app's own — often it is in the name or the core mechanic and missing
  from the screen.
- **Which 4.3 prong is at risk** (indistinguishable vs low-effort) and why — `references/4-3-spam.md`.
- Manual checks: passed / failed (with device and steps) / not checked (with reason).
- The App Review notes draft, filled in (`references/review-notes.md`). After a rejection the notes describe the
  *next* build; only list changes that will really be in it.
- Read the per-prong scores, not only the total: a low-effort FLAG can sit beside a low total when the store
  text is original.
- The disclaimer line, last.

## Judgement rules

- A FLAG from the script is a reason to look harder, not a verdict on its own; a PASS does not clear a
  first session that is broken or monetisation-first. Say where you disagree with the script and why.
- Facts vs inference: label anything inferred from case patterns as inference.
- Never cite statistics that have no source (e.g. "4.3 is 28% of rejections").
- If the app is in a category 4.3(b) names, the burden is on the app: name the one experience nobody else offers
  and check it is visible in screenshot 1 and in the first minute.
- After a 4.3 rejection, stop at the audit and hand over to `submission-pilot` for the reply and resubmission
  strategy. Do not recommend resubmitting the same build.
- Visual differentiation work: recommend running `no-slop-design` for the visual pass; do not redesign here.

## Output

`store-audit.md` with: verdict and readiness score, 4.3 section, P0/P1/P2 fix list (each with guideline number,
evidence, fix), manual-check table, 2.5.2 interview answers, App Review notes draft, disclaimer. Keep the
JSON outputs and the competitor snapshot beside it so the run can be reproduced.

## References

- `references/4-3-spam.md` — 4.3(a)/(b), related rules, case patterns, reading a 4.3 letter
- `references/clone-signals.md` — the nine signals, verdict rules, trait catalogues, competitor-set rules
- `references/completeness-checklist.md` — 2.1 crash surface, 2.2, 2.3, 4.2 manual pass
- `references/privacy-5-1.md` — 5.1.1, 5.1.2, 4.8, privacy manifest, purpose strings
- `references/code-download-2-5-2.md` — the runtime code-download interview
- `references/listing-format.md` — `listing.json`
- `references/review-notes.md` — writing App Review notes

Every reference states the guidelines revision it summarises (8 June 2026) and the date it was last checked.
If Apple has published a newer revision, say so in the report and re-check the cited numbers.
