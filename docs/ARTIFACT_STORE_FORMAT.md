# Pine Billing SDK — Artifact Store Format

> **Audience:** Pinelabs MCP / release-engineering team.
> **Goal:** every distributable SDK is a single self-describing `.zip` on the
> Pinelabs artifact server, indexed by a flat manifest. Migrating later
> (S3 → CDN → on-prem → another vendor) is just `aws s3 sync` /
> `rsync` — nothing in the format is host-specific.
>
> The `get_sdk` MCP tool resolves user requests against the manifest defined
> here. Spec is consumed by the release pipeline (write side) and by the
> `get_sdk` server (read side). Pin the spec version in both.

---

## 1. Top-level layout on the artifact server

```
artifacts.pinelabs.com/
└── pine-billing-sdk/
    ├── manifest.json                          ← single source of truth
    ├── channels/
    │   ├── stable.json                        ← {"version":"0.1.0"}
    │   ├── beta.json                          ← {"version":"0.2.0-beta.3"}
    │   └── nightly.json
    └── releases/
        └── 0.1.0/
            ├── android-kotlin-0.1.0.zip
            ├── ios-swift-0.1.0.zip
            ├── python-cpython311-linux-x86_64-0.1.0.zip
            ├── python-cpython311-macos-arm64-0.1.0.zip
            ├── nodejs-linux-x86_64-0.1.0.zip
            ├── nodejs-macos-arm64-0.1.0.zip
            ├── nodejs-windows-x86_64-0.1.0.zip
            ├── c-linux-x86_64-0.1.0.zip
            ├── c-linux-aarch64-0.1.0.zip
            ├── c-macos-universal-0.1.0.zip
            └── c-windows-x86_64-0.1.0.zip
```

**Rules**

- **One zip per artifact_key** — never multi-binding zips. Keeps the
  resolver math trivial.
- **Releases are immutable.** A `0.1.0` zip is uploaded once and never
  overwritten. If a build is bad, cut `0.1.0.1` and update
  `channels/stable.json`.
- **Channels are pointers**, not directories — flipping
  `channels/stable.json` is the only way to promote a release.
- **No integrity sidecars in v1.** No `.sha256` files, no signatures.
  Bytes are served exclusively over HTTPS from
  `artifacts.pinelabs.com` via short-TTL signed URLs minted by the
  `get_sdk` MCP tool. See §11 for when to revisit.

---

## 2. artifact_key naming convention

```
<binding>[-<lang-or-runtime>][-<os>][-<arch>][-<extra>]
```

The on-disk filename is `<artifact_key>-<version>.zip`.

| binding | lang/runtime | os                    | arch                | example artifact_key                                |
|---------|--------------|-----------------------|---------------------|-----------------------------------------------------|
| android | kotlin       | (implicit: android)   | (multi-ABI inside)  | `android-kotlin`                                    |
| ios     | swift        | (implicit: apple)     | universal           | `ios-swift`                                         |
| python  | cpython311   | linux                 | x86_64              | `python-cpython311-linux-x86_64`                    |
| python  | cpython311   | macos                 | arm64               | `python-cpython311-macos-arm64`                     |
| nodejs  | (implicit)   | linux                 | x86_64              | `nodejs-linux-x86_64`                               |
| c       | (implicit)   | linux                 | aarch64             | `c-linux-aarch64`                                   |
| jvm     | java         | windows               | x86_64              | `jvm-java-windows-x86_64`  *(future / non-v1)*      |

`artifact_key` MUST match `^[a-z0-9][a-z0-9-]*[a-z0-9]$`. No uppercase,
no underscores, no spaces. Versions are SemVer 2.0.0.

---

## 3. Inside every zip — mandatory layout

```
android-kotlin-0.1.0.zip
├── METADATA.json                  ← machine-readable, single source of truth for THIS artifact
├── README.md                      ← human-readable install steps (mirrors get_sdk install.snippet)
├── LICENSE.txt
├── CHANGELOG.md
└── payload/                       ← THE ACTUAL SDK FILES (binding-shaped)
    └── …
```

