#!/usr/bin/env python3
"""Read an App Review rejection or message and decide the response path.

Classifies the letter (which guidelines, which kind of 4.3, information request or rejection, whether it
says not to resubmit, whether it carries the extended-review warning), combines that with the account's
history, and returns:

  path       ANSWER_ONLY      reply in Resolution Center; no new build needed
             FIX_AND_RESUBMIT fix, new build, short reply listing the fixes
             CLARIFY          the reviewer may have misread; reply with evidence before changing anything
             REWORK           do not resubmit this build; change the product, test, then resubmit once
             STOP             do not submit anything on this concept until you have talked to Apple
  risk       LOW / ELEVATED / HIGH / CRITICAL   for the developer account, not the app
  steps      ordered actions
  avoid      what not to do now

Examples:
  rejection_triage.py --letter rejection.txt
  rejection_triage.py --letter rejection.txt --prior-4-3 1 --similar-apps 0 --format md
  rejection_triage.py --letter rejection.txt --believe-misread

Deterministic and pattern-based. It reads Apple's standard phrasings; an unusual letter gets a low
confidence and a note to read it against references/resubmission-strategy.md by hand.
"""

import argparse
import json
import re
import sys

GUIDELINE = re.compile(r"Guideline\s+(\d+(?:\.\d+){1,2})(?:\s*\(([a-z]+)\))?(?:\s*[-–—]\s*([A-Za-z][\w ,&'/-]{2,60}))?", re.I)

FOUR_THREE = [
    ("b-low-effort", [r"high[- ]quality experience", r"well[- ]crafted", r"low[- ]quality", r"low[- ]effort",
                      r"mediocre", r"does not add value", r"do not add value"]),
    ("b-saturated", [r"saturated category", r"duplicates the content and functionality",
                     r"already widely available", r"well established on the App Store", r"meaningfully different"]),
    ("a-terminated", [r"terminated", r"removed from the App Store for"]),
    ("a-similarity", [r"similar binary", r"similar(?:ar)? (?:binary, )?metadata", r"repackaged", r"only minor differences",
                      r"shares a similar"]),
    ("a-bundle-ids", [r"multiple bundle ids", r"multiple versions of the same app", r"separate apps? for each"]),
]
INFO_NEEDED = [r"information needed", r"we need additional information", r"please (provide|reply|clarify|confirm)",
               r"we have (some|a few) questions", r"help us (better )?understand"]
DO_NOT_RESUBMIT = [r"do not resubmit", r"until significant changes", r"should not resubmit"]
EXTENDED = [r"extended review", r"repeated submissions", r"removal from the apple developer program",
            r"significant safety, security, or quality concerns"]
ACCOUNT = [r"developer code of conduct", r"account (is|has been) (flagged|under review|under investigation)",
           r"pending termination", r"fraudulent", r"dishonest"]
CANT_ACCESS = [r"unable to (sign in|log in|access|use|locate|find)", r"could not (sign in|log in|access|find)",
               r"demo account", r"was unresponsive", r"crashed", r"did not load", r"bug"]

FIXABLE_PREFIXES = ("2.1", "2.3", "2.5", "3.1", "3.2", "4.0", "4.8", "5.1", "5.2", "1.2", "1.4", "1.5", "2.2", "4.5", "4.2")


def any_re(patterns, text):
    return [p for p in patterns if re.search(p, text, re.I)]


def classify(text):
    guidelines = []
    for m in GUIDELINE.finditer(text):
        num, sub, title = m.group(1), m.group(2), (m.group(3) or "").strip()
        tag = f"{num}({sub})" if sub else num
        if tag not in [g["guideline"] for g in guidelines]:
            guidelines.append({"guideline": tag, "title": title})
    kinds43 = [k for k, pats in FOUR_THREE if any_re(pats, text)]
    has43 = any(g["guideline"].startswith("4.3") for g in guidelines) or bool(kinds43 and re.search(r"\bspam\b", text, re.I))
    return {
        "guidelines": guidelines,
        "is_4_3": has43,
        "kind_4_3": (kinds43[0] if kinds43 else ("unspecified" if has43 else None)),
        "kinds_4_3_all": kinds43,
        "information_needed": bool(any_re(INFO_NEEDED, text)) and not any_re([r"rejected", r"did not comply",
                                                                              r"does not comply"], text),
        "do_not_resubmit": bool(any_re(DO_NOT_RESUBMIT, text)),
        "extended_review_warning": bool(any_re(EXTENDED, text)),
        "account_level": bool(any_re(ACCOUNT, text)),
        "access_or_bug": bool(any_re(CANT_ACCESS, text)),
        "mentions_testflight": bool(re.search(r"testflight", text, re.I)),
    }


