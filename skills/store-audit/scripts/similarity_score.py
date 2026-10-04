#!/usr/bin/env python3
"""Score how much an app listing looks like the apps already in its niche (Guideline 4.3).

Reads your listing (JSON, format in references/listing-format.md) and a competitor snapshot
from competitor_scan.py, and returns a clone-signal score from 0 to 100 with every signal's
evidence, the nearest neighbours, and a verdict:

  PASS   < 30   no strong clone signal; still read the evidence
  WARN   30-54  a reviewer could reasonably file this with the category; differentiate first
  FLAG   >= 55  or any hard trigger; expect a 4.3 conversation unless something changes

The score measures resemblance, not quality, and it cannot see the running app. It is the
input to a judgement, not the judgement. Deterministic: the same files give the same score.

Examples:
  similarity_score.py --listing listing.json --competitors competitors.json
  similarity_score.py --listing listing.json --competitors competitors.json --format md
  similarity_score.py --listing listing.json --competitors competitors.json --catalog hypercasual-game
"""

import argparse
import json
import math
import re
import sys
from collections import Counter

VERSION = "1.0"

STOPWORDS = set("""
a about above after again all also am an and any app apps are as at be because been before being below
between both but by can could did do does doing down during each few for from further get got had has have
having he her here hers him his how i if in into is it its itself just let like make me more most my new no
nor not now of off on once one only or other our out over own play same she should so some such than that
the their them then there these they this those through to too under until up use using very via want was
we were what when where which while who whom why will with you your yours ios iphone ipad free best top
game games feature features available store download
""".split())

# Apple names these categories in 4.3(b) (June 2026 text) as established or low-effort.
# Paraphrased keys, matched against name, subtitle, keywords, category and description.
SATURATED = {
    "dating": ["dating", "date app", "find singles", "match with singles", "swipe to match"],
    "flashlight": ["flashlight", "torch light", "led torch"],
    "sound effects": ["sound effects", "soundboard", "sound board", "prank sounds"],
    "wallpaper": ["wallpaper", "wallpapers", "live wallpaper"],
    "simple timer": ["simple timer", "countdown timer", "kitchen timer", "stopwatch timer"],
    "fortune telling": ["fortune telling", "fortune teller", "tarot", "horoscope", "astrology", "palm reading"],
    "drinking game": ["drinking game", "drinking games", "beer pong", "never have i ever"],
    "kama sutra": ["kama sutra", "sex positions"],
    "fart/burp": ["fart", "burp"],
}

GENERIC_CAPTIONS = [
    "relax", "unwind", "addictive", "brain training", "train your brain", "1000+ levels", "hundreds of levels",
    "thousands of levels", "challenge your mind", "satisfying", "stress relief", "best app", "easy to use",
    "simple and easy", "boost your", "all in one", "#1", "number one", "no wifi", "offline game",
]

