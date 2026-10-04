# Keyword research method — public data only

Last checked: **2026-10-04**

The goal: a shortlist of words that real users type, that describe what the app actually does, and where a new
or small app can rank. Then pack them into 30 + 30 + 100 characters without waste.

## 1. Seeds (5–10)

Write the app's job in the words a user would type, not in the developer's words:
- the task ("find climbing partner"), the object ("belay"), the situation ("climbing gym tonight");
- the category's generic term ("climbing app");
- words from the app's own listing that no competitor uses (from `store-audit`'s vocabulary signal, if run).

## 2. Expand

```bash
python3 scripts/keyword_rank.py expand --seed "climbing partner" --seed belay --seed bouldering --country us -o expand.json
```

Autocomplete shows what people type. Read the list and strike:
- app names (they are other people's brands);
- terms about a different job ("climbing games" for a partner finder);
- terms in languages the app does not support.

Use `--alphabet` only for the 2–3 most important seeds. It makes 26 extra calls per seed.

## 3. Mine reviews

```bash
python3 scripts/keyword_rank.py reviews --app-id <top competitor> --app-id <another> --country us --format md
```

Top phrases show how users describe the job, and these often make good keywords. Complaint words from 1–2 star
reviews are *differentiation material* for the subtitle and screenshots. They are not keywords.

## 4. Score

```bash
python3 scripts/keyword_rank.py score --keywords shortlist.json --app-text listing.json --country us,gb -o scores.json
```

Read the columns as proxies:
- **popularity**: how early and how high autocomplete offers the term. 0 means it was never offered, which
  is not the same as never searched.
- **difficulty**: the strength of the top 10 results. Above about 70, a new app rarely reaches page one.
- **relevance**: calculated from the listing text. Override it by hand with `--relevance` when the
  calculation is wrong. Relevance is a judgement, and a keyword that doesn't describe the app is a 2.3.7 problem
  whatever its score.
- **opportunity**: popularity × (100 − difficulty) × relevance.

For a new app, sort by opportunity and look for terms with popularity of 20 or more and difficulty under 60.
The name and subtitle carry the 2–3 terms that matter most. The keyword field carries the long tail.

## 5. Multi-market check

Score the same list in each launch storefront (`--country us,gb,de`). A term can be easy in one market and
saturated in another. If the app is localised, run seeds in each language. Never translate keywords
mechanically. Users in each market type their own words.

## 6. Build variants

- **3 name variants**: brand alone, brand plus a short descriptor, and descriptor-led if the brand is unknown.
  Every variant must be a name a person would say, not a list of words.
- **3 subtitle variants**: each is a promise ("Find a belayer for tonight"), and none repeats a name word.
- **1–2 keyword fields** from `keyword_pack.py` for each name/subtitle pair, since the pack depends on what the
  name and subtitle already hold.

```bash
python3 scripts/keyword_pack.py --scores scores.json --country us --name "Belayer" --subtitle "Find partners at your crag"
python3 scripts/char_lint.py --file variants.json --competitors competitors.json
```

Nothing is shown to the user until `char_lint.py` passes.

## 7. Category

See `category-choice.md`.

## 8. Measure

After launch, re-run `score --app-id <your id>` every 2–4 weeks for the shortlist and record your rank. Apple
Search Ads (search popularity 1–100, inside the Apple Ads dashboard) is the only first-party volume signal. If
the developer has access, calibrate the proxies against it.
