# Screenshot narrative planner

Last checked: **2026-10-04**

Plan the story in words before any pixels. A plan is a JSON file (`scripts/plan_lint.py --example`) that
`plan_lint.py` checks.

## Step 1: the three sentences

Write these before anything else. If you cannot, the screenshots will not fix it.

1. **Core outcome**: what the user has after using the app ("a belay partner for tonight's session").
2. **Differentiator**: what only this app does, visible on screen ("verified belay certification on every
   profile"). Take it from `store-audit`'s differentiation moves if it ran.
3. **The doubt**: what makes someone hesitate ("will a stranger be safe to climb with?"). One frame answers it.

## Step 2: the moment map

List the 6–10 moments of a first good session in order: the first screen with value, the core action, the
result, the second-best feature, proof (data, a review quote the app is allowed to use, an award it really won),
and the answer to the doubt. Mark each one as `outcome`, `differentiator`, `feature`, `proof` or `setup`.

## Step 3: pick and order

| Frame | Job | Typical moment |
|---|---|---|
| 1 | Make them stop | The outcome or the differentiator, real UI, readable small |
| 2 | Show how | The core action in progress |
| 3 | Show why this app | The differentiator if frame 1 was the outcome, otherwise the answer to the doubt |
| 4–6 | Remove doubts | Second features, proof, privacy and safety answers |
| 7–10 | Optional | Depth, widgets, Watch, iPad, accessibility |

Games: frame 1 is the game's most distinctive moment (mid-play, not the menu). Frame 2 is the core verb. Frame
3 is progression or the world. Show the art direction that is the game's own.

## Step 4: compare with the niche

Look at the top 10 competitors' first three frames (store-audit's snapshot keeps `firstScreenshots` URLs).
Write down the shared pattern: layout, palette, caption style. **Your frame 1 should be recognisably not that
pattern.** Converge on what the market needs to see (the outcome, readable UI). Diverge in how it looks.

## Step 5: lint, then design

```bash
python3 scripts/plan_lint.py --plan plan.json
```

Fix every BLOCK. Then hand the plan to the visual pass. If the `no-slop-design` skill is installed, run it for
the composition, palette and type of the frames, and give it the plan and the niche pattern from step 4. This
skill does not do the visual design itself.

After the frames are exported:

```bash
python3 scripts/asset_check.py exports/iphone/*.png exports/ipad/*.png --platform iphone --platform ipad
```
