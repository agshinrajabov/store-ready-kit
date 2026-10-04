# The 4.3(b) playbook: why "but my app is original" doesn't work, and what does

*store-ready-kit · guidelines revision of 8 June 2026 · last checked 2026-10-04*

> Guidance based on public App Review Guidelines; Apple's decisions are their own.

## The letter

In September 2026 an indie puzzle game got two rejections in two days. The first was ordinary: Guideline
2.1(a). On the reviewer's iPad the first tap on the first piece did nothing. The developer fixed it and
resubmitted the next morning.

The second reviewer played the game, and the second rejection was not ordinary. It cited **Guideline 4.3(b)
Spam**. It said the app's design, content and overall concept did not provide the high-quality experience
expected on the App Store. It said not to resubmit until significant changes had been made, and to use
TestFlight. It closed with the paragraph every developer dreads: repeat submissions like this lengthen review
and can end in removal from the Developer Program.

The developer's first reaction is the one most developers have: *but nothing else on the store plays like
this.* That was true. The core mechanic, unfolding hinged fairground rides in the one order the hinges allow,
did not exist in any live app. It also didn't matter.

(The case is real and used with the developer's permission. Names and identifying details are removed.)

## What 4.3(b) says now

Apple rewrote 4.3(b) in June 2026. In our own words, it now has two prongs:

1. **Indistinguishable.** Variants of crowded categories or popular apps. Some categories are named as
   established (dating, flashlight, sound effects, wallpaper, simple timers, fortune telling). New apps there need
   a meaningfully different or improved experience.
2. **Low-effort.** Some kinds of apps are called mediocre or low-effort, apps that don't add value. Repeated
   submissions of this kind can lead to removal from the program.

Most advice online is written for prong 1: be different from the apps in your category. This letter was prong
2. It didn't say "there are too many games like yours". It said "what you made doesn't feel made". That
distinction decides everything that follows. **Arguing originality answers prong 1. It doesn't answer prong
2.**

## What the reviewer actually met

New-app reviews are short; court filings in Epic v. Apple put the average around thirteen minutes. In those
minutes the reviewer saw:

- an engine splash screen, then an empty island with a padlocked level teaser;
- a big PLAY button, a hearts row, a coin pill with a "+" shop shortcut, "Level 1" as the title;
- chunky outlined candy buttons, a rounded white font with an ink outline, blob clouds, lollipop trees, bloom and
  vignette;
- a generated first level, a win card with confetti whose loudest button was "watch an ad";
- by the second level, a $1.99 rescue pack as the biggest button on the fail screen;
- **five purchase or ad prompts inside three minutes**, on a build with seven in-app purchases.

The developer later scored the build against a sixteen-point checklist of the hyper-casual template. It matched
thirteen points fully. The new mechanic was in there, but it was dressed exactly like everything else in the
category, and monetised like it.

That is what "low-effort" means in practice. The reviewer is not judging the idea. They are judging **the
package they meet in the first minutes**.

## What works and what doesn't: twenty public cases

We read twenty documented 4.3 cases from 2023–2026 (developer forums, engine forums, press). The pattern is
consistent:

**What resolved cases:**
- a short, factual Resolution Center reply explaining what the app is (and, for engine games, why binaries look
  alike);
- a visibly different first impression. In one case, a clearly different icon alone;
- re-review by a different reviewer, sometimes after an appeal.

**What did not:**
- rapid resubmissions with cosmetic changes. Every documented account flag followed this pattern;
- a new bundle ID, a new account, or a rename to escape the history;
- appeals that argued "my app is original" when the problem was a category label or a quality judgement.

**What nobody can tell you:** an appeal success rate (Apple publishes none for rejections), or what share of
rejections are 4.3. Figures that circulate online have no source we could find. Be suspicious of anyone who
quotes one, including us.

## The playbook

### Before you submit

1. **Look at your app the way the reviewer will: store page, then the first five minutes, fresh install, on an
   iPad.** Write down every purchase or ad prompt with a timestamp.
2. **Name your niche's template.** Open the top ten apps in your category. List what they all share: art style,
   HUD, win and fail screens, screenshot style, business model. Then count how many of those your app has.
3. **Find the idea that is already yours.** It is usually in the name or the core mechanic, and usually missing
   from the screen. Make it the first thing a reviewer sees: screenshot 1, the first level, the win moment.
4. **Let the first session breathe.** At most one stated purchase and one optional ad in the first ten
   minutes. Keep the other products in App Store Connect, unattached, for a later version.
5. **Hand-author the first five minutes.** One idea per step, no repeats, every tap answered.
6. **Write review notes that state the difference in two plain sentences** a reviewer can verify in the first
   minute.

### After a 4.3

1. **Read the letter for its prong.** "Saturated category / duplicates content" is prong 1. "High-quality
   experience / well-crafted" is prong 2. "Similar binary or metadata" is lineage.
2. **If it says "do not resubmit until significant changes": don't.** Not tomorrow, not with a new icon.
3. **Change what the reviewer meets, not what the app is called.** The store page and the first five minutes
   must look and feel like a different, more finished product.
4. **Run an external TestFlight round.** Record testers, days, and what you changed because of it. The letter
   asked for it, and your notes can cite it.
5. **Reply once in Resolution Center if you want to**: short, factual, what you are changing, and a request
   for the specific concern. It costs nothing.
6. **Appeal only for a misapplied guideline, with evidence.** Not to argue originality against a quality
   judgement. Expect weeks of silence.
7. **Resubmit once.** It should be a build you would defend as a different product.
8. **Know the real risk.** We found no documented case where one appeal, or one first 4.3 on a first app, led to
   termination. The documented terminations followed **repeated near-identical resubmissions** or **several
   similar apps on one account**. Avoid those two things and a 4.3 is a setback, not a sentence.

## What happened next

The developer did not appeal and did not resubmit. Within three days they had committed the work in progress
and started rebuilding the encounter: a hand-written first chapter of twelve levels, a page-turn instead of a
win card, and art moving towards paper and ink to match the unfolding mechanic. The plan cuts seven purchases
to one. At the time of writing the rebuilt version has not been submitted. We will update this page with the
outcome, whatever it is.

## Doing this with store-ready-kit

The kit turns this playbook into four agent skills:

- **`store-audit`** pulls your niche from the App Store and scores your listing on nine clone signals, with the
  low-effort combination as its own rule. It checks completeness, metadata, privacy and runtime code download,
  and drafts your review notes. The case above is its first golden eval: the kit must flag it, and flag it for
  the reasons the fix has to move.
- **`submission-pilot`** triages a rejection letter into a path (answer, fix, clarify, rework or stop) and an
  account-risk level, drafts the reply, and lints every message to App Review.
- **`aso-research`** and **`store-assets`** take care of keywords, the first three screenshots, captions, the icon
  brief and the preview script, without stuffing, stock phrases or competitor names.

```bash
git clone https://github.com/agshinrajabov/store-ready-kit && cd store-ready-kit && ./install.sh
```

Then ask your agent: *"Audit my app before I submit it to the App Store."*

*Guidance based on public App Review Guidelines; Apple's decisions are their own.*
