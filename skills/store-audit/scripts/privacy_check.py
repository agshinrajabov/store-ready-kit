#!/usr/bin/env python3
"""Cross-check permissions, purpose strings, privacy manifest and privacy policy (Guideline 5.1).

Walks a project (native iOS, Android, Expo / React Native, Flutter, Unity export) and compares four
things that must agree:

  1. what the code uses        (APIs and libraries that need a permission)
  2. what the app declares     (Info.plist purpose strings, AndroidManifest permissions, Expo config)
  3. how it explains them      (purpose strings that say why, not "needs access")
  4. what the policy discloses (privacy policy text, if given)

Plus: privacy manifest for required-reason APIs, account deletion when accounts exist (5.1.1(v)),
and an equivalent privacy-focused login option when third-party login is offered (4.8).

Examples:
  privacy_check.py --project ./MyApp
  privacy_check.py --project ./MyApp --policy privacy.md --format md
  privacy_check.py --project ./MyApp --policy-url https://example.com/privacy

The scan is pattern-based: it finds evidence for a human to confirm, it does not prove absence.
"""

import argparse
import json
import os
import plistlib
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

SKIP_DIRS = {".git", "node_modules", "Pods", "build", "DerivedData", "Library", "dist", ".expo", ".dart_tool",
             "Temp", "obj", ".gradle", "vendor", "Carthage", ".build", "__pycache__", "venv", ".venv"}
CODE_EXT = {".swift", ".m", ".mm", ".h", ".kt", ".java", ".dart", ".js", ".jsx", ".ts", ".tsx", ".cs"}
DEP_FILES = {"package.json", "pubspec.yaml", "Podfile", "Podfile.lock", "build.gradle", "build.gradle.kts",
             "Package.resolved", "Package.swift"}
MAX_BYTES = 1_500_000