**Hard rules**

- `METADATA.json` and `payload/` are **mandatory**. Everything else is
  recommended.
- Tools and humans only ever look at `payload/` for code. The
  `METADATA.json` at the root means a `get_sdk` reader can read just
  the central directory + a single file via HTTP `Range` and resolve
  everything without downloading the whole artifact.
- Do NOT put loose files at the zip root other than the five names
  above. Future format additions live under new top-level dirs (e.g.
  `examples/`, `attestations/`, `checksums/`, `signatures/` — see §11).

---

## 4. `METADATA.json` schema (inside every zip)

```jsonc
{
  "schema_version": "1.0",
  "sdk": "pine-billing-sdk",
  "version": "0.1.0",
  "artifact_key": "android-kotlin",
  "filename": "android-kotlin-0.1.0.zip",

  "binding": "android",
  "languages": ["Kotlin", "Java"],
  "target": {
    "os": "android",
    "min_os": "Android API 24",
    "arch": ["arm64-v8a", "armeabi-v7a", "x86_64", "x86"]
  },

  "payload": {
    "entrypoint": "payload/pine-billing-sdk-0.1.0.aar",
    "kind": "aar",
    "size_bytes": 7340032
  },

  "consume_as": "local_gradle",
  "install_snippet": "repositories { flatDir { dirs(\"libs\") } }\ndependencies { implementation(files(\"libs/pine-billing-sdk-0.1.0.aar\")) }",

  "build_info": {
    "rust_version": "1.75",
    "uniffi_version": "0.27.0",
    "git_commit": "<sha>",
    "built_at": "2026-04-30T10:00:00Z",
    "reproducible": true
  },

  "compat": {
    "supported_transports": ["AppToApp", "Cloud"],
    "min_sdk_protocol": "1.0"
  },

  "do_not_publish": "Distribute via Pinelabs artifact server only. Do not re-host on public/shared registries."
}
```

`payload.kind` enum:

```
"aar" | "xcframework" | "wheel" | "node-tarball" | "static-lib" | "shared-lib" | "jar"
```

`consume_as` enum:

```
"raw_file" | "local_gradle" | "local_spm" | "local_pip" | "local_npm" | "cmake" | "classpath_jar"
```

---

## 5. Per-binding `payload/` shapes

### android-kotlin
```
payload/
├── pine-billing-sdk-0.1.0.aar
└── sources/
    └── pine-billing-sdk-0.1.0-sources.jar     ← optional, for IDE jump-to-definition
```

### ios-swift
```
payload/
├── PineBillingSdk.xcframework/                ← directory (preserve symlinks; zip with `-y`)
└── PineBillingSdk-doccarchive.zip             ← optional
```
> ⚠️ Apple `.xcframework` bundles contain symlinks. Build the outer
> zip with `zip -y` to preserve them and document this in the team's
> release runbook.

### python (one zip per OS × arch × py-abi)
```
payload/
└── pine_billing_sdk-0.1.0-cp311-manylinux2014_x86_64.whl
```

### nodejs (one zip per OS × arch)
```
payload/
└── pinelabs-pine-billing-sdk-0.1.0.tgz        ← `npm pack` output
```

### c (one zip per OS × arch)
```
payload/
├── include/
│   └── pine_billing.h
├── lib/
│   ├── libpine_billing_sdk.so                 ← .dylib on macOS, .dll+.lib on Windows
│   └── libpine_billing_sdk.a
├── cmake/
│   └── PineBillingSdkConfig.cmake
└── pkgconfig/
    └── pine_billing_sdk.pc
```

