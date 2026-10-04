#!/usr/bin/env python3
"""Find what makes a build look unfinished or risky to a reviewer (Guidelines 2.1, 2.3, 2.5.2, 4.2).

Scans a project and, optionally, a listing JSON for:

  2.1   placeholder and lorem text in user-facing strings, dev/staging endpoints, test credentials
  2.3   beta wording, other-platform names and prices in the metadata
  2.5.2 code that downloads or runs code after review (OTA updaters, eval of fetched JS, dynamic loading)
  4.2   a remote website wrapped in a web view as the whole app
  4.2.6 app-generation scaffolds left in place

Examples:
  completeness_scan.py --project ./MyApp
  completeness_scan.py --project ./MyApp --listing listing.json --format md

Pattern-based: it points at lines for a human to check. It cannot run the app, so crashes, dead
buttons and empty states still need the manual pass in references/completeness-checklist.md.
"""

import argparse
import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", "Pods", "build", "DerivedData", "Library", "dist", ".expo", ".dart_tool",
             "Temp", "obj", ".gradle", "vendor", "Carthage", ".build", "__pycache__", "venv", ".venv", "test",
             "tests", "__tests__", "Tests", "androidTest", "fixtures", "mocks", "__mocks__", "storybook"}
CODE_EXT = {".swift", ".m", ".mm", ".kt", ".java", ".dart", ".js", ".jsx", ".ts", ".tsx", ".cs", ".vue", ".svelte"}
STRING_EXT = {".strings", ".stringsdict", ".xcstrings", ".arb", ".xml", ".json", ".plist", ".html"}
CONFIG_NAMES = {"package.json", "pubspec.yaml", "app.json", "app.config.js", "app.config.ts", "Podfile",
                "build.gradle", "build.gradle.kts", "Info.plist", "capacitor.config.json", "capacitor.config.ts"}
MAX_BYTES = 1_500_000

PLACEHOLDER = r"(lorem ipsum|dolor sit amet|coming soon|placeholder text|sample text|your text here|" \
              r"under construction|dummy (text|data|content)|test user|john doe|jane doe|asdf|qwerty|" \
              r"insert (text|title|description) here|\bTBD\b|\bTODO\b|\bFIXME\b|feature not (yet )?available|" \
              r"not implemented)"
STRING_LITERAL = re.compile(r"([\"'`])((?:(?!\1).){0,200}?)\1")
DEV_ENDPOINT = re.compile(r"https?://(localhost|127\.0\.0\.1|10\.0\.2\.2|0\.0\.0\.0|192\.168\.\d+\.\d+|"
                          r"[\w.-]*ngrok[\w.-]*|[\w.-]*\.local\b|staging[\w.-]*|dev[-.]api[\w.-]*|[\w.-]*\.test\b)", re.I)
TEST_CREDS = re.compile(r"(password|passwd|pwd)\s*[:=]\s*[\"'](test|1234|123456|password|admin|demo)[\"']", re.I)