# capability: iOS purpose-string keys (any one satisfies), code/dependency patterns, Android permissions,
# words a privacy policy would use for the data.
CAPS = {
    "camera": {
        "ios": ["NSCameraUsageDescription"],
        "code": [r"AVCaptureDevice", r"UIImagePickerController\.SourceType\.camera", r"\.camera\b.*sourceType",
                 r"expo-camera", r"react-native-vision-camera", r"\bimage_picker\b", r"CameraX", r"camera_android",
                 r"WebCamTexture", r"\bcamera:\s*\^"],
        "android": ["android.permission.CAMERA"],
        "policy": ["camera", "photo", "image", "picture"],
    },
    "microphone": {
        "ios": ["NSMicrophoneUsageDescription"],
        "code": [r"AVAudioRecorder", r"AVAudioSession.*record", r"requestRecordPermission", r"expo-av",
                 r"expo-audio", r"MediaRecorder", r"\brecord:\s*\^", r"Microphone\.Start"],
        "android": ["android.permission.RECORD_AUDIO"],
        "policy": ["microphone", "audio", "voice", "recording"],
    },
    "photos": {
        "ios": ["NSPhotoLibraryUsageDescription", "NSPhotoLibraryAddUsageDescription"],
        "code": [r"PHPhotoLibrary", r"PHAsset", r"UIImageWriteToSavedPhotosAlbum", r"expo-media-library",
                 r"react-native-camera-roll", r"photo_manager", r"\bgallery_saver\b"],
        "android": ["android.permission.READ_MEDIA_IMAGES", "android.permission.READ_EXTERNAL_STORAGE",
                    "android.permission.READ_MEDIA_VIDEO"],
        "policy": ["photo", "image", "media", "picture"],
    },
    "location": {
        "ios": ["NSLocationWhenInUseUsageDescription", "NSLocationAlwaysAndWhenInUseUsageDescription",
                "NSLocationAlwaysUsageDescription"],
        "code": [r"CLLocationManager", r"requestWhenInUseAuthorization", r"expo-location", r"\bgeolocator\b",
                 r"react-native-geolocation", r"FusedLocationProviderClient", r"Input\.location"],
        "android": ["android.permission.ACCESS_FINE_LOCATION", "android.permission.ACCESS_COARSE_LOCATION",
                    "android.permission.ACCESS_BACKGROUND_LOCATION"],
        "policy": ["location", "gps", "geolocation"],
    },
    "contacts": {
        "ios": ["NSContactsUsageDescription"],
        "code": [r"CNContactStore", r"expo-contacts", r"react-native-contacts", r"flutter_contacts",
                 r"ContactsContract"],
        "android": ["android.permission.READ_CONTACTS"],
        "policy": ["contact", "address book"],
    },
    "calendar": {
        "ios": ["NSCalendarsUsageDescription", "NSCalendarsFullAccessUsageDescription",
                "NSCalendarsWriteOnlyAccessUsageDescription"],
        "code": [r"EKEventStore", r"expo-calendar", r"device_calendar", r"CalendarContract"],
        "android": ["android.permission.READ_CALENDAR", "android.permission.WRITE_CALENDAR"],
        "policy": ["calendar"],
    },
    "bluetooth": {
        "ios": ["NSBluetoothAlwaysUsageDescription"],
        "code": [r"CBCentralManager", r"CBPeripheralManager", r"react-native-ble", r"flutter_blue",
                 r"BluetoothLeScanner"],
        "android": ["android.permission.BLUETOOTH_SCAN", "android.permission.BLUETOOTH_CONNECT"],
        "policy": ["bluetooth"],
    },
    "motion": {
        "ios": ["NSMotionUsageDescription"],
        "code": [r"CMMotionActivityManager", r"CMPedometer", r"expo-sensors.*Pedometer", r"\bpedometer\b"],
        "android": ["android.permission.ACTIVITY_RECOGNITION"],
        "policy": ["motion", "activity", "step"],
    },
    "health": {
        "ios": ["NSHealthShareUsageDescription", "NSHealthUpdateUsageDescription"],
        "code": [r"HKHealthStore", r"react-native-health", r"\bhealth:\s*\^", r"HealthConnectClient"],
        "android": ["android.permission.health."],
        "policy": ["health"],
    },
    "tracking": {
        "ios": ["NSUserTrackingUsageDescription"],
        "code": [r"ATTrackingManager", r"advertisingIdentifier", r"expo-tracking-transparency",
                 r"app_tracking_transparency", r"react-native-tracking-transparency"],
        "android": ["com.google.android.gms.permission.AD_ID"],
        "policy": ["advertising", "tracking", "advertis", "identifier"],
    },
    "face_id": {
        "ios": ["NSFaceIDUsageDescription"],
        "code": [r"LAContext", r"deviceOwnerAuthenticationWithBiometrics", r"expo-local-authentication",
                 r"local_auth", r"BiometricPrompt"],
        "android": ["android.permission.USE_BIOMETRIC"],
        "policy": [],
    },
    "speech": {
        "ios": ["NSSpeechRecognitionUsageDescription"],
        "code": [r"SFSpeechRecognizer", r"expo-speech-recognition", r"speech_to_text", r"SpeechRecognizer"],
        "android": [],
        "policy": ["speech", "voice"],
    },
    "local_network": {
        "ios": ["NSLocalNetworkUsageDescription"],
        "code": [r"NWBrowser", r"NetServiceBrowser", r"NSBonjourServices", r"react-native-zeroconf"],
        "android": [],
        "policy": [],
    },
}

AD_SDKS = [r"GoogleMobileAds", r"google_mobile_ads", r"react-native-google-mobile-ads", r"FBAudienceNetwork",
           r"AppLovin", r"IronSource", r"UnityAds", r"com\.google\.android\.gms:play-services-ads",
           r"AppsFlyer", r"Adjust", r"FBSDKCoreKit", r"facebook_app_events"]

# Required-reason API categories (privacy manifest). Pattern -> NSPrivacyAccessedAPIType.
REQUIRED_REASON = {
    "NSPrivacyAccessedAPICategoryUserDefaults": [r"UserDefaults", r"NSUserDefaults", r"AsyncStorage",
                                                  r"shared_preferences", r"PlayerPrefs", r"react-native-mmkv"],
    "NSPrivacyAccessedAPICategoryFileTimestamp": [r"creationDate", r"modificationDate", r"NSFileCreationDate",
                                                  r"NSFileModificationDate", r"attributesOfItem", r"\bstat\("],
    "NSPrivacyAccessedAPICategorySystemBootTime": [r"systemUptime", r"mach_absolute_time"],
    "NSPrivacyAccessedAPICategoryDiskSpace": [r"volumeAvailableCapacity", r"NSFileSystemFreeSize", r"statfs\("],
    "NSPrivacyAccessedAPICategoryActiveKeyboards": [r"activeInputModes"],
}

ACCOUNT_CREATE = [r"createUser", r"createUserWithEmail", r"signUp\b", r"sign_up", r"registerUser", r"auth\.signUp",
                  r"Create account", r"Create an account", r"Sign up"]
