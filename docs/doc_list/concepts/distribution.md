# Concept: distribution

> **AI INSTRUCTIONS:** Use this file when the user asks "where do I get the SDK?" or "how do I add it to my build?" Always tell them honestly that there is no public package registry yet — direct file drop only.

## How the SDK is delivered today

The Pine Billing SDK is **not** published to Maven Central, CocoaPods,
PyPI, or npm in `0.5.0-preview.2`. Distribution is **direct file drop**:

| Artifact | Filename | Where it goes |
|---|---|---|
| Android | `pine-billing-sdk-0.5.0-preview.2.aar` | `app/libs/` (or any local Maven repo) |
| JVM     | `pine-billing-sdk-0.5.0-preview.2.jar` | local `lib/` directory or local Maven repo |

Pinelabs delivers the artifact directly to the merchant (typically via
a private channel — email, internal portal, or a shared private Maven
repository). Treat the file as proprietary; do not redistribute.

## Version pinning

* Pin to **the exact version**. Pre-1.0 minor bumps may break source
  compatibility.
* Record the SHA-256 of the artifact in your build (Gradle
  `dependencyVerification` or Maven `verify-checksums`); a change of
  artifact contents under the same version is a release-engineering bug
  on Pinelabs' side and must be flagged.

## License

Proprietary — Pinelabs internal-use license. Do not embed in
open-source projects without prior written approval. Bundled native
libraries inherit the same license; the few permissively-licensed
transitive dependencies are listed in the artifact's
`META-INF/LICENSES/` directory.

## Roadmap (not in `0.5.0-preview.2`)

| Channel | Target binding | ETA |
|---|---|---|
| Maven Central (`com.pinelabs:pine-billing-sdk`) | android, jvm | TBD |
| CocoaPods / SwiftPM | ios | TBD |
| PyPI (`pine-billing-sdk`) | python | TBD |
| npm (`@pinelabs/pine-billing-sdk`) | nodejs | TBD |
| Tar/zip releases | c / c++ | TBD |

When these channels open, this document and the per-binding
`distribution.md` files will be updated. Until then, do not invent
coordinates.

## Next docs

`versioning-and-support`, per-binding `distribution.md`.