OTA = {
    "react-native-code-push": "CodePush OTA updates",
    "expo-updates": "Expo OTA updates",
    "@capacitor/live-updates": "Capacitor live updates",
    "@capgo/capacitor-updater": "Capgo live updates",
    "hot-updater": "hot-updater OTA",
    "shorebird": "Shorebird code push (Flutter)",
    "@revopush": "Revopush OTA",
}
DYNAMIC_CODE = [
    (r"\beval\s*\(", "JavaScript eval()"),
    (r"new Function\s*\(", "JavaScript new Function()"),
    (r"evaluateScript\s*\(", "JavaScriptCore evaluateScript"),
    (r"\bdlopen\s*\(", "dlopen()"),
    (r"DexClassLoader|PathClassLoader", "Android dynamic class loading"),
    (r"Assembly\.Load\s*\(", "C# Assembly.Load"),
    (r"\bloadstring\s*\(|luaL_loadstring", "Lua loadstring"),
    (r"NSBundle\(path:|Bundle\(path:", "loading a bundle from a path"),
]
WEB_WRAPPER = [
    (r"WKWebView[\s\S]{0,400}load\(\s*URLRequest\(\s*url:\s*URL\(string:\s*\"https?://", "WKWebView loading a remote URL"),
    (r"<WebView[\s\S]{0,200}source=\{\{\s*uri:\s*['\"]https?://", "react-native-webview with a remote uri"),
    (r"WebView\([\s\S]{0,200}initialUrl:\s*['\"]https?://", "Flutter WebView with a remote initialUrl"),
    (r"loadUrl\(\s*\"https?://", "Android WebView.loadUrl remote"),
    (r"\"server\"\s*:\s*\{[^}]*\"url\"\s*:\s*\"https?://", "Capacitor server.url pointing at a live site"),
]
SCAFFOLDS = [r"\brork\b", r"a0\.dev", r"\bvibecode\b", r"createanything", r"bolt\.new", r"\blovable\b",
             r"replit", r"flutterflow", r"\bbubble\.io\b", r"\bglide\b", r"\badalo\b", r"\bthunkable\b"]

META_RULES = [
    (r"\b(beta|alpha|preview build|test version|demo version|trial version)\b", "2.2",
     "Beta / demo wording in the metadata", "Betas belong in TestFlight; ship the store build as the finished product."),
    (r"\b(android|google play|play store|samsung|huawei)\b", "2.3.10",
     "Another platform named in the metadata", "Remove references to other platforms from the listing."),
    (r"(\$\s?\d|\bfree\b|\bsale\b|\d+% off|\bdiscount\b)", "2.3.7",
     "Price or promotion language in the name/subtitle/keywords", "Keep pricing out of the name, subtitle and keywords."),
    (r"(lorem|placeholder|\bTODO\b|\bTBD\b|xxx)", "2.1 / 2.3",
     "Placeholder text in the metadata", "Replace every placeholder before submitting."),
]


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.endswith((".xcassets", ".framework"))]
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


def finding(sev, guideline, title, evidence, fix):
    return {"severity": sev, "guideline": guideline, "title": title, "evidence": evidence[:8],
            "more": max(0, len(evidence) - 8), "fix": fix}


