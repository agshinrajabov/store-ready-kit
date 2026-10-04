# Resolution Center replies — templates by path

Last checked: **2026-10-04**

Principles: short, factual, numbered, polite, no pressure. Name the guideline. Each point in their letter gets
a matching numbered point in yours. Run `message_lint.py --kind reply` on every draft.

## ANSWER_ONLY: information request

```
Hello App Review,

Thank you. Answers to your questions:

1. <their question 1, shortened> — <direct answer, one or two sentences>.
2. <question 2> — <answer>.
3. <question 3> — <answer>. Screen recording: <link>.

Happy to provide anything else.
```

## FIX_AND_RESUBMIT: a fixed issue

```
Hello App Review,

Thank you for the review under <guideline>. In build <number> we:

1. <what was wrong, in their words> — <what changed>, tested on <device, OS>.
2. <…>

<If access was the problem:> The demo account in App Review Information has been checked from an outside
network today.
```

## CLARIFY: misread, or 4.3 similarity

Misread:
```
Hello App Review,

Regarding <guideline>: <the feature> is in this build. To reach it:
1. <step> 2. <step> 3. <step>
A 40-second recording: <link>. Could you take another look at the same build?
```

4.3(a)-style similarity:
```
Hello App Review,

Regarding 4.3: <app> was built by <who> <since when>. It is not based on a template, another developer's
project, or any other app on our account. <For engine games:> It is built with <engine>, whose runtime is shared
by many games, which can make binaries look alike.

What a player sees in the first minute that is ours: <two or three concrete things>.
Gameplay video: <link>.
```

## REWORK: a quality / low-effort 4.3(b)

Optional, sent once, and only after you have decided what to change. It is not an argument.

```
Hello App Review,

Thank you for the review under 4.3(b). We read it as a judgement on the experience as a whole.
We are not resubmitting this build. We are changing:
1. <change to the first session>
2. <change to the store page / art direction>
3. <change to monetisation>
We will run an external TestFlight round before submitting again. If there is a specific concern you can point
us to, we would be grateful.
```

## STOP

Do not reply in Resolution Center with arguments. Answer any account notice through the channel it names,
once, with: the facts of the account's apps, what you will change, and a contact.