def risk_level(c, prior43, similar_apps, prior_removals):
    n43 = prior43 + (1 if c["is_4_3"] else 0)        # this letter counts
    if c["account_level"] or prior_removals or (n43 >= 3) or (similar_apps >= 2 and c["is_4_3"]):
        return "CRITICAL", n43
    if n43 >= 2 or (c["is_4_3"] and c["extended_review_warning"] and similar_apps >= 1):
        return "HIGH", n43
    if c["is_4_3"] or c["extended_review_warning"] or c["do_not_resubmit"]:
        return "ELEVATED", n43
    return "LOW", n43


def decide(c, prior43=0, similar_apps=0, prior_removals=0, believe_misread=False):
    risk, n43 = risk_level(c, prior43, similar_apps, prior_removals)
    steps, avoid = [], [
        "A new bundle ID, a new developer account, or a rename to escape this history",
        "Hostile or pleading tone; claiming the app 'fully complies'",
        "Hiding or disabling features only for the review build",
    ]
    confidence = "high" if (c["guidelines"] or c["information_needed"]) else "low"

    if risk == "CRITICAL":
        path = "STOP"
        steps = ["Do not submit any build or new app from this account until the situation is clear.",
                 "Request a one-on-one App Review consultation (Meet with Apple) and ask what specifically must change.",
                 "Write down the account's history: every app, every rejection, dates, guidelines.",
                 "If a termination or Code of Conduct notice arrived: answer it once, in writing, factually, with the improvements planned."]
        avoid += ["Any upload while the account question is open", "Uploading a second similar title"]
    elif c["information_needed"] and not c["is_4_3"]:
        path = "ANSWER_ONLY"
        steps = ["Answer every question in Resolution Center, numbered to match theirs.",
                 "Attach evidence (screen recording, documents) where a question asks for it.",
                 "Do not upload a new build unless the answer requires a change."]
    elif c["is_4_3"] and (c["do_not_resubmit"] or c["kind_4_3"] == "b-low-effort" or n43 >= 2):
        path = "REWORK"
        steps = ["Do not resubmit this build. Do not file an appeal that argues the app is original.",
                 "Run store-audit: find which surfaces read as template or low-effort (store page, first five minutes, monetisation).",
                 "Rework so the store page and first five minutes look like a different, more finished product.",
                 "External TestFlight round (the letter may name it): record tester count, length, what changed because of it.",
                 "Optionally reply once in Resolution Center: short, factual, what you are changing; ask for the specific concern.",
                 "Resubmit once, with review notes that list the changes and the TestFlight round."]
        avoid += ["Resubmitting with cosmetic changes", "More than one resubmission before the rework is done",
                  "Uploading any other similar app from the account meanwhile"]
    elif c["is_4_3"] and c["kind_4_3"] in ("a-similarity", "a-terminated", "unspecified"):
        path = "CLARIFY"
        steps = ["Reply in Resolution Center with facts: who built it, that it is not from a template or another account, "
                 "and (for engine games) why binaries look alike.",
                 "Link a 60–90 s video of the core loop.",
                 "List what in the app is your own work that a reviewer can see in the first minute.",
                 "If the reply does not resolve it: one App Review Board appeal with the same facts.",
                 "If it is true that the app shares lineage (copied project, template): fix that first, then resubmit."]
        avoid += ["Changing name, icon and keywords in a hurry and resubmitting the same build"]
    elif c["is_4_3"] and c["kind_4_3"] == "b-saturated":
        path = "REWORK" if not believe_misread else "CLARIFY"
        steps = (["Name the one experience no existing app offers. If there is none, do not resubmit: rethink the app.",
                  "Make it visible in screenshot 1 and in the first minute.",
                  "State it in the review notes in plain words; resubmit once."] if path == "REWORK" else
                 ["Reply in Resolution Center: what the app is (category label may be wrong), what is different, with a video.",
                  "If the label sticks, change what the reviewer sees first rather than arguing originality.",
                  "Appeal only with facts that contradict the label."])
        avoid += ["Arguing 'there are few apps like mine' against a category label"]
    elif c["is_4_3"] and c["kind_4_3"] == "a-bundle-ids":
        path = "REWORK"
        steps = ["Merge the variants into one app with the variations inside it (in-app choice or purchase).",
                 "Remove or stop updating the duplicates; submit the single app."]
    elif believe_misread:
        path = "CLARIFY"
        steps = ["Reply in Resolution Center: where the feature is, exact steps, a screen recording.",
                 "Ask the reviewer to re-review the same build; upload nothing new unless they ask.",
                 "If still rejected and you are sure: one App Review Board appeal with the evidence."]
    else:
        path = "FIX_AND_RESUBMIT"
        steps = ["Fix each cited issue; check the same guideline across the whole app, not only the screen named.",
                 "Test on the device and OS named in the letter (iPad if it says iPad).",
                 "New build; reply in Resolution Center with a short numbered list of fixes, matching their points.",
                 "Update review notes (demo account, steps) if access was part of the problem."]
        if c["access_or_bug"]:
            steps.insert(1, "Reproduce on a fresh install with the demo account from a different network; back end on.")

    if not any(g["guideline"].startswith(FIXABLE_PREFIXES + ("4.3",)) for g in c["guidelines"]) and c["guidelines"]:
        confidence = "medium"
    return {"path": path, "risk": risk, "four_three_count_including_this": n43, "confidence": confidence,
            "steps": steps, "avoid": avoid}


