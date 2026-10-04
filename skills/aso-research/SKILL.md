---
name: aso-research
description: App Store keyword research and metadata from public data, for indie developers without paid ASO tools. Use when asked for ASO, App Store keywords, an app name or subtitle, the 100-character keyword field, which category to pick, why an app does not show up in search, or how to rank in another country. Expands seeds with App Store autocomplete, mines competitor reviews, scores keywords per storefront (popularity proxy, difficulty, relevance, opportunity), packs the keyword field, and proposes name / subtitle / keyword variants that always pass a character-limit and 2.3.7 linter. Refuses keyword stuffing, competitor names, and any tactic that breaks Apple's rules.
---

# aso-research

Find the words real users type for what the app does, where a small app can rank, and fit them into the
30-character name, the 30-character subtitle and the 100-character keyword field without waste or rule-breaking.

**Hard rules.** Every proposed name, subtitle and keyword field goes through `scripts/char_lint.py` and
passes before it is shown. Never propose competitor names, trademarks, prices, "#1"/"best", or irrelevant
terms. Refuse those tactics even when asked (`references/prohibited-tactics.md`). Popularity and difficulty are
proxies from public data, so call them proxies every time and never present them as search volumes.

## Inputs

1. What the app does, for whom, in the developer's words, plus the current listing if one exists (`listing.json`,
   same format as `store-audit`).
2. Launch storefronts and the languages the app really supports.
3. The App Store ID if the app is live (so its current rank can be reported).
4. A competitor snapshot, if `store-audit` already made one (`competitors.json`).

## Workflow

Keep every file in `aso/<date>/` at the project root (or a scratch folder). Commands below are relative to
this skill's folder. Read `references/keyword-method.md` once before starting. It explains each step and how
to read the numbers.

0. **Competitors**: `python3 scripts/keyword_rank.py apps --term "<job term>" --term … --country us -o apps.json`
   This gives competitor IDs for step 3 and the snapshot that `char_lint.py --competitors` needs. You can
   also use `store-audit`'s `competitors.json`.
1. **Seeds**: 5–10 words for the app's job, written as a user would type them.
2. **Expand**: `python3 scripts/keyword_rank.py expand --seed … --country us -o expand.json`
   Remove app names, other jobs and unsupported languages. Keep 20–40 candidates as `shortlist.json` (a list of
   terms). In a niche, autocomplete is mostly app names, so expect to write much of the shortlist by hand.
3. **Reviews**: `python3 scripts/keyword_rank.py reviews --app-id <top 2–3 competitors from apps.json> --format md`
   Add the phrases users actually use, but never competitor names that show up among them. Keep complaint words
   separately for `store-assets`. If the direct competitors have no reviews, mine the closest adjacent apps and
   say so.
4. **Score**: `python3 scripts/keyword_rank.py score --keywords shortlist.json --app-text listing.json --country us[,gb…] -o scores.json`
   Do a quick pass with `--no-popularity` first (about 2 s per term per storefront), then probe popularity only
   for the 15–20 best terms (roughly 10–30 s each per storefront). Correct relevance by hand where the
   calculation is wrong (`--relevance overrides.json`). Rows marked `blocked` are competitor names, and a term
   blocked in one storefront stays out everywhere.
5. **Variants**: 3 names, 3 subtitles (`keyword-method.md` §6), then a keyword field for each pair **and each
   localisation** (en-US and en-GB are separate fields):
   `python3 scripts/keyword_pack.py --scores scores.json --country us --competitors apps.json --name "…" --subtitle "…"`
   It drops terms with relevance below 0.5 and never reassembles a blocked brand. If it reports free
   characters, add relevant words by hand.
6. **Lint**: write all variants to `variants.json` and run
   `python3 scripts/char_lint.py --file variants.json --competitors apps.json` (give each variant a `label`)
   Fix and re-run until it passes. WASTE warnings are worth fixing. LIMIT and BLOCK must be fixed.
7. **Category**: recommend a primary and a secondary category (`references/category-choice.md`), with chart
   depth from `python3 scripts/keyword_rank.py charts --genre <id> --genre <id> --country us,gb`.

## Output: `aso-research.md`

1. **Recommendation**: one name, one subtitle and one keyword field, with character counts and the `char_lint`
   result line.
2. **Alternatives**: the other variants in a table (name · subtitle · keywords · counts · lint).
3. **Keyword table**: the top 25 by opportunity for each storefront. Columns: keyword, popularity proxy,
   difficulty, relevance, opportunity, current rank, and where it is placed (name / subtitle / keywords / not
   used). Add one line explaining that the numbers are proxies.
4. **Why these words**: 3–5 sentences connecting the choice to what users type and what the app does.
5. **Category** recommendation with the chart-depth numbers.
6. **Multi-market notes**: terms that are easy in one storefront and hard in another, plus localisation advice
   for supported languages only.
7. **Refused tactics**: anything the user asked for that this skill would not do, and why.
8. **Measure**: which 5–10 keywords to re-check in 2–4 weeks, and the command to do it.
9. Footer: *Guidance based on public App Review Guidelines; Apple's decisions are their own.* Also the date the
   data was fetched.

## Judgement

- Relevance beats opportunity. A high-scoring keyword that does not describe the app is a 2.3.7 rejection risk
  and a 4.3 signal.
- A new app should not target terms with difficulty above ~70 in the name. Win the long tail first.
- If `store-audit` flagged the name as a keyword stack, the recommended name must fix that. Brand first, at
  most one descriptor.
- If the user's current metadata breaks a rule, say so plainly before proposing anything else.
- The scripts call public Apple endpoints at about one request a second, and slower when Apple throttles.
  Popularity probing costs several calls per term. Budget about 15 minutes for 20 probed terms in two
  storefronts, and keep the rest difficulty-only. In the keyword table, mark difficulty-only rows as such.

## References

- `references/keyword-method.md`: the method, step by step, and how to read the numbers
- `references/metadata-rules.md`: limits, what is indexed, how fields combine, 2.3.7
- `references/category-choice.md`: picking categories, genre IDs, chart depth
- `references/prohibited-tactics.md`: what is refused and the honest alternative
