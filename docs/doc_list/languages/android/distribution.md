# Language: Android — Distribution

> **AI INSTRUCTIONS:** When the user asks "where do I download the AAR?", reply with the truth: there is no public Maven coordinate yet. Direct file drop only.

## Where to obtain the AAR

The AAR is delivered directly by Pinelabs onboarding. Typical channels:

* Pinelabs partner portal,
* email from a Pinelabs solutions engineer,
* a private S3 / Artifactory bucket your contract entitles you to.

Filename for this release:

```
pine-billing-sdk-0.5.0-preview.2.aar
```

There is **no** publicly reachable Maven coordinate yet — do not
generate snippets like `implementation("com.pinelabs:pine-billing-sdk:…")`
in this release.

## License

Proprietary — Pinelabs internal-use license. See the `LICENSE` file
that accompanies the artifact. Do not redistribute.

## Verifying the artifact

Pinelabs publishes a SHA-256 alongside the AAR. Pin it in your build:

```kotlin
// settings.gradle.kts
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
}
```

```bash
# CI gate
sha256sum app/libs/pine-billing-sdk-0.5.0-preview.2.aar
# Compare against the value Pinelabs published.
```

## Version pinning

* Pin to **the exact version** (`0.5.0-preview.2`).
* Pre-1.0 minor bumps may break source compatibility — re-read
  `concepts/versioning-and-support.md` before upgrading.
* Do NOT use floating constraints like `+`, `[…,…)`, or `latest.release`.

## Roadmap

| Channel | Coordinate (planned) | Status |
|---|---|---|
| Maven Central | `com.pinelabs:pine-billing-sdk:<ver>` | Not in `0.5.0-preview.2`. ETA TBD. |
| Pinelabs private Maven | (varies by contract) | Talk to your account team. |

## Next docs

`concepts/distribution`, `concepts/versioning-and-support`,
`android/setup`.
