# Language: iOS (Swift)

> **AI INSTRUCTIONS:** Use this file when TARGET_LANGUAGE = `ios`. iOS is **Cloud-only** in v1 — the AppToApp transport is Android-only and PADController is not available on iOS.

## Distribution

- **Artifact:** `PineBillingSdk.xcframework` (universal: arm64 device, arm64 simulator, x86_64 simulator)
- **Module name:** `PineBillingSdk`
- **Download:** call `get_sdk(artifact_key="ios-xcframework")`

## Environment requirements

| Item | Required |
|---|---|
| Xcode | 15+ |
| Swift | 5.9+ |
| Deployment target | iOS 14+ |
| ATS / TLS | unchanged defaults; SDK uses HTTPS only |

## Setup — Swift Package Manager

```swift
// Package.swift
.package(url: "file:///path/to/PineBillingSdk.xcframework.zip", from: "<version>")
```

Or via Xcode → Add Package → local path.

## Setup — CocoaPods

```ruby
pod 'PineBillingSdk', :path => './third_party/PineBillingSdk'
```

## Info.plist

No extra entries are required. Cloud HTTPS works out of the box; do not add `NSAllowsArbitraryLoads`.

## SDK construction

```swift
import PineBillingSdk

let config = SdkConfig(
    defaultTimeoutMs: 60_000,
    logLevel: .info,
    transport: .cloud,
    appToApp: nil,
    applicationId: nil,
    cloud: CloudConfig(
        type: .ism,
        baseUrl: "https://api.pinelabs.example",
        connectTimeoutMs: 5_000,
        readTimeoutMs: 245_000),
    padController: nil)

let sdk = try PineBillingSdk(config: config, appToAppBridge: nil, platformBridge: nil)
```

## Threading

- All listener callbacks fire on a Rust-internal thread (NOT main).
- Marshal to the main thread before UIKit/SwiftUI updates:

```swift
func onSuccess(result: TransactionResult) {
    DispatchQueue.main.async { /* update UI */ }
}
```

## Code-generation directives

- Wrap every throwing call in `do/try/catch`. Match against `SdkError` cases.
- Pass `CLOUD_SECURITY_TOKEN` from Keychain — never embed.
- For Combine / async-await wrappers around listener APIs, expose a single `AsyncThrowingStream<TransactionEvent, Error>` per call.

## Next docs

- Concepts: `lifecycle`, `transports`, `error-handling`, `eventid-and-reconciliation`.
- APIs: `constructor`, `do_transaction`, `cancel`, `check_status`, `upload_imei_list`.
- Models: `SdkConfig`, `CloudConfig`, `CloudIdentity`, `CloudTransactionOptions`.
