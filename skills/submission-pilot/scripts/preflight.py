#!/usr/bin/env python3
"""Build the pre-flight checklist for one app: only the guidelines that apply to it, in review order.

Input: a profile JSON of yes/no facts about the app (see --example). Output: a markdown checklist with the
guideline number on every line, grouped the way a reviewer meets the app.

Examples:
  preflight.py --example > profile.json      # edit it
  preflight.py --profile profile.json > preflight.md
  preflight.py --profile profile.json --format json

Guidelines revision summarised: 8 June 2026 (checked 2026-10-04). Wording is our own; check the current
text for anything you are unsure about.
"""

import argparse
import json
import sys

EXAMPLE = {
    "name": "Belayer", "platforms": ["iphone", "ipad"], "accounts": True, "login_required": True,
    "third_party_login": True, "iap": True, "subscriptions": True, "ads": False, "tracking": False,
    "ugc": True, "chat": True, "kids_category": False, "health": False, "medical": False, "finance": False,
    "crypto": False, "location": True, "background_location": False, "camera_or_mic": False,
    "ai_generated_content": False, "webview_main": False, "external_purchase_links": False,
    "loot_boxes": False, "gambling": False, "vpn": False, "uses_ota_updates": False,
    "previously_rejected_for": [],
}

BASE = [
    ("Before upload", "2.1", "Final build, tested on a device on the latest iOS and the oldest supported iOS"),
    ("Before upload", "2.1", "Fresh install, no saved data: launch, first screen, core feature — nothing crashes or hangs"),
    ("Before upload", "2.1", "Airplane mode and slow network: errors are explained, nothing spins forever"),
    ("Before upload", "2.1", "No placeholder text, test data, 'coming soon', dead buttons or staging URLs"),
    ("Before upload", "2.5.1", "Only public APIs; built with the current Xcode and SDK Apple requires"),
    ("Before upload", "2.5.2", "No code downloaded after review that adds or changes features"),
    ("Before upload", "Privacy manifest", "PrivacyInfo.xcprivacy present with reasons for every required-reason API; SDK manifests included"),
    ("Store page", "2.3.1", "Every feature in the description and screenshots is in this build"),
    ("Store page", "2.3.3", "Screenshots show the app in use, for every required device size"),
    ("Store page", "2.3.7", "Name ≤ 30, no prices, rankings, trademarks or competitor names in name/subtitle/keywords"),
    ("Store page", "2.3.10", "No other platforms named or shown"),
    ("Store page", "2.3.6", "Age rating questionnaire answered for the content as it is"),
    ("Store page", "5.1.1(i)", "Privacy policy URL loads, and the policy is also reachable inside the app"),
    ("Store page", "5.1.2", "App Privacy answers match what the app and its SDKs actually collect"),
    ("Store page", "1.5", "Support URL loads and shows a way to contact you"),
    ("Review notes", "2.1", "Steps to reach the core feature; anything non-obvious explained"),
    ("Review notes", "4.3(b)", "If the category is crowded: what is different, in two or three plain sentences"),
]