ACCOUNT_DELETE = [r"deleteUser", r"delete_account", r"deleteAccount", r"Delete account", r"Delete my account",
                  r"auth\.admin\.deleteUser", r"currentUser\.delete", r"user\.delete\("]
THIRD_PARTY_LOGIN = [r"GoogleSignIn", r"google_sign_in", r"@react-native-google-signin", r"expo-auth-session.*google",
                     r"FBSDKLoginKit", r"flutter_facebook_auth", r"signInWithPopup", r"LoginManager"]
PRIVACY_LOGIN = [r"ASAuthorizationAppleIDProvider", r"sign_in_with_apple", r"expo-apple-authentication",
                 r"@invertase/react-native-apple-authentication", r"AppleAuthProvider", r"SignInWithApple"]

GENERIC_PURPOSE = [r"^\s*$", r"\bTODO\b", r"lorem", r"needs? (access|permission)", r"requires? (access|permission)",
                   r"^allow \$\(PRODUCT_NAME\) to access", r"^\$\(PRODUCT_NAME\) (needs|would like|wants)",
                   r"^this app (needs|requires|uses) (access to )?(the |your )?\w+\.?$", r"for (better|a better) experience",
                   r"^(camera|microphone|location|photos?)( access)?\.?$"]

EXPO_PLUGIN_KEYS = {
    "cameraPermission": "NSCameraUsageDescription",
    "microphonePermission": "NSMicrophoneUsageDescription",
    "photosPermission": "NSPhotoLibraryUsageDescription",
    "savePhotosPermission": "NSPhotoLibraryAddUsageDescription",
    "locationWhenInUsePermission": "NSLocationWhenInUseUsageDescription",
    "locationAlwaysAndWhenInUsePermission": "NSLocationAlwaysAndWhenInUseUsageDescription",
    "contactsPermission": "NSContactsUsageDescription",
    "calendarPermission": "NSCalendarsUsageDescription",
    "userTrackingPermission": "NSUserTrackingUsageDescription",
    "faceIDPermission": "NSFaceIDUsageDescription",
    "motionPermission": "NSMotionUsageDescription",
}


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.endswith(".xcassets")]
        for f in filenames:
            yield os.path.join(dirpath, f)


def read(path):
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return ""
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""


def rel(path, root):
    return os.path.relpath(path, root)


def collect(root):
    plists, manifests, xcprivacy, expo, code = [], [], [], [], {}
    for path in walk(root):
        name = os.path.basename(path)
        ext = os.path.splitext(name)[1]
        if name == "Info.plist" and "Tests" not in path:
            plists.append(path)
        elif name == "AndroidManifest.xml" and "/build/" not in path:
            manifests.append(path)
        elif name == "PrivacyInfo.xcprivacy":
            xcprivacy.append(path)
        elif name in ("app.json", "app.config.json"):
            expo.append(path)
        if ext in CODE_EXT or name in DEP_FILES:
            code[path] = read(path)
    return plists, manifests, xcprivacy, expo, code


def load_plist(path):
    try:
        with open(path, "rb") as fh:
            return plistlib.load(fh)
    except Exception:
        return {}


