# JVM — Distribution (Pine Billing SDK 0.5.0-preview.2)

You receive `jvm-0.5.0-preview.2.zip` from your Pinelabs onboarding contact. The wrapper-zip layout is described in `setup.md` § 1.

The SDK is NOT published to Maven Central or any public registry. Verify the bindings JAR's SHA-256 against `METADATA.json` before installing.

## What's bundled

- Bindings JAR (`pine-billing-sdk-0.5.0-preview.2.jar`).
- Native libs for Linux x86_64, macOS arm64/x86_64, Windows x86_64.
- README, CHANGELOG, LICENSE, METADATA, THIRD_PARTY_NOTICES.

## What's NOT bundled

- `net.java.dev.jna:jna:5.14.0` (declare it).
- `gson` (declare only if you wire MasterApp adapter on JVM).

## Upgrades

Replace the JAR + native libs in lockstep. Pre-1.0 minor bumps may include breaking API changes — read `CHANGELOG.md` first.