# Template-trait catalogues. A trait is something that, on its own, is fine; many of them together
# are the category's default package. Full descriptions live in references/clone-signals.md.
CATALOGS = {
    "hypercasual-game": [
        ("HC01", "Flat-shaded low-poly or stock-asset geometry with no art direction of its own"),
        ("HC02", "Near-full-chroma primary palette, often pushed further by post-processing"),
        ("HC03", "Default gradient sky / floating island / empty ground plane"),
        ("HC04", "Chunky outlined candy buttons with a darker bottom lip"),
        ("HC05", "Bold rounded display font with white fill and ink outline"),
        ("HC06", "Hearts / lives row"),
        ("HC07", "Coin pill with a '+' shop shortcut in the corner"),
        ("HC08", "'Level N' as the screen title"),
        ("HC09", "Big PLAY button bottom-centre on the home screen"),
        ("HC10", "Win card with confetti, stars and a CONTINUE button"),
        ("HC11", "Fail sheet stacked with coloured paid / ad / coin offers"),
        ("HC12", "Stock props (blob clouds, lollipop trees, capsule characters)"),
        ("HC13", "Default engine post-processing look (bloom + vignette + saturation boost)"),
        ("HC14", "Store screenshots = bright capture + big caption band"),
        ("HC15", "Generated levels with no authored first session"),
        ("HC16", "Engine splash or template branding before the first frame"),
    ],
    "utility-app": [
        ("UT01", "Stock SF Symbol or clip-art glyph on a gradient as the icon"),
        ("UT02", "Hard paywall before the user has done anything"),
        ("UT03", "Weekly subscription pre-selected as the default plan"),
        ("UT04", "Onboarding carousel that promises outcomes the app does not deliver"),
        ("UT05", "Core screen is one list or one button with no domain-specific depth"),
        ("UT06", "Feature set matches the top 5 apps in the niche one-for-one"),
        ("UT07", "Generic name built from category keywords"),
        ("UT08", "Template UI kit visible unchanged (default tab bar, stock illustrations)"),
        ("UT09", "Rate-us prompt in the first session"),
        ("UT10", "No offline / empty / error states beyond the template's"),
    ],
    "ai-wrapper": [
        ("AI01", "Chat screen that mirrors a general-purpose assistant with a new skin"),
        ("AI02", "Value proposition is a third-party model's name, not a task"),
        ("AI03", "Prompt templates as the only domain content"),
        ("AI04", "Paywall before the first useful answer"),
        ("AI05", "No handling of the model being wrong, slow or unavailable"),
        ("AI06", "Same app published under several names or niches"),
        ("AI07", "Generated icon / screenshots in the house style of other AI apps"),
        ("AI08", "Built on an app-generation service with its scaffold unchanged"),
    ],
}

WEIGHTS = {
    "text_similarity": 15,
    "name_genericness": 10,
    "vocabulary": 10,
    "saturated_category": 15,
    "template_traits": 20,
    "monetisation": 15,
    "content": 10,
    "lineage": 15,
    "captions": 5,
}


def tokens(text):
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9+#\s-]", " ", text)
    out = []
    for raw in text.split():
        w = raw.strip("-")
        if len(w) < 2 or w in STOPWORDS or w.isdigit():
            continue
        if w.endswith("s") and len(w) > 3 and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    return out


def tfidf_vectors(docs):
    df = Counter()
    tfs = []
    for d in docs:
        tf = Counter(d)
        tfs.append(tf)
        df.update(tf.keys())
    n = len(docs)
    idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
    vecs = []
    for tf in tfs:
        total = sum(tf.values()) or 1
        vecs.append({t: (c / total) * idf[t] for t, c in tf.items()})
    return vecs, df


def cosine(a, b):
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(t, 0.0) for t, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def listing_text(lst):
    parts = [lst.get("name"), lst.get("subtitle"), (lst.get("keywords") or "").replace(",", " "),
             lst.get("description")]
    parts += [s.get("caption", "") for s in lst.get("screenshots", []) if isinstance(s, dict)]
    return " ".join(p for p in parts if p)


def comp_text(app):
    return " ".join(p for p in [app.get("trackName"), app.get("subtitle"), app.get("description")] if p)


def signal(key, points, evidence, assessed=True, hard=False, fix=None):
    return {"key": key, "max": WEIGHTS[key], "points": round(min(points, WEIGHTS[key]), 2),
            "assessed": assessed, "hard": hard, "evidence": evidence, "fix": fix or ""}


