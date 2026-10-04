#!/usr/bin/env python3
"""Lint a screenshot plan before anything is designed: the first three frames, the narrative, the captions.

Input: a plan JSON (see --example). Each frame says what it shows, whether that is the real app UI, which
moment of the app it is, and its caption.

Blocking (exit 1):
  - frame 1 is not the real app in use (title art, splash, login, onboarding)      2.3.3 + conversion
  - frames 1-3 never show the core outcome or the differentiator
  - two of the first three frames show the same concept
  - prices, rankings or 'free' in a caption                                         2.3.7
  - other platforms named                                                           2.3.10
Warnings:
  - captions longer than 7 words (unreadable at search-result size)
  - feature-list captions ('Powerful tools', 'Easy to use') instead of outcomes
  - stock category phrases ('Relax and unwind', '1000+ levels')
  - fewer than 3 or more than 10 frames

Examples:
  plan_lint.py --example > plan.json
  plan_lint.py --plan plan.json
"""

import argparse
import json
import re
import sys

EXAMPLE = {
    "app": "Belayer",
    "core_outcome": "a belay partner for tonight's session",
    "differentiator": "verified belay certification on every profile",
    "frames": [
        {"caption": "Find a belayer for tonight", "shows": "Tonight list with three climbers free at your gym",
         "real_ui": True, "moment": "outcome", "concept": "tonight-list"},
        {"caption": "Every belayer is certified", "shows": "profile with the verified certification badge expanded",
         "real_ui": True, "moment": "differentiator", "concept": "certification"},
        {"caption": "Plan the session together", "shows": "shared session plan with routes and time",
         "real_ui": True, "moment": "outcome", "concept": "session-plan"},
        {"caption": "Check in when you're down", "shows": "safety check-in prompt after the session",
         "real_ui": True, "moment": "feature", "concept": "check-in"},
    ],
}

STOCK = ["relax", "unwind", "addictive", "brain training", "train your brain", "1000+ levels", "hundreds of levels",
         "thousands of levels", "challenge your mind", "satisfying", "stress relief", "all in one", "all-in-one",
         "easy to use", "simple and easy", "boost your", "next level", "like never before"]
FEATURE_WORDS = ["powerful", "features", "feature-rich", "tools", "supports", "easy to use", "intuitive",
                 "user-friendly", "beautiful design", "simple interface", "customizable", "advanced"]
PRICE_RANK = [r"\bfree\b", r"\$\s?\d", r"\d+\s?% off", r"#\s?1\b", r"\bbest\b", r"\btop[- ]rated\b", r"\bnumber one\b"]
PLATFORMS = [r"\bandroid\b", r"google play", r"play store"]
NOT_IN_USE = {"title", "splash", "login", "onboarding", "logo"}


def words(s):
    return re.findall(r"[a-z0-9']+", (s or "").lower())


def lint(plan):
    frames = plan.get("frames", [])
    blocks, warns = [], []
    n = len(frames)
    if n < 3:
        warns.append(f"{n} frames; plan at least 3 — most people only see the first three, but they swipe for more")
    if n > 10:
        blocks.append(f"{n} frames; App Store Connect accepts at most 10")
    if not frames:
        return {"ok": False, "violations": ["no frames"], "warnings": warns}

    f1 = frames[0]
    if not f1.get("real_ui", False) or (f1.get("moment") or "").lower() in NOT_IN_USE:
        blocks.append("frame 1 does not show the app in use (title art, splash, login or onboarding) — 2.3.3, and it "
                      "wastes the one frame everyone sees")
    first3 = frames[:3]
    diff_words = set(words(plan.get("differentiator"))) - {"the", "a", "on", "every", "of", "and", "your"}
    hits_diff = any((f.get("moment") or "").lower() == "differentiator" or
                    len(diff_words & set(words(f.get("shows")) + words(f.get("caption")))) >= 2 for f in first3)
    hits_outcome = any((f.get("moment") or "").lower() == "outcome" for f in first3)
    if not (hits_diff or hits_outcome):
        blocks.append("frames 1-3 show neither the core outcome nor the differentiator")
    elif not hits_diff:
        warns.append("the differentiator does not appear in frames 1-3; after a 4.3 conversation it should")
    concepts = [(f.get("concept") or f.get("shows") or "").strip().lower() for f in first3]
    if len(set(concepts)) < len(concepts):
        blocks.append("two of the first three frames show the same concept")

    for i, f in enumerate(frames, 1):
        cap = f.get("caption") or ""
        low = cap.lower()
        for pat in PRICE_RANK:
            m = re.search(pat, low)
            if m:
                blocks.append(f"frame {i}: '{m.group(0)}' in the caption (2.3.7: no prices or rankings in screenshots)")
        for pat in PLATFORMS:
            if re.search(pat, low + " " + (f.get("shows") or "").lower()):
                blocks.append(f"frame {i}: another platform named (2.3.10)")
        if len(words(cap)) > 7:
            warns.append(f"frame {i}: caption has {len(words(cap))} words; keep to 7 or fewer")
        stock = [s for s in STOCK if s in low]
        if stock:
            warns.append(f"frame {i}: stock phrase '{stock[0]}' — every competitor says it")
        feat = [w for w in FEATURE_WORDS if w in low]
        if feat:
            warns.append(f"frame {i}: feature-list wording ('{feat[0]}') — caption the outcome the user gets instead")
        if not f.get("real_ui", True) and i <= 3:
            warns.append(f"frame {i}: not real UI; keep composed art out of the first three frames")
    return {"ok": not blocks, "violations": blocks, "warnings": warns}


def evaluate(plan):
    with open(plan, encoding="utf-8") as fh:
        r = lint(json.load(fh))
    return {"tool": "plan_lint", **r}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--plan")
    p.add_argument("--example", action="store_true")
    p.add_argument("--format", choices=["json", "md"], default="md")
    a = p.parse_args()
    if a.example:
        print(json.dumps(EXAMPLE, indent=2))
        return
    if not a.plan:
        p.error("give --plan or --example")
    r = evaluate(a.plan)
    if a.format == "json":
        print(json.dumps(r, indent=2))
    else:
        for v in r["violations"]:
            print(f"BLOCK {v}")
        for w in r["warnings"]:
            print(f"WARN  {w}")
        print("Plan OK." if r["ok"] else f"{len(r['violations'])} blocking issue(s).")
    sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
