# Language: JVM — Distribution

> **AI INSTRUCTIONS:** The JAR is delivered by direct file drop. Do NOT generate `mavenCentral()` snippets in this release.

## Where to obtain the JAR

Pinelabs ships the artifact directly. Filename:

```
pine-billing-sdk-0.5.0-preview.2.jar
```

There is **no** publicly reachable Maven coordinate yet.

## License

Proprietary — Pinelabs internal-use license. Do not redistribute.
The JAR's `META-INF/LICENSES/` directory lists transitive native-side
permissive licenses.

## Verifying the artifact

```bash
sha256sum lib/pine-billing-sdk-0.5.0-preview.2.jar
# Compare against the value Pinelabs published.
```

## Version pinning

* Pin to **the exact version** (`0.5.0-preview.2`).
* Pre-1.0 minor bumps may break source compatibility.
* Do NOT use floating constraints.

## What is bundled inside the JAR

* `uniffi/pine_billing/*.class` — Kotlin/Java surface.
* `META-INF/jniLibs/<triple>/libuniffi_pine_billing.{so,dylib,dll}` —
  native libraries for each shipping triple. JNA extracts the
  matching one to a temp directory at runtime.
* `META-INF/LICENSES/` — license bundle.

## Roadmap

| Channel | Coordinate (planned) | Status |
|---|---|---|
| Maven Central | `com.pinelabs:pine-billing-sdk:<ver>` | Not in `0.5.0-preview.2`. ETA TBD. |

## Next docs

`concepts/distribution`, `concepts/versioning-and-support`,
`jvm/setup`.
