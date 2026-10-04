# App Review notes — writer's guide and templates

Last checked: **2026-10-04** · relates to 2.1 (demo account, back end on, hardware), 2.5.4 (background modes),
4.3(b) (stating the difference)

The reviewer reads the notes before opening the app. Aim for under ~1,200 characters (the field holds 4,000).
Put credentials in the dedicated sign-in fields of App Review Information, and keep the notes for everything
else.

## Skeleton

```
<App> <one sentence: who it is for and what it lets them do>.

Access: <demo account is in the sign-in fields; it has <data> pre-loaded> | <no account needed>.

To see the core feature:
1. <tap>
2. <tap>
3. <what they should see>

<Only if needed:>
Not obvious: <hardware, region, two-account features, why a permission is asked>.
Different from other <category> apps: <two plain sentences a reviewer can verify in the first minute>.
Changes since the last review (<guideline>, <date>): <numbered list of what is in this build>.
In-app purchases: <list, plainly>.
```

## Situations

| Situation | Add |
|---|---|
| Needs hardware (a device, a sensor, a location) | A recording of the feature working with the hardware; a demo mode if possible |
| Two-person features (chat, matching, sharing) | Pre-seeded matches or a second demo account |
| Background location, audio or Bluetooth | Why it runs in the background and how to see it (2.5.4) |
| Regional content | Which storefronts, and a way to see it from elsewhere |
| Kids or education | Who it is for, the parental gate location |
| User-generated content | Where to report and block, and how moderation works (1.2) |
| After a 4.3 | The changes, the TestFlight round (testers, days, what changed) |

## Rules

- Only describe what is in this build.
- No marketing, no superlatives, no deadlines, no pleading, no competitor names.
- Run `message_lint.py --kind notes [--requires-login]` and fix every BLOCK.
