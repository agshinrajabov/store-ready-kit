# Guideline 4.3 — Spam: what it asks, how reviewers apply it

Guidelines revision: **8 June 2026** · last checked: **2026-10-04** · numbers: 4.3(a), 4.3(b), 4.2, 4.2.6, 2.3.7, 5.6.4

Summaries are in our own words. Read the current text at
https://developer.apple.com/app-store/review/guidelines/#spam before relying on any detail here.

## The two parts

**4.3(a) — one app, many bundle IDs.** Don't ship the same app several times (one per city, team, school…).
Ship one app and offer the variations inside it. In practice reviewers also use the (a) wording when your binary,
metadata or concept look like apps *other developers* already submitted, including apps from terminated accounts.

**4.3(b) — indistinguishable or low-effort.** Since the June 2026 rewrite it has two prongs:

1. **Indistinguishable.** Variants of crowded categories or of popular apps hurt discovery. Some categories are
   named as established (dating, flashlight, sound effects, wallpaper, simple timers, fortune telling): new apps
   there need a *meaningfully different or improved experience*, and existing ones may be removed if they are not
   kept up.
2. **Low-effort.** Some kinds of apps (drinking games, Kama Sutra, fart and burp apps are the named examples) are
   called mediocre or low-effort, and repeated submissions of this kind can end in removal from the Developer
   Program.

The second prong is the one that catches vibe-coded and template apps that are *not* in a named category: the
reviewer judges the whole product — design, content, concept — as not adding value.

## Related rules that travel with 4.3

| Rule | In short |
|---|---|
| 4.2 Minimum Functionality | More than a repackaged website; lasting entertainment value or real utility. |
| 4.2.6 | Apps from a commercial template or app-generation service are rejected unless the content provider submits them. |
| 2.3.7 | Unique name; accurate keywords; no trademarks, competitor names, prices or filler to game search. 30-character name. |
| 5.6.4 App Quality | Sustained low quality (complaints, refunds) can count against the developer account itself. |
| After You Submit → Timing | Repeated rejections for the same guideline, or manipulating review, make reviews slower. |

## How it plays out (patterns from documented cases, 2023–2026)

What reviewers react to — evidenced in public cases:

- **The first minutes and the store page.** New-app reviews are short (court filings put the 2016 average around
  13 minutes). Icon, screenshots, first screen, first level, first purchase prompt carry the judgement.
- **Template packaging.** Engine or kit defaults left visible; the category's standard HUD, art and store frames.
- **Shared binaries and copied projects.** Engine builds flagged as similar to unrelated games; projects cloned
  from another app with the same asset IDs.
- **Several similar apps on one account.** The documented route to account termination.
- **The reviewer's category label.** A B2B dashboard called "astrology", a social app called "dating": once the
  label sticks, renames and new keywords rarely move it. Arguing originality against the label fails; changing
  what the reviewer sees first sometimes works.

What resolved cases — evidenced:

- A short, factual Resolution Center reply explaining what the app is (and, for engine games, why binaries look
  alike).
- A visibly different first impression — in one case a new icon alone.
- Re-review by a different reviewer, sometimes after an appeal or a forum post.

What did not work — evidenced:

- Rapid resubmissions with cosmetic changes. Every documented account flag followed this.
- New bundle ID, new account, or a rename to escape the history (Apple tracks lineage; evasion is a
  termination matter).
- Appeals that argued "my app is original" when the problem was the category label or the quality judgement.

Not evidenced (do not claim it): any published appeal success rate for rejections; any per-guideline share of
rejections (figures like "4.3 is 28% of rejections" circulate without a source); that hyper-casual art alone
triggers 4.3.

## What "significant changes" means

Apple does not define it. Read it as: **the store page and the first five minutes must look and feel like a
different, more finished product**, and the next submission should be one you would defend as such. Diff size
is not the measure; the reviewer's first impression is.

## Reading a 4.3 letter

| The letter says | Prong | Answer with |
|---|---|---|
| "duplicates the content and functionality of similar apps in a saturated category" | (b) indistinguishable | The one experience no existing app offers, visible in screenshot 1 and minute 1 |
| "similar binary, metadata, and/or concept … minor differences" | (a)-style similarity | Lineage facts (own code, not a template; engine explains shared binary) + visible difference |
| "design, content, and overall concept do not provide the high-quality experience" | (b) low-effort | Craft: authored first session, own art direction, monetisation that does not lead |
| mentions a terminated account | (a) lineage | A factual statement of who built it and how, if that is the truth |

The `submission-pilot` skill owns the response and resubmission strategy; this file is what `store-audit` uses
to predict the conversation before it happens.
