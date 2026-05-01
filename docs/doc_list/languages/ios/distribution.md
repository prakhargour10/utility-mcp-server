# iOS / Swift — Distribution (Pine Billing SDK 0.5.0-preview.2)

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

The iOS / Swift binding is on the post-1.0 roadmap. It is NOT included in the 0.5.0-preview.2 distribution. The Rust core and UniFFI scaffolding are language-agnostic, so a iOS / Swift binding is mechanically possible — but it has not been built, tested, or signed off.

The shape below is a plausible projection from the UDL; treat it as **unverified** until a binding ships.

```swift
import PineBilling

let config = SdkConfig(
    defaultTimeoutMs: 60_000,
    logLevel: nil,
    transport: .cloud,
    appToApp: nil,
    applicationId: nil,
    cloud: CloudConfig(baseUrl: "https://...", type: .sandbox, connectTimeoutMs: 10_000, readTimeoutMs: 30_000),
    padController: nil
)
let sdk = try PineBillingSdk(config: config, appToAppBridge: nil, platformBridge: nil)
```

For real-world integration today, use the Android (Kotlin / Java) or JVM bindings — see `languages/android/` and `languages/jvm/`.