def score_text(lst, comps):
    """How close the listing sits to its niche, relative to how close niche members sit to each other.

    Raw TF-IDF cosines depend on description length and niche vocabulary, so a fixed threshold misleads.
    The baseline is the median nearest-neighbour cosine among the competitors themselves: a listing whose
    nearest neighbour is as close as the niche's typical pair reads as "one of them".
    """
    if len(comps) < 3:
        return signal("text_similarity", 0, ["fewer than 3 competitors in the snapshot"], assessed=False), []
    docs = [tokens(listing_text(lst))] + [tokens(comp_text(a)) for a in comps]
    vecs, _ = tfidf_vectors(docs)
    mine, others = vecs[0], vecs[1:]
    sims = sorted(((round(cosine(mine, v), 3), app) for app, v in zip(comps, others)), key=lambda x: -x[0])
    top = sims[0][0]
    nn_base = []
    for i, v in enumerate(others):
        nn_base.append(max(cosine(v, w) for j, w in enumerate(others) if j != i))
    nn_base.sort()
    baseline = nn_base[len(nn_base) // 2] or 1e-6
    top3 = sum(s for s, _ in sims[:3]) / 3
    ratio = top3 / baseline
    pts = max(0.0, (ratio - 0.4) / 0.6) * 15
    nn = [{"score": s, "trackName": a.get("trackName"), "trackId": a.get("trackId"),
           "userRatingCount": a.get("userRatingCount")} for s, a in sims[:5]]
    ev = [f"closest listing: {nn[0]['trackName']} (cosine {top}); mean of top 3 = {top3:.3f}",
          f"niche baseline (median nearest-neighbour cosine between competitors) = {baseline:.3f}; ratio {ratio:.2f}"]
    fix = ("Rewrite the description around what only this app does; lead with the specific situation and "
           "outcome, not the category's shared vocabulary.")
    return signal("text_similarity", pts, ev, fix=fix), nn


def score_name(lst, comps):
    name = lst.get("name") or ""
    if not comps or not name:
        return signal("name_genericness", 0, ["no name or no competitors"], assessed=False)
    brand, _, tail = name.partition(":")
    if not tail:
        brand, _, tail = name.partition(" - ")
    name_tokens = set(tokens(name))
    tail_tokens = set(tokens(tail)) if tail else set()
    comp_names = [set(tokens(a.get("trackName"))) for a in comps]
    common = []
    for t in sorted(name_tokens):
        share = sum(1 for cn in comp_names if t in cn) / len(comp_names)
        if share >= 0.10:
            common.append((t, round(share, 2)))
    generic_share = len(common) / len(name_tokens) if name_tokens else 0
    pts = generic_share * 6
    ev = [f"name tokens shared with >=10% of competitor names: "
          + (", ".join(f"{t} ({int(s * 100)}%)" for t, s in common) or "none")]
    sub = set(tokens(lst.get("subtitle")))
    kw = set(tokens((lst.get("keywords") or "").replace(",", " ")))
    if tail_tokens and tail_tokens & {t for t, _ in common}:
        pts += 3
        ev.append(f"'{brand.strip()}: {tail.strip()}' pattern: brand plus category keywords in the name")
    stack = (sub | tail_tokens) & {t for cn in comp_names for t in cn}
    if len(stack) >= 4:
        pts += 1
        ev.append(f"name+subtitle reuse {len(stack)} words that appear in competitor names")
    if kw & set(tokens(name)):
        ev.append("keyword field repeats words already in the name (wasted slots, 2.3.7-adjacent)")
    fix = ("Let the name carry the brand and one honest descriptor at most; make the subtitle a promise in "
           "your own words rather than a stack of the niche's search terms.")
    return signal("name_genericness", pts, ev, fix=fix)


def score_vocabulary(lst, comps):
    if not comps:
        return signal("vocabulary", 0, ["no competitors"], assessed=False)
    docs = [tokens(comp_text(a)) for a in comps]
    df = Counter()
    for d in docs:
        df.update(set(d))
    mine = Counter(tokens(" ".join(p for p in [lst.get("name"), lst.get("subtitle"), lst.get("description")] if p)))
    top_mine = [t for t, _ in mine.most_common(25)]
    if not top_mine:
        return signal("vocabulary", 0, ["listing has no text"], assessed=False)
    shared = [t for t in top_mine if df[t] / len(docs) >= 0.30]
    own = [t for t in top_mine if df[t] == 0]
    ratio = len(shared) / len(top_mine)
    pts = max(0.0, (ratio - 0.15) / 0.5) * 10
    ev = [f"{len(shared)} of your 25 most-used words appear in >=30% of competitor listings: {', '.join(shared[:12]) or 'none'}",
          f"words no competitor uses: {', '.join(own[:12]) or 'none'}"]
    fix = "Your own vocabulary is the differentiation evidence; put the words no competitor uses in the first lines."
    return signal("vocabulary", pts, ev, fix=fix)


def score_saturated(lst):
    hay = " ".join([lst.get("name") or "", lst.get("subtitle") or "", lst.get("keywords") or "",
                    lst.get("category") or "", (lst.get("description") or "")[:600]]).lower()
    hits = []
    for cat, phrases in SATURATED.items():
        for ph in phrases:
            if re.search(r"\b" + re.escape(ph) + r"\b", hay):
                hits.append((cat, ph))
                break
    declared = lst.get("niche_saturated")
    if not hits and not declared:
        return signal("saturated_category", 0, ["no category named in 4.3(b) detected"])
    cats = sorted({c for c, _ in hits}) or ["declared saturated"]
    ev = [f"listing matches a category 4.3(b) names: {', '.join(cats)}"]
    diff = lst.get("differentiators") or []
    pts = 15 if len(diff) < 2 else 10
    ev.append(f"{len(diff)} stated differentiators (4.3(b) asks for a 'meaningfully different or improved experience')")
    fix = ("In a named category the burden is on you: name the one experience no existing app offers, make it "
           "visible in the first screenshot and the first minute, and say it in the App Review notes.")
    return signal("saturated_category", pts, ev, fix=fix)


def score_traits(lst, catalog_name):
    traits = lst.get("traits")
    catalog_name = catalog_name or lst.get("trait_catalog")
    if not traits or not catalog_name:
        return signal("template_traits", 0, ["no trait checklist filled in"], assessed=False)
    catalog = CATALOGS.get(catalog_name)
    if not catalog:
        raise SystemExit(f"unknown catalog '{catalog_name}'; choose from {', '.join(CATALOGS)}")
    ids = [i for i, _ in catalog]
    matched = [i for i in ids if traits.get(i) is True]
    partial = [i for i in ids if traits.get(i) == "partial"]
    answered = [i for i in ids if i in traits]
    if len(answered) < len(ids) // 2:
        return signal("template_traits", 0, [f"only {len(answered)} of {len(ids)} traits answered"], assessed=False)
    share = (len(matched) + 0.5 * len(partial)) / len(answered)
    pts = max(0.0, (share - 0.2) / 0.6) * 20
    labels = dict(catalog)
    ev = [f"{len(matched)} full + {len(partial)} partial of {len(answered)} '{catalog_name}' template traits"]
    ev += [f"{i}: {labels[i]}" for i in matched[:8]]
    fix = ("Pick the one idea that is yours (often already in the name or the core mechanic) and let it replace "
           "the template traits on screen — art, HUD, win/fail moments, icon.")
    return signal("template_traits", pts, ev, fix=fix)


def score_monetisation(lst):
    m = lst.get("monetisation")
    if not m:
        return signal("monetisation", 0, ["no monetisation details given"], assessed=False)
    pts, ev = 0.0, []
    iap = m.get("iap_count", 0)
    cons = m.get("consumable_count", 0)
    rewarded = m.get("rewarded_placements", 0)
    prompts = m.get("purchase_prompts_first_10_min", 0)
    if iap >= 6:
        pts += 3; ev.append(f"{iap} in-app purchases at launch")
    if cons >= 4:
        pts += 2; ev.append(f"{cons} consumables (coin-pack ladder)")
    if rewarded >= 4:
        pts += 2; ev.append(f"{rewarded} rewarded-ad placements")
    if m.get("interstitial"):
        pts += 2; ev.append(f"interstitials: {m['interstitial']}")
    if prompts >= 3:
        pts += 4; ev.append(f"{prompts} purchase/ad prompts in the first 10 minutes")
    if m.get("paywall_before_value"):
        pts += 4; ev.append("paywall before the user gets any value")
    if m.get("sink_without_content"):
        pts += 2; ev.append("currency sink exists mainly to give packs a job")
    if not ev:
        ev.append("monetisation surface is modest for the content")
    fix = ("Cut the first session to at most one stated purchase and one optional ad; keep the other products "
           "in App Store Connect, unattached, for a later version.")
    return signal("monetisation", pts, ev, fix=fix)


def score_content(lst):
    c = lst.get("content")
    if not c:
        return signal("content", 0, ["no content details given"], assessed=False)
    pts, ev = 0.0, []
    if c.get("generated") and not c.get("authored_onboarding"):
        pts += 5; ev.append("content is generated and the first session is not hand-authored")
    if c.get("repeats_in_first_session"):
        pts += 2; ev.append("content repeats within the first session")
    if c.get("silent_failures"):
        pts += 2; ev.append("inputs that do nothing with no feedback")
    if c.get("lasting_value") is False:
        pts += 3; ev.append("little lasting value beyond the first session (4.2)")
    if not ev:
        ev.append("first session is authored and responsive")
    fix = "Hand-author the first five minutes: one idea per step, every input answered, no repeats."
    return signal("content", pts, ev, fix=fix)


def score_lineage(lst):
    a = lst.get("account")
    if not a:
        return signal("lineage", 0, ["no account details given"], assessed=False)
    pts, ev, hard = 0.0, [], False
    similar = a.get("similar_apps_on_account", 0)
    if similar >= 2:
        pts, hard = 15, True; ev.append(f"{similar} similar apps already on this account (4.3(a))")
    elif similar == 1:
        pts += 8; ev.append("one similar app already on this account")
    if a.get("template_or_generator"):
        pts += 10; hard = True
        ev.append("built from a commercial template or app-generation service (4.2.6)")
    if a.get("reused_project_assets"):
        pts += 5; ev.append("project copied from another app (shared asset GUIDs / binary lineage)")
    if a.get("prior_4_3_rejections", 0) >= 2:
        pts += 5; hard = True
        ev.append(f"{a['prior_4_3_rejections']} earlier 4.3 rejections on this concept")
    if not ev:
        ev.append("no lineage concerns given")
    fix = ("Do not answer a 4.3 with a new bundle ID, a new account or a rename; fix the product under the "
           "same record and say so in the review notes.")
    return signal("lineage", pts, ev, hard=hard, fix=fix)


def score_captions(lst):
    shots = [s for s in lst.get("screenshots", []) if isinstance(s, dict)]
    if not shots:
        return signal("captions", 0, ["no screenshot captions given"], assessed=False)
    hits = []
    for s in shots:
        cap = (s.get("caption") or "").lower()
        for g in GENERIC_CAPTIONS:
            if g in cap:
                hits.append((s.get("caption"), g))
                break
    pts = min(len(hits), 3) / 3 * 5
    ev = [f"{len(hits)} of {len(shots)} captions use stock phrases: "
          + ("; ".join(f"'{c}'" for c, _ in hits[:3]) or "none")]
    fix = "Caption the outcome only this app gives; show the distinctive moment in frame 1."
    return signal("captions", pts, ev, fix=fix)


def run(listing, snapshot, catalog=None, exclude_ids=()):
    comps = [a for a in snapshot.get("apps", [])
             if str(a.get("trackId")) not in {str(x) for x in exclude_ids}
             and (a.get("trackName") or "").strip().lower() != (listing.get("name") or "").strip().lower()]
    text_sig, neighbours = score_text(listing, comps)
    signals = [
        text_sig,
        score_name(listing, comps),
        score_vocabulary(listing, comps),
        score_saturated(listing),
        score_traits(listing, catalog),
        score_monetisation(listing),
        score_content(listing),
        score_lineage(listing),
        score_captions(listing),
    ]
    assessed = [s for s in signals if s["assessed"]]
    possible = sum(s["max"] for s in assessed)
    got = sum(s["points"] for s in assessed)
    score = round(100 * got / possible, 1) if possible else 0.0
    coverage = round(possible / sum(WEIGHTS.values()), 2)
    hard = [s["key"] for s in signals if s["hard"]]
    by = {s["key"]: s for s in signals}

    def share(key):
        x = by[key]
        return x["points"] / x["max"] if x["assessed"] else 0.0

    # Combination rules: patterns that the 4.3(b) text names directly, regardless of the total.
    combos = []
    if share("template_traits") >= 0.6 and max(share("monetisation"), share("content")) >= 0.5:
        combos.append("category package: the niche's template on screen plus a monetisation-first or generated "
                      "first session (the 'low-effort' prong)")
    if by["saturated_category"]["assessed"] and by["saturated_category"]["points"] >= 15:
        combos.append("named category without a stated, meaningful difference")
    hard += combos
    page_twin = all(share(k) >= 0.8 for k in ("text_similarity", "name_genericness", "vocabulary"))
    if hard or score >= 55:
        verdict = "FLAG"
    elif score >= 30 or by["saturated_category"]["points"] > 0 or page_twin:
        # A category 4.3(b) names is never a clean pass: the burden of showing a difference is on the app.
        # A store page that reads like the niche's is the "indistinguishable" prong as the reviewer meets it.
        verdict = "WARN"
    else:
        verdict = "PASS"
    return {
        "tool": "similarity_score", "version": VERSION,
        "app": listing.get("name"),
        "score": score, "verdict": verdict, "coverage": coverage, "hard_triggers": hard,
        "store_page_twin": page_twin,
        "competitors_compared": len(comps),
        "nearest_neighbours": neighbours,
        "signals": signals,
        "notes": [
            "Resemblance score, not a quality score; it cannot see the running app.",
            "Signals not assessed are left out of the denominator; low coverage means a less reliable score.",
            "Guidance based on public App Review Guidelines; Apple's decisions are their own.",
        ],
    }


def to_markdown(r):
    lines = [f"# 4.3 clone-signal score — {r['app']}", "",
             f"**{r['verdict']}** · score {r['score']}/100 · coverage {int(r['coverage'] * 100)}% · "
             f"{r['competitors_compared']} competitors compared", ""]
    if r["hard_triggers"]:
        lines += [f"Hard triggers: {', '.join(r['hard_triggers'])}", ""]
    lines += ["| Signal | Points | Evidence |", "|---|---|---|"]
    for s in r["signals"]:
        pts = f"{s['points']}/{s['max']}" if s["assessed"] else "not assessed"
        lines.append(f"| {s['key']} | {pts} | {'<br>'.join(s['evidence'])} |")
    if r["nearest_neighbours"]:
        lines += ["", "Nearest neighbours:", ""]
        lines += [f"- {n['trackName']} — cosine {n['score']} ({n['userRatingCount'] or 0} ratings)"
                  for n in r["nearest_neighbours"]]
    fixes = [s for s in sorted(r["signals"], key=lambda s: -s["points"]) if s["assessed"] and s["points"] >= s["max"] * 0.4]
    if fixes:
        lines += ["", "Where to differentiate first:", ""]
        lines += [f"{i}. **{s['key']}** — {s['fix']}" for i, s in enumerate(fixes, 1)]
    lines += ["", "_" + r["notes"][-1] + "_"]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--listing", help="your listing JSON (see references/listing-format.md)")
    p.add_argument("--competitors", help="snapshot JSON from competitor_scan.py")
    p.add_argument("--catalog", choices=sorted(CATALOGS), help="template-trait catalogue (overrides listing.trait_catalog)")
    p.add_argument("--exclude-id", action="append", default=[], help="App Store ID to leave out (e.g. your own live app)")
    p.add_argument("--format", choices=["json", "md"], default="json")
    p.add_argument("--list-catalogs", action="store_true", help="print the trait catalogues and exit")
    args = p.parse_args()

    if args.list_catalogs:
        for name, items in CATALOGS.items():
            print(name)
            for i, label in items:
                print(f"  {i}  {label}")
        return
    if not args.listing or not args.competitors:
        p.error("--listing and --competitors are required")

    with open(args.listing, encoding="utf-8") as fh:
        listing = json.load(fh)
    with open(args.competitors, encoding="utf-8") as fh:
        snapshot = json.load(fh)
    result = run(listing, snapshot, args.catalog, args.exclude_id)
    print(to_markdown(result) if args.format == "md" else json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