### jvm-java (desktop JVM, future / non-v1)
```
payload/
├── pine-billing-sdk-0.1.0.jar                 ← UniFFI-generated Java bindings
├── lib/
│   └── pine_billing_sdk.dll                   ← native JNI lib (per OS × arch)
└── sources/
    └── pine-billing-sdk-0.1.0-sources.jar     ← optional
```

---

## 6. `manifest.json` schema (top-level index)

```jsonc
{
  "schema_version": "1.0",
  "sdk": "pine-billing-sdk",
  "generated_at": "2026-04-30T10:00:00Z",
  "channels": {
    "stable":  { "version": "0.1.0" },
    "beta":    { "version": "0.2.0-beta.3" },
    "nightly": { "version": "0.3.0-nightly.20260430" }
  },
  "releases": {
    "0.1.0": {
      "released_at": "2026-04-30T10:00:00Z",
      "yanked": false,
      "yanked_reason": null,
      "artifacts": [
        {
          "artifact_key": "android-kotlin",
          "filename": "android-kotlin-0.1.0.zip",
          "path": "releases/0.1.0/android-kotlin-0.1.0.zip",
          "size_bytes": 7340032,
          "binding": "android",
          "languages": ["Kotlin", "Java"],
          "target": { "os": "android", "min_os": "Android API 24",
                      "arch": ["arm64-v8a","armeabi-v7a","x86_64","x86"] },
          "consume_as": "local_gradle"
        },
        {
          "artifact_key": "python-cpython311-linux-x86_64",
          "filename": "python-cpython311-linux-x86_64-0.1.0.zip",
          "path": "releases/0.1.0/python-cpython311-linux-x86_64-0.1.0.zip",
          "size_bytes": 4194304,
          "binding": "python",
          "languages": ["Python"],
          "target": { "os": "linux", "arch": ["x86_64"], "py_abi": "cp311" },
          "consume_as": "local_pip"
        }
        /* … one entry per (OS × arch × abi) */
      ]
    }
  }
}
```

`get_sdk` resolves a request in three deterministic steps:

1. Resolve `version` (from `channel` or explicit). Reject if
   `releases[v].yanked == true`.
2. Filter `releases[v].artifacts` by `binding` (from
   `language_aliases`) + `target.os` + `target.arch` + `py_abi` /
   other extras.
3. Score remaining rows; tie-break on `arch == "universal"` and
   most-recent `built_at`. Winner is returned, runners-up populate
   the `alternatives` array.

---

## 7. Storage backend (host-agnostic)

Plain object storage with HTTP GET. No registry, no DB-backed package
server.

| Property | Choice |
|---|---|
| Authoritative store | S3-compatible bucket (S3, GCS, MinIO, on-prem) |
| Edge | Any HTTP CDN (CloudFront, Fastly, on-prem nginx) — caching only, no transformations |
| Access control | Signed URLs (HMAC, ≤ 15 min TTL); origin denies unsigned GETs |
| Auth on `get_sdk` | Bearer token issued at merchant onboarding; tool exchanges it for a signed URL per call |
| Migration | `aws s3 sync s3://old s3://new` (or `rclone`); flip CDN origin; manifest stays valid because all paths are relative |
| Yanking | Set `releases[v].yanked = true` in `manifest.json` and re-publish. Do NOT delete the zip — historical version references must remain resolvable. |

---

## 8. Release pipeline checklist

1. Build → produce binding-shaped `payload/`.
2. Generate `METADATA.json` from build inputs.
3. Zip the staging dir
   (`zip -y -r android-kotlin-0.1.0.zip METADATA.json README.md … payload/`).
4. Upload the zip to `releases/<version>/`.
5. Once **all** artifacts for the release are uploaded, regenerate
   `manifest.json` and upload it atomically (write to
   `manifest.json.new`, then rename).
6. Promote: write `channels/stable.json` last. The promotion is the
   only mutable operation in the whole pipeline.

> **Atomicity rule:** never update `manifest.json` mid-upload. The
> manifest must always reference artifacts that exist on disk.

---

