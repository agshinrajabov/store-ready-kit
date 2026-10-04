# Privacy consistency — 5.1, 5.1.2, 4.8 and the privacy manifest

Guidelines revision: **8 June 2026** · last checked: **2026-10-04** · numbers: 5.1.1(i), 5.1.1(ii), 5.1.1(v), 5.1.2, 4.8

Four things must tell the same story: the **code**, the **declarations** (Info.plist / AndroidManifest / Expo
config), the **purpose strings**, and the **privacy policy** — plus the App Privacy answers in App Store Connect,
which the audit cannot read and the developer must compare by hand.

## The rules in short

- **5.1.1(i) Privacy policy.** Every app links one, in App Store Connect *and* inside the app. It says what is
  collected, how, and for what; who it is shared with and that they protect it equally; how long it is kept and
  how to delete it; how to withdraw consent.
- **5.1.1(ii) Permission.** Ask for consent for data collection; purpose strings must explain the use clearly.
  Paid features cannot depend on granting access to unrelated data.
- **5.1.1(v) Account sign-in.** Don't force a login without account-based features. **If the app lets people
  create an account, it must let them delete it inside the app.**
- **5.1.2 Data use and sharing.** Tracking needs App Tracking Transparency permission first; no fingerprinting.
- **4.8 Login services.** If a third-party or social login sets up the main account, also offer an equivalent
  login that limits data to name and email, allows a private email, and does not track (Sign in with Apple meets
  this).
- **Privacy manifest.** Apps and SDKs that call "required-reason" APIs (UserDefaults, file timestamps, system boot
  time, disk space, active keyboards) declare an approved reason in `PrivacyInfo.xcprivacy`; uploads without it get
  ITMS-91053 warnings or rejections. Cross-platform storage (AsyncStorage, shared_preferences, PlayerPrefs) uses
  UserDefaults underneath.

## Purpose strings that pass

Formula: **what the user does + what they get**. One sentence, the app's own words.

| Weak | Strong |
|---|---|
| "This app needs camera access." | "Photograph a receipt to add it to this month's expenses." |
| "Location is required for a better experience." | "Show climbing gyms within 20 km and sort them by distance." |
| "Allow $(PRODUCT_NAME) to access your photos" (an Expo default) | "Pick a photo of your plant so we can identify it." |

## What `privacy_check.py` maps

Camera, microphone, photos, location, contacts, calendars, Bluetooth, motion, health, tracking/IDFA, Face ID,
speech, local network: each with its iOS purpose-string keys, code and library patterns (native, Expo/React
Native, Flutter, Unity), Android permissions, and the words a policy would use for that data. Also: ad and
attribution SDKs without ATT, required-reason APIs without a manifest, sign-up without deletion, social login
without an equivalent option.

## What the developer still checks by hand

- App Privacy ("nutrition label") answers match what SDKs collect — analytics, crash reporting and ads SDKs
  collect even when the app's own code does not.
- Third-party SDKs ship their own privacy manifests (and signatures, for the listed common SDKs).
- Kids Category or apps aimed at children: stricter rules (1.3, 5.1.4) — out of scope for this audit; flag it.
- Health, financial, or location-based services with legal obligations (5.1.1(ix)) — flag for specialist review.
