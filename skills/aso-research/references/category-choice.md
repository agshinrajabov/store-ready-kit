# Choosing the primary and secondary category

Guidelines revision: **8 June 2026** · last checked: **2026-10-04** · numbers: 2.3.5

## The rule

Pick the category that best fits what the app *does* (2.3.5). Apple can change it. A category chosen for
ranking reasons but not by fit is a metadata problem, and a reviewer may also read it as a 4.3(b) signal.

## How to choose between two that both fit

1. **Fit first.** If a user browsing each category would expect to find this app there, both are candidates.
2. **Chart depth.** `python3 scripts/keyword_rank.py charts --genre <id> --genre <id> --country us,gb` reports
   ratings at #10 and the median ratings of positions 41–60 and 81–100 in each top-free chart. Single positions
   are noisy, so read the medians. Fewer ratings means an easier chart to enter.
3. **Search, not charts, brings most installs to small apps.** Do not trade fit for chart position.
4. **Secondary category**: a second fit. It does not change ranking much, but it costs nothing if it is
   honest.
5. **Games**: choose the subgenre the core loop belongs to (Puzzle, Word, Board…), not the theme.

## Genre IDs (common)

| Category | ID | Category | ID |
|---|---|---|---|
| Games | 6014 | Productivity | 6007 |
| Puzzle (game) | 7012 | Utilities | 6002 |
| Casual (game) | 7003 | Health & Fitness | 6013 |
| Lifestyle | 6012 | Education | 6017 |
| Photo & Video | 6008 | Finance | 6015 |
| Social Networking | 6005 | Travel | 6003 |
| Sports | 6004 | Food & Drink | 6023 |

These were checked against the live top charts on 2026-10-04.

## Report it as

The recommended primary and secondary category, one sentence on fit, and the chart-depth numbers for each
candidate with the date fetched.