def scan_project(root, exclude=()):
    placeholders, endpoints, creds, dynamic, wrapper, scaffold, ota = [], [], [], [], [], [], {}
    ats_open = []
    exclude = {os.path.abspath(e) for e in exclude if e}
    for path in walk(root):
        if os.path.abspath(path) in exclude:
            continue
        name = os.path.basename(path)
        ext = os.path.splitext(name)[1]
        if ext not in CODE_EXT and ext not in STRING_EXT and name not in CONFIG_NAMES:
            continue
        if name in ("package-lock.json", "yarn.lock", "Package.resolved") or name.endswith(".min.js"):
            continue
        text = read(path)
        if not text:
            continue
        r = os.path.relpath(path, root)
        is_code = ext in CODE_EXT
        for n, line in enumerate(text.splitlines(), 1):
            if len(line) > 2000:
                continue
            stripped = line.strip()
            is_comment = stripped.startswith(("//", "#", "*", "/*", "<!--"))
            if is_code and not is_comment:
                for _, body in STRING_LITERAL.findall(line):
                    if re.search(PLACEHOLDER, body, re.I):
                        placeholders.append(f"{r}:{n}: {body[:90]}")
                        break
            elif ext in STRING_EXT and re.search(PLACEHOLDER, line, re.I) and not is_comment:
                placeholders.append(f"{r}:{n}: {stripped[:90]}")
            if not is_comment and DEV_ENDPOINT.search(line):
                endpoints.append(f"{r}:{n}: {DEV_ENDPOINT.search(line).group(0)}")
            if TEST_CREDS.search(line):
                creds.append(f"{r}:{n}")
            if is_code and not is_comment:
                for pat, label in DYNAMIC_CODE:
                    if re.search(pat, line):
                        dynamic.append(f"{r}:{n}: {label}")
        if name in CONFIG_NAMES:
            for dep, label in OTA.items():
                if dep in text:
                    ota[label] = r
            for pat in SCAFFOLDS:
                m = re.search(pat, text, re.I)
                if m:
                    scaffold.append(f"{r}: '{m.group(0)}'")
        if is_code or name.startswith("capacitor.config"):
            for pat, label in WEB_WRAPPER:
                if re.search(pat, text):
                    wrapper.append(f"{r}: {label}")
        if name == "Info.plist" and re.search(r"<key>NSAllowsArbitraryLoads</key>\s*<true/>", text):
            ats_open.append(r)

    out = []
    if placeholders:
        out.append(finding("HIGH", "2.1", f"Placeholder text in user-facing strings ({len(placeholders)})", placeholders,
                           "Replace or remove each one; a reviewer who sees 'Coming soon' or lorem ipsum stops reviewing."))
    if endpoints:
        out.append(finding("HIGH", "2.1", f"Development or staging endpoints ({len(endpoints)})", endpoints,
                           "Point release builds at production; a reviewer's device cannot reach localhost or a staging host."))
    if creds:
        out.append(finding("MEDIUM", "2.1", "Hard-coded test credentials", creds,
                           "Remove them from the build; give App Review a working demo account in the review notes instead."))
    if ota:
        out.append(finding("MEDIUM", "2.5.2 / DPLA", "Over-the-air code updates",
                           [f"{label} ({where})" for label, where in ota.items()],
                           "Allowed for interpreted code only if updates do not change the app's primary purpose, add a store, "
                           "or bypass review of new features. Use OTA for fixes; ship features through review."))
    if dynamic:
        out.append(finding("MEDIUM", "2.5.2", f"Code that executes or loads code at runtime ({len(dynamic)})", dynamic,
                           "Confirm none of it runs code fetched from a server. If it does, that is a 2.5.2 rejection waiting to happen."))
    if wrapper:
        root_files = ("App.tsx", "App.jsx", "App.js", "index.tsx", "index.js", "_layout.tsx", "main.dart",
                      "ContentView.swift", "MainActivity.kt", "MainActivity.java", "capacitor.config")
        at_root = any(os.path.basename(w.split(":")[0]).startswith(root_files) for w in wrapper)
        title = ("The app may be a remote website in a web view" if at_root
                 else "Remote web content in a web view (not at the app's entry point)")
        out.append(finding("MEDIUM" if at_root else "LOW", "4.2 / 4.2.2", title, wrapper,
                           "If the main experience is your website, add native value (offline, device features, native navigation) "
                           "or the app is likely to be rejected for minimum functionality."))
    if scaffold:
        out.append(finding("LOW", "4.2.6 / 4.3", "App-generation platform scaffold detected", scaffold,
                           "Not a violation by itself. Make sure nothing of the generator's default (name, icon, sample screens, "
                           "sample data) is left, and that the app does something its siblings from the same tool do not."))
    if ats_open:
        out.append(finding("LOW", "ATS", "App Transport Security disabled globally", ats_open,
                           "Use per-domain exceptions; a blanket NSAllowsArbitraryLoads needs a justification in review."))
    return out