def expo_declarations(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        return {}, []
    exp = data.get("expo", data)
    info = dict((exp.get("ios") or {}).get("infoPlist") or {})
    perms = list((exp.get("android") or {}).get("permissions") or [])
    for plugin in exp.get("plugins") or []:
        if isinstance(plugin, list) and len(plugin) == 2 and isinstance(plugin[1], dict):
            for k, v in plugin[1].items():
                if k in EXPO_PLUGIN_KEYS and isinstance(v, str):
                    info.setdefault(EXPO_PLUGIN_KEYS[k], v)
    perms = [p if "." in p else f"android.permission.{p}" for p in perms]
    return info, perms


def android_permissions(path):
    try:
        tree = ET.parse(path)
    except ET.ParseError:
        return []
    ns = "{http://schemas.android.com/apk/res/android}name"
    return [el.get(ns) for el in tree.iter() if el.tag in ("uses-permission", "uses-permission-sdk-23") and el.get(ns)]


def find(patterns, code, root, limit=3):
    hits = []
    for path, text in code.items():
        for pat in patterns:
            if re.search(pat, text):
                hits.append(f"{rel(path, root)} ({pat.replace(chr(92), '')})")
                break
        if len(hits) >= limit:
            break
    return hits


def finding(sev, guideline, title, evidence, fix):
    return {"severity": sev, "guideline": guideline, "title": title, "evidence": evidence, "fix": fix}


def check(root, policy_text=None):
    plists, manifests, xcprivacy, expo, code = collect(root)
    declared_ios = {}
    for p in plists:
        for k, v in load_plist(p).items():
            if k.endswith("UsageDescription"):
                declared_ios[k] = (v if isinstance(v, str) else "", rel(p, root))
    declared_android = {}
    for m in manifests:
        for perm in android_permissions(m):
            declared_android[perm] = rel(m, root)
    for e in expo:
        info, perms = expo_declarations(e)
        for k, v in info.items():
            if k.endswith("UsageDescription"):
                declared_ios.setdefault(k, (v if isinstance(v, str) else "", rel(e, root)))
        for perm in perms:
            declared_android.setdefault(perm, rel(e, root))

    has_ios = bool(plists or expo or any(p.endswith((".swift", ".m")) for p in code))
    has_android = bool(manifests or expo or any(p.endswith((".kt", ".java")) for p in code))
    findings, used = [], []
    policy = (policy_text or "").lower()

    for cap, spec in CAPS.items():
        hits = find(spec["code"], code, root)
        ios_keys = [k for k in spec["ios"] if k in declared_ios]
        android_keys = [k for k in declared_android if any(k.startswith(a) for a in spec["android"])]
        if hits:
            used.append(cap)
        if hits and has_ios and spec["ios"] and not ios_keys:
            findings.append(finding("HIGH", "5.1.1", f"{cap}: code uses it, no purpose string declared",
                                    hits + [f"expected one of: {', '.join(spec['ios'])}"],
                                    "Add the purpose string; iOS terminates the app the moment the API is called without it."
                                    + (" In Expo, set it through the library's config-plugin option or ios.infoPlist; "
                                       "otherwise the build gets a generic default that does not say why." if expo else "")))
        if ios_keys and not hits and not android_keys:
            findings.append(finding("LOW", "5.1.1", f"{cap}: purpose string declared but no use found",
                                    [f"{k} in {declared_ios[k][1]}" for k in ios_keys],
                                    "Remove it if nothing uses it (a reviewer may ask what it is for); keep it if an SDK needs it and say which."))
        for k in ios_keys:
            text, where = declared_ios[k]
            if any(re.search(g, text, re.I) for g in GENERIC_PURPOSE) or len(text.strip()) < 25:
                findings.append(finding("MEDIUM", "5.1.1(ii)", f"{cap}: purpose string does not explain why",
                                        [f'{k} = "{text}" ({where})'],
                                        "Say what the user gets: 'Scan a receipt to add it to this month's expenses' — not 'needs camera access'."))
        if hits and has_android and spec["android"] and not android_keys and cap not in ("face_id", "local_network", "speech"):
            findings.append(finding("MEDIUM", "Play policy / runtime", f"{cap}: Android code uses it, no permission in the manifest",
                                    hits, "Declare the permission or confirm the library merges it in."))
        if (hits or ios_keys or android_keys) and policy_text is not None and spec["policy"]:
            if not any(w in policy for w in spec["policy"]):
                findings.append(finding("MEDIUM", "5.1.1(i)", f"{cap}: privacy policy does not mention this data",
                                        [f"policy has none of: {', '.join(spec['policy'])}"],
                                        "Describe what is collected, why, how long it is kept and who it is shared with."))

    ads = find(AD_SDKS, code, root)
    if ads:
        used.append("advertising SDK")
        if has_ios and "NSUserTrackingUsageDescription" not in declared_ios:
            findings.append(finding("MEDIUM", "5.1.2", "Ad/attribution SDK present, no App Tracking Transparency purpose string",
                                    ads, "Either show the ATT prompt before any tracking (and add the string) or configure the SDKs for non-tracking use and declare that in App Privacy."))

    if policy_text is None:
        findings.append(finding("HIGH", "5.1.1(i)", "No privacy policy supplied to the audit",
                                ["--policy / --policy-url not given"],
                                "Every app needs a privacy policy link in App Store Connect and inside the app. Supply it so it can be checked."))
    elif len(policy.strip()) < 400:
        findings.append(finding("MEDIUM", "5.1.1(i)", "Privacy policy is very short",
                                [f"{len(policy.strip())} characters"],
                                "Cover what is collected, how, why, retention and deletion, third parties, and a contact."))

    reasons_needed = {cat: find(pats, code, root, 2) for cat, pats in REQUIRED_REASON.items()}
    reasons_needed = {k: v for k, v in reasons_needed.items() if v}
    if has_ios and reasons_needed:
        declared_types = set()
        for x in xcprivacy:
            data = load_plist(x)
            for item in data.get("NSPrivacyAccessedAPITypes", []) or []:
                declared_types.add(item.get("NSPrivacyAccessedAPIType"))
        missing = [k for k in reasons_needed if k not in declared_types]
        if missing:
            ev = [f"{k}: {', '.join(reasons_needed[k])}" for k in missing]
            if not xcprivacy:
                ev.insert(0, "no PrivacyInfo.xcprivacy in the project")
            findings.append(finding("MEDIUM", "Privacy manifest (ITMS-91053)", "Required-reason APIs used without a declared reason",
                                    ev, "Add PrivacyInfo.xcprivacy with NSPrivacyAccessedAPITypes and an approved reason code for each category. "
                                        "Cross-platform storage libraries usually trigger UserDefaults."))

    creates = find(ACCOUNT_CREATE, code, root)
    if creates and not find(ACCOUNT_DELETE, code, root):
        findings.append(finding("HIGH", "5.1.1(v)", "Account creation found, no account deletion",
                                creates, "Offer in-app account deletion (not just deactivation, not only by email)."))
    tpl = find(THIRD_PARTY_LOGIN, code, root)
    if tpl and has_ios and not find(PRIVACY_LOGIN, code, root):
        findings.append(finding("MEDIUM", "4.8", "Third-party login without an equivalent privacy-focused option",
                                tpl, "Offer Sign in with Apple (or another login that limits data to name and email, allows a private email, and does not track)."))

    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    findings.sort(key=lambda f: order[f["severity"]])
    return {
        "tool": "privacy_check",
        "project": os.path.abspath(root),
        "platforms": [p for p, on in (("ios", has_ios), ("android", has_android)) if on],
        "capabilities_used": sorted(set(used)),
        "declared_ios": sorted(declared_ios),
        "declared_android": sorted(declared_android),
        "files": {"info_plist": [rel(p, root) for p in plists], "android_manifest": [rel(m, root) for m in manifests],
                  "privacy_manifest": [rel(x, root) for x in xcprivacy], "expo_config": [rel(e, root) for e in expo]},
        "findings": findings,
        "counts": {s: sum(1 for f in findings if f["severity"] == s) for s in order},
        "note": "Guidance based on public App Review Guidelines; Apple's decisions are their own.",
    }


def to_markdown(r):
    c = r["counts"]
    lines = [f"# Privacy consistency (5.1) — {os.path.basename(r['project'])}", "",
             f"Platforms: {', '.join(r['platforms']) or 'none detected'} · uses: {', '.join(r['capabilities_used']) or 'nothing detected'}",
             f"Findings: {c['HIGH']} high · {c['MEDIUM']} medium · {c['LOW']} low", ""]
    for f in r["findings"]:
        lines += [f"### [{f['severity']}] {f['title']} ({f['guideline']})", ""]
        lines += [f"- {e}" for e in f["evidence"]]
        lines += [f"- **Fix:** {f['fix']}", ""]
    lines.append("_" + r["note"] + "_")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--project", required=True, help="project root")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--policy", help="privacy policy as a local text/markdown/html file")
    g.add_argument("--policy-url", help="privacy policy URL (fetched once)")
    p.add_argument("--format", choices=["json", "md"], default="json")
    args = p.parse_args()

    policy, unreachable = None, None
    if args.policy:
        policy = read(args.policy)
    elif args.policy_url:
        # This is a live network fetch. Offline, save the policy to a file and pass --policy instead.
        req = urllib.request.Request(args.policy_url, headers={"User-Agent": "store-ready-kit/privacy_check"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                policy = re.sub(r"<[^>]+>", " ", resp.read().decode("utf-8", "ignore"))
        except Exception as exc:
            unreachable = f"{args.policy_url}: {exc}"
            policy = ""
    result = check(args.project, policy)
    if unreachable:
        result["findings"].insert(0, finding("HIGH", "5.1.1(i) / 2.1", "Privacy policy URL did not load", [unreachable],
                                             "The policy must load for the reviewer. Fix the URL or hosting; if you are "
                                             "offline, re-run with --policy <file>."))
        # Nothing can be said about a policy that did not load beyond the fact that it did not load.
        result["findings"] = result["findings"][:1] + [f for f in result["findings"][1:] if f["guideline"] != "5.1.1(i)"]
        result["counts"] = {s_: sum(1 for f in result["findings"] if f["severity"] == s_) for s_ in ("HIGH", "MEDIUM", "LOW")}
    print(to_markdown(result) if args.format == "md" else json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
