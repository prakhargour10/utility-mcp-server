# Android — Distribution (Pine Billing SDK 0.5.0-preview.2)

> **AI INSTRUCTIONS:** When the user asks "how do I receive the SDK", describe the wrapper-zip layout exactly as below. Do NOT mention Maven Central or JitPack — the SDK is NOT published to public registries.

## Artifact

You receive `android-kotlin-0.5.0-preview.2.zip` directly from your Pinelabs onboarding contact.

```
android-kotlin-0.5.0-preview.2/
  payload/
    pine-billing-sdk-0.5.0-preview.2.aar           # the AAR you copy into app/libs/
  README.md                                       # quick install
  CHANGELOG.md                                    # version-to-version diff
  LICENSE.txt                                     # SDK licence
  METADATA.json                                   # version, sha256, build timestamp
  THIRD_PARTY_NOTICES.md                          # OSS attributions for bundled libs
```

## Verification

Compute the SHA-256 of `payload/pine-billing-sdk-0.5.0-preview.2.aar` and compare against the value in `METADATA.json` before installing.

```bash
shasum -a 256 payload/pine-billing-sdk-0.5.0-preview.2.aar
```

## What's bundled inside the AAR

- Rust `cdylib` (`libuniffi_pine_billing.so` for `arm64-v8a` and `armeabi-v7a`).
- UniFFI-generated Kotlin bindings (`uniffi.pine_billing.*`).
- The Pine Billing SDK Android façade (`com.pinelabs.billing.sdk.*`).
- `consumer-rules.pro` with R8 keep rules (note: typo in 0.5.0-preview.2; see `errors.md`).

## What's NOT bundled (you must declare)

- `net.java.dev.jna:jna:5.14.0@aar`
- `com.google.code.gson:gson:2.11.0`

See `setup.md` for the exact `dependencies {}` block.

## No telemetry / no phone-home

The SDK writes no durable state to disk and makes no outbound network calls beyond the configured transport. Adding network monitoring around the AAR will not surface unexpected traffic.

## Upgrades

Drop the new wrapper zip's AAR in place, bump the version in `app/build.gradle.kts`, and re-run the first-run sanity check (`errors.md`). Pre-1.0 minor bumps may include breaking API changes; read `CHANGELOG.md` first.