def scan_listing(lst):
    out = []
    head = " ".join([lst.get("name") or "", lst.get("subtitle") or "", lst.get("keywords") or ""])
    full = head + " " + (lst.get("description") or "") + " " + (lst.get("whats_new") or "") + " " + \
        " ".join(s.get("caption", "") for s in lst.get("screenshots", []) if isinstance(s, dict))
    for pat, guideline, title, fix in META_RULES:
        hay = head if guideline == "2.3.7" else full
        hits = sorted({m.group(0) for m in re.finditer(pat, hay, re.I)})
        if hits:
            sev = "HIGH" if guideline.startswith("2.1") else "MEDIUM"
            out.append(finding(sev, guideline, title, [f"found: {', '.join(hits)}"], fix))
    url = lst.get("privacy_policy_url") or ""
    if re.search(r"example\.(com|org|net|invalid)|localhost|\.test\b|placeholder", url, re.I):
        out.append(finding("HIGH", "5.1.1(i) / 2.1", "Privacy policy URL is a placeholder", [url],
                           "Use the real, reachable policy URL."))
    desc = (lst.get("description") or "")
    claim = re.search(r"(hundreds|thousands|\d{3,}\+?) (of )?(levels|puzzles|stages|challenges)", desc + " " +
                      " ".join(s.get("caption", "") for s in lst.get("screenshots", []) if isinstance(s, dict)), re.I)
    if claim and (lst.get("content") or {}).get("generated"):
        out.append(finding("MEDIUM", "2.3.1 / 4.2", "Content-count claim on generated content", [f"'{claim.group(0)}'"],
                           "Claim only what is authored and distinct, or drop the count; the reviewer will play the first few."))
    filler = sorted({m.group(0) for m in re.finditer(r"download (it )?now|easy to learn,? hard to master|the most (addictive|satisfying)|what are you waiting for", desc, re.I)})
    if filler:
        out.append(finding("LOW", "4.3(b) / 2.3", "Stock store-copy phrases", [", ".join(filler)],
                           "Replace with sentences only this app could say."))
    if not lst.get("privacy_policy_url"):
        out.append(finding("HIGH", "5.1.1(i)", "No privacy policy URL in the listing", ["privacy_policy_url missing"],
                           "Add a reachable privacy policy URL in App Store Connect."))
    if lst.get("requires_login") and not lst.get("demo_account"):
        out.append(finding("HIGH", "2.1", "Login required and no demo account for App Review", ["requires_login: true"],
                           "Give a working demo account (or a demo mode) in the App Review notes."))
    for s in lst.get("screenshots", []) or []:
        if isinstance(s, dict) and s.get("shows_real_ui") is False:
            out.append(finding("MEDIUM", "2.3.3", "Screenshot does not show the app in use",
                               [f"'{s.get('caption', '')}'"], "Screenshots must show the app in use, not only title art or a splash."))
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--project", help="project root")
    p.add_argument("--listing", help="listing JSON (references/listing-format.md)")
    p.add_argument("--format", choices=["json", "md"], default="json")
    args = p.parse_args()
    if not args.project and not args.listing:
        p.error("give --project, --listing or both")

    findings = []
    if args.project:
        findings += scan_project(args.project, exclude=[args.listing])
    if args.listing:
        with open(args.listing, encoding="utf-8") as fh:
            findings += scan_listing(json.load(fh))
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    findings.sort(key=lambda f: order[f["severity"]])
    result = {"tool": "completeness_scan", "project": args.project, "listing": args.listing, "findings": findings,
              "counts": {s: sum(1 for f in findings if f["severity"] == s) for s in order},
              "note": "Guidance based on public App Review Guidelines; Apple's decisions are their own."}
    if args.format == "md":
        c = result["counts"]
        lines = ["# Completeness and risk scan (2.1 · 2.3 · 2.5.2 · 4.2)", "",
                 f"Findings: {c['HIGH']} high · {c['MEDIUM']} medium · {c['LOW']} low", ""]
        for f in findings:
            lines += [f"### [{f['severity']}] {f['title']} ({f['guideline']})", ""]
            lines += [f"- {e}" for e in f["evidence"]]
            if f["more"]:
                lines.append(f"- …and {f['more']} more")
            lines += [f"- **Fix:** {f['fix']}", ""]
        lines.append("_" + result["note"] + "_")
        print("\n".join(lines))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