## 9. Why zip (not tar.gz / aar / whl directly)

- **Universally readable** on Windows, macOS, Linux, Android Studio,
  Xcode without extra tooling.
- **Random access** — central directory at end of file lets the
  resolver fetch only `METADATA.json` via a single HTTP `Range`
  request without downloading the whole artifact.
- **Self-describing** — one `.zip` carries binary + metadata. Migration
  = move bytes.
- **Wrapping `.aar` / `.whl` / `.jar` inside a zip is fine** — those
  are already zips; nesting is cheap (no recompression). The inner
  file is the entrypoint named in `METADATA.json.payload.entrypoint`.

---

## 10. Versioning the format itself

- Bump `METADATA.json.schema_version` and `manifest.json.schema_version`
  independently.
- `get_sdk` MUST refuse to serve a manifest whose `schema_version.major`
  it doesn't understand (return a structured error telling the LLM to
  upgrade the MCP tool).
- Old zips stay readable forever — schema bumps are additive only,
  never rename or remove fields.

---

## 11. Why no integrity files in v1

The v1 distribution model relies on three things already in place:

1. **HTTPS to `artifacts.pinelabs.com` only.** TLS certificate
   validation prevents in-flight tampering and MITM.
2. **Per-call signed download URLs with ≤ 15 min TTL** issued by the
   `get_sdk` MCP tool only to authenticated merchants. The artifact
   store is not a public registry.
3. **The artifact bucket itself is access-controlled** with audit
   logging. Only the release pipeline writes; nothing else does.

Adding `.sha256` sidecars or sigstore bundles would only matter if an
attacker compromised the artifact bucket *and* tampered with a
specific zip. That threat is real but narrow and currently
unregulated. The cost (cosign / Fulcio key custody, rotation,
revocation, and a verification step the consumer LLM must invoke) is
not justified at v1 scale.

### Add integrity sidecars later if any of these become true

- The SDK ships to **third-party developers** outside merchant
  onboarding.
- **Regulatory pressure** (RBI, PCI-DSS, SBOM mandates) requires it.
- A **mirror or partner CDN** outside direct Pinelabs operational
  control is added to the distribution path.
- A **post-mortem** traces an incident back to artifact-bucket
  tampering.

The format absorbs them additively when that day comes:

- Add `<artifact>.zip.sha256` sidecars in the release directory.
- Add `sha256` and (later) `sigstore_bundle_path` fields per artifact
  in `manifest.json`.
- Add `checksums/SHA256SUMS` (and later `signatures/SHA256SUMS.sigstore`)
  inside each zip.
- Add `payload.sha256` to `METADATA.json`.

No existing fields are renamed — readers that ignore unknown fields
keep working through the upgrade.

## 12. Reference samples

Two worked examples sit alongside this document under
`sample-artifacts/`, packaged from the real `0.5.0-preview.2` handoff
artifacts (Android AAR + JVM fat JAR):

| File | Purpose |
|---|---|
| `sample-artifacts/android-kotlin-0.5.0-preview.2.zip` | Real Android binding (Kotlin + Java consumers). Wraps `pine-billing-sdk-0.5.0-preview.2.aar` as `payload/`. |
| `sample-artifacts/jvm-java-0.5.0-preview.2.zip` | Desktop JVM binding. **Universal fat JAR** with bundled native slices for `windows-x86_64`, `macos-aarch64`, `macos-x86_64`, `linux-x86_64`. JNA selects the right slice at runtime. |
| `sample-artifacts/manifest.json` | Real top-level manifest covering both zips. |

> **Why one universal JVM zip instead of per-OS zips?** The handoff JAR
> already embeds all 4 native slices and JNA picks the right one based
> on `os.name` + `os.arch` at load time. Splitting it would either
> require rebuilding the JAR per OS or shipping the same fat JAR under
> 4 different artifact_keys — both are misleading. A single
> `jvm-java` artifact_key is the honest representation.