CONDITIONAL = [
    ("ipad_supported", "Before upload", "2.4.1", "Runs well on iPad (layouts, first tap, keyboard); reviewers often test on iPad"),
    ("accounts", "Before upload", "5.1.1(v)", "Account deletion inside the app (not only deactivation, not only by email)"),
    ("accounts", "Before upload", "5.1.1(v)", "No login required for features that do not need an account"),
    ("login_required", "Review notes", "2.1", "Demo account with full access and no expiry; back end on; works from another network"),
    ("third_party_login", "Before upload", "4.8", "An equivalent privacy-focused login option (e.g. Sign in with Apple) next to the social login"),
    ("iap", "Before upload", "3.1.1", "Digital goods and features unlocked only with in-app purchase"),
    ("iap", "Before upload", "3.1.1", "Restore Purchases works (non-consumables and subscriptions)"),
    ("iap", "Store page", "2.1", "Every in-app purchase is submitted with this version, with a review screenshot"),
    ("subscriptions", "Before upload", "3.1.2", "Subscription screen shows price, period, what is included, auto-renewal, links to terms and privacy"),
    ("subscriptions", "Before upload", "3.1.2", "Subscription gives ongoing value; free trial terms are clear"),
    ("ads", "Before upload", "2.5.18", "Ads are not shown in extensions, widgets or notifications; they can be closed; no ads to children"),
    ("tracking", "Before upload", "5.1.2", "App Tracking Transparency prompt shown before any tracking, with a purpose string"),
    ("ugc", "Before upload", "1.2", "Filter for objectionable content, a way to report it, a way to block users, published contact info"),
    ("ugc", "Before upload", "1.2", "Moderation that acts on reports in a timely way"),
    ("chat", "Before upload", "1.2", "Users can report and block other users in chat"),
    ("kids_category", "Before upload", "1.3", "No third-party analytics or ads that collect data; parental gate before links and purchases"),
    ("kids_category", "Before upload", "5.1.4", "Children's privacy rules (COPPA/GDPR-K) followed; policy says so"),
    ("health", "Before upload", "5.1.3", "Health data not used for ads or shared without consent; not stored in iCloud"),
    ("medical", "Before upload", "1.4.1", "Medical claims backed; regulatory clearance where required; accuracy disclosed"),
    ("finance", "Before upload", "3.2.1 / 5.1.1(ix)", "Licensed entity submits the app if it offers regulated financial services"),
    ("crypto", "Before upload", "3.1.5", "Wallet / exchange / mining rules: organisation account, licences, no on-device mining"),
    ("location", "Before upload", "5.1.1", "Location purpose string says what the user gets; app works with location denied where possible"),
    ("background_location", "Review notes", "2.5.4", "Why background location is needed, and how to see it working"),
    ("camera_or_mic", "Before upload", "5.1.1(ii)", "Camera/microphone purpose strings explain the use; nothing recorded without a visible indicator"),
    ("ai_generated_content", "Before upload", "1.2 / 4.7", "Generated content is moderated and reportable; age rating reflects what can be generated"),
    ("webview_main", "Before upload", "4.2", "Native value beyond the website (offline, device features, native navigation)"),
    ("external_purchase_links", "Before upload", "3.1.1(a) / 3.1.3", "External purchase links only under an entitlement or a reader-app rule that applies"),
    ("loot_boxes", "Store page", "3.1.1", "Odds of each item type disclosed before purchase"),
    ("gambling", "Before upload", "5.3", "Real-money gaming: licence, geo-restriction, free on the store, organisation account"),
    ("vpn", "Before upload", "5.4", "VPN apps: NEVPNManager, organisation account, data use disclosed"),
    ("uses_ota_updates", "Before upload", "2.5.2", "OTA updates limited to fixes of reviewed features; no new features over the air"),
]


def build(profile):
    p = dict(profile)
    p["ipad_supported"] = "ipad" in [x.lower() for x in p.get("platforms", [])]
    items = list(BASE)
    for flag, group, g, text in CONDITIONAL:
        if p.get(flag):
            items.append((group, g, text))
    for g in p.get("previously_rejected_for", []):
        items.append(("Before upload", g, f"Previously rejected under {g}: re-check the whole app against it, not just the screen named"))
    order = ["Before upload", "Store page", "Review notes"]
    items.sort(key=lambda x: order.index(x[0]))
    return {"tool": "preflight", "app": p.get("name"), "count": len(items),
            "items": [{"group": a, "guideline": b, "check": c} for a, b, c in items],
            "note": "Guidance based on public App Review Guidelines; Apple's decisions are their own."}


def evaluate(profile):
    with open(profile, encoding="utf-8") as fh:
        return build(json.load(fh))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--profile", help="profile JSON (see --example)")
    p.add_argument("--example", action="store_true", help="print an example profile and exit")
    p.add_argument("--format", choices=["json", "md"], default="md")
    a = p.parse_args()
    if a.example:
        print(json.dumps(EXAMPLE, indent=2))
        return
    if not a.profile:
        p.error("give --profile or --example")
    r = evaluate(a.profile)
    if a.format == "json":
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return
    print(f"# Pre-flight — {r['app'] or 'app'} ({r['count']} checks)\n")
    group = None
    for it in r["items"]:
        if it["group"] != group:
            group = it["group"]
            print(f"\n## {group}\n")
        print(f"- [ ] **{it['guideline']}** — {it['check']}")
    print(f"\n_{r['note']}_")


if __name__ == "__main__":
    sys.exit(main())
