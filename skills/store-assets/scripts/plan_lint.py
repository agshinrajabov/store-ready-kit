#!/usr/bin/env python3
"""Lint a screenshot plan before anything is designed: the first three frames, the narrative, the captions.

Input: a plan JSON (see --example). Each frame says what it shows, whether that is the real app UI, which
moment of the app it is, and its caption.

Blocking (exit 1):
  - frame 1 is not the real app in use (title art, splash, login, onboarding)      2.3.3 + conversion
  - frames 1-3 never show the core outcome or the differentiator
  - frame 1 shows a menu, level grid, settings or feature list instead of a moment of use
  - two of the first three frames show the same concept
  - prices, rankings, ratings or award claims in a caption                          2.3.7
  - other platforms or stores named                                                 2.3.10
  - another app named (with --competitors)                                          2.3.7
  - more than 10 frames
Warnings:
  - captions longer than 7 words (hyphenated words count once)
  - feature-list captions ('Powerful tools', 'Easy to use') instead of outcomes
  - stock category phrases ('Relax and unwind', '1000+ levels')
  - a caption band on all of the first three frames (the category's default frame)
  - fewer than 3 frames

The checks read the plan's own labels (real_ui, moment, concept). They catch mistakes, not misrepresentation:
describe each frame honestly.

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
PRICE_RANK = [r"\bfree\b", r"[$€£¥]\s?\d", r"\b\d+[.,]\d{2}\b", r"\d+\s?% off", r"#\s?1\b", r"\bbest\b",
              r"\btop[- ]rated\b", r"\btop \d+\b", r"\bnumber one\b", r"\b\d(\.\d)? stars?\b", r"editors'? choice",
              r"\baward[- ]winning\b", r"\bgame of the year\b", r"\bapp of the (day|year)\b"]
PLATFORMS = [r"\bandroid\b", r"google play", r"play store", r"\bsteam\b", r"\bxbox\b", r"\bplaystation\b",
             r"\bnintendo\b", r"\bswitch\b(?= version| edition)", r"\bon pc\b", r"\bwindows\b", r"\bgalaxy store\b"]
NOT_A_MOMENT = [r"\blevel (grid|select|map)\b", r"\bmain menu\b", r"\bhome menu\b", r"\bsettings\b",
                r"\bfeature list\b", r"\blogo\b", r"\bsplash\b", r"\bpaywall\b", r"\bsign[- ]?in\b", r"\blogin\b"]
NOT_IN_USE = {"title", "splash", "login", "onboarding", "logo"}


def words(s):
    # "flat-packed" is one word to a reader.
    return re.findall(r"[a-z0-9']+(?:-[a-z0-9']+)*", (s or "").lower())


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def has(phrase, text):
    return re.search(r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", text) is not None


def lint(plan, competitors=()):
    frames = plan.get("frames", [])
    blocks, warns = [], []
    n = len(frames)
    if n < 3:
        warns.append(f"{n} frames; plan at least 3 — most people only see the first three, but they swipe for more")
    if n > 10:  # App Store Connect limit, so it blocks
        blocks.append(f"{n} frames; App Store Connect accepts at most 10")
    if not frames:
        return {"ok": False, "violations": ["no frames"], "warnings": warns}

    f1 = frames[0]
    if not f1.get("real_ui", False) or (f1.get("moment") or "").lower() in NOT_IN_USE:
        blocks.append("frame 1 does not show the app in use (title art, splash, login or onboarding) — 2.3.3, and it "
                      "wastes the one frame everyone sees")
    f1_text = ((f1.get("shows") or "") + " " + (f1.get("concept") or "")).lower()
    if any(re.search(pt, f1_text) for pt in NOT_A_MOMENT):
        blocks.append("frame 1 shows a menu, level grid, settings or similar structure, not a moment of use")
    first3 = frames[:3]
    if len(first3) == 3 and all(f.get("caption_band") for f in first3):
        warns.append("all of the first three frames use a caption band — the category's default frame; drop it at least on frame 1")
    diff_words = set(words(plan.get("differentiator"))) - {"the", "a", "on", "every", "of", "and", "your"}
    hits_diff = any((f.get("moment") or "").lower() == "differentiator" or
                    len(diff_words & set(words(f.get("shows")) + words(f.get("caption")))) >= 2 for f in first3)
    hits_outcome = any((f.get("moment") or "").lower() == "outcome" for f in first3)
    if not (hits_diff or hits_outcome):
        blocks.append("frames 1-3 show neither the core outcome nor the differentiator")
    elif not hits_diff:
        warns.append("the differentiator does not appear in frames 1-3; after a 4.3 conversation it should")
    concepts = [norm(f.get("concept") or f.get("shows")) for f in first3]
    if len(set(concepts)) < len(concepts):
        blocks.append("two of the first three frames show the same concept")

    for i, f in enumerate(frames, 1):
        cap = f.get("caption") or ""
        low = cap.lower()
        for c in competitors:
            if c and has(c, low):
                blocks.append(f"frame {i}: names another app ('{c}') (2.3.7)")
        for pat in PRICE_RANK:
            m = re.search(pat, low)
            if m:
                blocks.append(f"frame {i}: '{m.group(0)}' in the caption (2.3.7: no prices, rankings, ratings or awards in screenshots)")
        for pat in PLATFORMS:
            if re.search(pat, low + " " + (f.get("shows") or "").lower()):
                blocks.append(f"frame {i}: another platform named (2.3.10)")
        if len(words(cap)) > 7:
            warns.append(f"frame {i}: caption has {len(words(cap))} words; keep to 7 or fewer")
        stock = [s_ for s_ in STOCK if has(s_, low)]
        if stock:
            warns.append(f"frame {i}: stock phrase '{stock[0]}' — every competitor says it")
        feat = [w for w in FEATURE_WORDS if has(w, low)]
        if feat:
            warns.append(f"frame {i}: feature-list wording ('{feat[0]}') — caption the outcome the user gets instead")
        if not f.get("real_ui", True) and i <= 3:
            warns.append(f"frame {i}: not real UI; keep composed art out of the first three frames")
    return {"ok": not blocks, "violations": blocks, "warnings": warns}


def competitor_names(path):
    with open(path, encoding="utf-8") as fh:
        snap = json.load(fh)
    out = set()
    for a in snap.get("apps", []):
        brand = re.split(r"[:\-–—|(]", (a.get("trackName") or "").lower())[0].strip()
        if len(brand) >= 5 and len(brand.split()) <= 4:
            out.add(brand)
    return out


def evaluate(plan, competitors=None):
    with open(plan, encoding="utf-8") as fh:
        data = json.load(fh)
    names = competitor_names(competitors) if competitors else set()
    names.discard(norm(data.get("app")))
    names = {c for c in names if norm(c) != norm(data.get("app"))}
    r = lint(data, names)
    return {"tool": "plan_lint", **r}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--plan")
    p.add_argument("--example", action="store_true")
    p.add_argument("--competitors", help="competitor snapshot JSON; captions naming those apps are blocked")
    p.add_argument("--format", choices=["json", "md"], default="md")
    a = p.parse_args()
    if a.example:
        print(json.dumps(EXAMPLE, indent=2))
        return
    if not a.plan:
        p.error("give --plan or --example")
    r = evaluate(a.plan, a.competitors)
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
