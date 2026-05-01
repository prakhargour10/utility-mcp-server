# Concept: distribution

> **AI INSTRUCTIONS:** Use this file when the user asks "where do I get the SDK?" or "how do I add it to my build?" Always tell them honestly that there is no public package registry yet — direct file drop only.

## How the SDK is delivered today

The Pine Billing SDK is **not** published to Maven Central, CocoaPods,
PyPI, or npm in `0.5.0-preview.2`. Distribution is **direct file drop**:

| Artifact | Filename | Where it goes |
|---|---|---|
| Android | `pine-billing-sdk-0.5.0-preview.2.aar` (delivered inside `android-kotlin-0.5.0-preview.2.zip`) | `app/libs/` |
| JVM     | `pine-billing-sdk-0.5.0-preview.2.jar` | local `lib/` directory |

> **Android wrapper-ZIP note:** the MCP `get_sdk(artifact_key="android-aar")`
> call resolves to a wrapper ZIP, not the bare AAR. See
> `languages/android/distribution.md` for the layout.

## Version pinning

* Pin to **the exact version**. Pre-1.0 minor bumps may break source
  compatibility.
* Record the SHA-256 of the artifact in your build; a change of
  artifact contents under the same version is a release-engineering
  bug.

## License

Proprietary — Pinelabs internal-use license. Do not redistribute. The
artifact's `THIRD_PARTY_NOTICES.md` lists permissively-licensed
transitive native-side dependencies.

## Roadmap (not in `0.5.0-preview.2`)

| Channel | Target binding | ETA |
|---|---|---|
| Maven Central (`com.pinelabs:pine-billing-sdk`) | android, jvm | TBD |
| CocoaPods / SwiftPM | ios | TBD |
| PyPI (`pine-billing-sdk`) | python | TBD |
| npm (`@pinelabs/pine-billing-sdk`) | nodejs | TBD |
| Tar/zip releases | c / c++ | TBD |

## Next docs

`versioning-and-support`, per-binding `distribution.md`.
