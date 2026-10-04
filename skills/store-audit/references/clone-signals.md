# Clone signals — what `similarity_score.py` measures

Last checked: **2026-10-04** · scoring version 1.0

The score is resemblance, not quality. It is built from nine signals; unassessed signals are left out of the
denominator, and `coverage` says how much was assessed. Below 60% coverage, say so in the report.

| Signal | Max | What it reads | Source of the input |
|---|---|---|---|
| `text_similarity` | 15 | Name + subtitle + keywords + description + captions vs every competitor (TF-IDF cosine), relative to how alike the competitors are to each other | competitor snapshot |
| `name_genericness` | 10 | Name words that ≥10% of competitor names share; "Brand: Category Words" pattern; subtitle reusing competitor-name words | snapshot |
| `vocabulary` | 10 | Share of your 25 most-used words that ≥30% of competitor listings also use | snapshot |
| `saturated_category` | 15 | Listing matches a category 4.3(b) names; fewer than two stated differentiators | listing |
| `template_traits` | 20 | Share of the niche's template-trait checklist present on screen | you fill it in, from the running app |
| `monetisation` | 15 | IAP count, consumable ladder, rewarded slots, interstitials, prompts in the first 10 minutes, paywall before value | listing |
| `content` | 10 | Generated content without an authored first session; repeats; silent inputs; little lasting value | listing |
| `lineage` | 15 | Similar apps on the account; template/app generator; copied project; earlier 4.3 rejections | listing |
| `captions` | 5 | Stock phrases in screenshot captions ("relax and unwind", "1000+ levels") | listing |

## Verdict rules

- **FLAG** — score ≥ 55, or any hard trigger:
  - lineage: ≥2 similar apps on the account, a template/app generator, or ≥2 earlier 4.3 rejections;
  - *category package*: template traits ≥ 60% of max **and** monetisation or content ≥ 50% of max
    (the low-effort prong: the niche's template on screen plus a monetisation-first or generated first session);
  - *named category without a difference*: a category 4.3(b) names and fewer than two stated differentiators.
- **WARN** — score 30–54, or a named category with differentiators, or a *store-page twin* (text, name and
  vocabulary all ≥ 80% of max: the product may differ, the page does not).
- **PASS** — everything else. Strong single signals on a PASS still appear as P2 items in the report.

Why combination rules: in the anonymised 4.3(b) case the text of the listing was not close to any competitor
(the mechanic was new), yet the reviewer rejected it. The total alone scored it WARN. The pattern that matched
the letter was the package — template on screen plus monetisation leading the first session — so that pattern is
a rule of its own.

## Template-trait catalogues

Fill these from the running app and the store page, not from intentions. `true`, `false` or `"partial"`.
At least half must be answered or the signal is not assessed. `--list-catalogs` prints them.

**hypercasual-game** (HC01–HC16): stock low-poly geometry · full-chroma primaries · gradient sky / floating island
· outlined candy buttons · white rounded display font with ink outline · hearts row · coin pill with "+" ·
"Level N" title · big PLAY bottom-centre · win card with confetti · fail sheet of coloured offers · stock props ·
default engine post-processing · capture-plus-caption-band screenshots · generated levels with no authored first
session · engine/template splash.

**utility-app** (UT01–UT10): clip-art glyph icon on a gradient · hard paywall before any use · weekly plan
pre-selected · onboarding promising what the app does not do · one list or one button as the whole app · feature
set equal to the niche's top five · name made of category keywords · template UI kit unchanged · rate prompt in the
first session · no empty/offline/error states beyond the template's.

**ai-wrapper** (AI01–AI08): reskinned general chat · value proposition is a model's name · prompt templates as the
only domain content · paywall before the first useful answer · no handling of wrong/slow/unavailable model · same
app under several names · generated icon/screenshots in the AI house style · app-generator scaffold unchanged.

Which catalogue: `hypercasual-game` for free-to-play casual games with a level loop (also premium puzzle games —
most traits will simply be false, which is the point); `utility-app` for single-job tools and trackers;
`ai-wrapper` for chat or generation apps built on a third-party model. A niche without a catalogue: write the traits down in the report as a table (what the top 10 apps all share) and
mark which of them the app has. Do not invent a score for it.

## Choosing the competitor set

- 2–6 search terms a user would type for this app's job, not its brand. Include the category's generic term.
- Same storefront as the primary market. Merge terms; `--limit 50`.
- Exclude your own live app (`--exclude-id`). Drop results that are obviously off-niche before scoring and say
  how many you dropped.
- Freeze the snapshot in the report folder so the score can be reproduced.

## Known limits

- The Search API has no subtitle, keyword field, IAP list or ads flag for competitors.
- Screenshots are not compared as images. The snapshot keeps each competitor's first three screenshot URLs
  (`firstScreenshots`); describe them in the report (concept, not pixels) and compare by hand with yours.
- A high `text_similarity` in a functional niche (to-do, camera, flight tracking) is normal; the approved
  reference apps in the evals score 10–15 there and still pass. Read it together with the other signals.