def triage(text, prior43=0, similar_apps=0, prior_removals=0, believe_misread=False):
    c = classify(text)
    d = decide(c, prior43, similar_apps, prior_removals, believe_misread)
    return {"tool": "rejection_triage", **c, **d,
            "note": "Guidance based on public App Review Guidelines; Apple's decisions are their own."}


def evaluate(letter, **kw):
    with open(letter, encoding="utf-8") as fh:
        return triage(fh.read(), **kw)


def to_markdown(r):
    g = ", ".join(x["guideline"] + (f" ({x['title']})" if x["title"] else "") for x in r["guidelines"]) or "none found"
    lines = [f"# Rejection triage — {r['path']} · account risk {r['risk']}", "",
             f"- Guidelines cited: {g}",
             f"- 4.3: {r['kind_4_3'] or 'no'}" + (f" (4.3 rejections on this concept incl. this one: {r['four_three_count_including_this']})" if r["is_4_3"] else ""),
             f"- Information request: {'yes' if r['information_needed'] else 'no'} · 'do not resubmit': {'yes' if r['do_not_resubmit'] else 'no'} · "
             f"extended-review warning: {'yes' if r['extended_review_warning'] else 'no'} · TestFlight named: {'yes' if r['mentions_testflight'] else 'no'}",
             f"- Confidence: {r['confidence']}", "", "## Do, in order", ""]
    lines += [f"{i}. {s}" for i, s in enumerate(r["steps"], 1)]
    lines += ["", "## Do not", ""] + [f"- {a}" for a in r["avoid"]]
    lines += ["", f"_{r['note']}_"]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--letter", required=True, help="the rejection / message text, pasted into a file")
    p.add_argument("--prior-4-3", type=int, default=0, help="earlier 4.3 rejections on this concept (not counting this one)")
    p.add_argument("--similar-apps", type=int, default=0, help="other similar apps on the same account")
    p.add_argument("--prior-removals", type=int, default=0, help="apps removed from the store on this account")
    p.add_argument("--believe-misread", action="store_true", help="you can show the reviewer missed or misread something")
    p.add_argument("--format", choices=["json", "md"], default="md")
    a = p.parse_args()
    with open(a.letter, encoding="utf-8") as fh:
        r = triage(fh.read(), a.prior_4_3, a.similar_apps, a.prior_removals, a.believe_misread)
    print(to_markdown(r) if a.format == "md" else json.dumps(r, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
