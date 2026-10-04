# Listing JSON — the input the audit scripts share

One file describes the app as the reviewer will meet it. Fields the scripts do not need can be left out; a
missing section means that signal is "not assessed", never "fine".

```json
{
  "name": "Belayer",                                  // ≤ 30 characters
  "subtitle": "Find partners at your crag",           // ≤ 30 characters
  "keywords": "climbing,bouldering,crag,belay",       // ≤ 100 characters, comma-separated
  "description": "…",
  "whats_new": "…",
  "category": "Sports",
  "one_line": "helps climbers find a belay partner for tonight's session.",   // review-notes draft
  "privacy_policy_url": "https://…",
  "requires_login": true,
  "demo_account": {"username": "review@…", "password": "…"},             // never commit real credentials
  "review_steps": ["Sign in with the demo account", "Tap Tonight", "Tap any climber to see the match card"],
  "non_obvious": ["Matching needs two accounts; the demo account already has a pending match."],
  "iap_summary": "One auto-renewing subscription (Belayer Plus), monthly and yearly.",
  "changes_since_rejection": [],

  "screenshots": [
    {"caption": "Find a belayer for tonight", "concept": "match card over a gym map", "shows_real_ui": true}
  ],

  "differentiators": ["Belay certification verified through partner gyms"],
  "niche_saturated": false,              // set true if a reviewer could file it under a category 4.3(b) names

  "trait_catalog": "utility-app",        // hypercasual-game | utility-app | ai-wrapper
  "traits": {"UT01": false, "UT02": false, "UT08": "partial"},

  "monetisation": {
    "iap_count": 2, "consumable_count": 0, "rewarded_placements": 0,
    "interstitial": null,                       // e.g. "every third level from level 9"
    "purchase_prompts_first_10_min": 0,
    "paywall_before_value": false,
    "sink_without_content": false
  },
  "content": {
    "generated": false, "authored_onboarding": true,
    "repeats_in_first_session": false, "silent_failures": false, "lasting_value": true
  },
  "account": {
    "similar_apps_on_account": 0, "template_or_generator": false,
    "reused_project_assets": false, "prior_4_3_rejections": 0
  },
  "exclude_ids": [1234567890]            // your own live app, left out of the competitor set
}
```

(Comments are for this page only; the real file is plain JSON.)

## Filling it honestly

- `traits`, `monetisation` and `content` describe the **build under review on a fresh install**, not the plan.
  Count purchase and ad prompts by playing the first ten minutes with a timer.
- `differentiators` are things a reviewer can *see*. "Better UX" is not one; "verified belay certification on every
  profile" is.
- `template_or_generator` is true for an app-builder project whose scaffold is still recognisable — be honest;
  the audit is cheaper than the rejection.
