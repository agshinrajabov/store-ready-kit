# App Store metadata — limits, indexing, rules

Guidelines revision: **8 June 2026** · last checked: **2026-10-04** · numbers: 2.3.1, 2.3.7, 2.3.8, 2.3.10, 5.2.1

## Fields and limits

| Field | Limit | Searchable | Notes |
|---|---|---|---|
| App name | 30 | Yes — strongest weight | Brand first. A short descriptor is fine; a keyword stack is not (2.3.7). |
| Subtitle | 30 | Yes | A promise in plain words. Don't repeat name words. |
| Keyword field | 100 | Yes (hidden) | Comma-separated, no spaces. Not shown to users. |
| Promotional text | 170 | No | Can change without a new build. |
| Description | 4,000 | No on the App Store search (reported widely; Apple does not document the ranking) | Written for people, not the algorithm. |
| What's New | 4,000 | No | Describe this version's changes (2.3.12). |
| In-app purchase display name | 30 | Can appear in search | Must describe the product. |
| Developer name | — | Yes | Set by the account. |

Apple documents the 30-character name and 100-character keyword field. The other behaviour in this table
(what is indexed, how heavily) is practitioner knowledge. It is consistent across ASO tools, but Apple
does not publish its ranking. Present it as such.

## How the three searchable fields combine

Words from the name, subtitle and keyword field are matched together. A user search for "climbing partner"
can match "Climbing" in the subtitle and "partner" in the keywords. So:

- Never repeat a word across the three fields. The repeat earns nothing and costs the space.
- Single words in the keyword field. Phrases combine on their own.
- Singular or plural, not both. Apple matches many plurals; pick the form users type.
- No spaces after commas. Each one wastes a character.
- Skip "app", "the", "and", the category name (an app in Games already matches "game").

## Localisations extend coverage

Each storefront indexes its primary language and, by widely reported practitioner experience, some other
localisations as well. One example often reported: the US store also indexes Spanish (Mexico) metadata.
Treat this as unverified and check it with your own rank results. Never fill a localisation with keywords in
a language the app does not support. The localisation must be real.

## What the rules forbid (2.3.7 and neighbours)

- Trademarked terms, other apps' names, and celebrity or public-figure names you have no rights to (2.3.7, 5.2.1).
- Prices, "free", "sale", rankings ("#1", "best", "top") in the name, subtitle or keywords (2.3.7).
- Irrelevant terms added only for search (2.3.7). The keywords must describe the app.
- Names of other platforms (2.3.10).
- Metadata that promises features the build does not have (2.3.1).
- Names that copy or imitate another app's name or icon (2.3.7, 4.1 copycats).

`char_lint.py` blocks the first three mechanically. The others need judgement.
