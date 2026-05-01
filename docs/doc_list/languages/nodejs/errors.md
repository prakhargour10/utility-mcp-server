# Node.js — Errors (Pine Billing SDK 0.5.0-preview.2)

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

The Node.js binding is on the post-1.0 roadmap. It is NOT included in the 0.5.0-preview.2 distribution. The Rust core and UniFFI scaffolding are language-agnostic, so a Node.js binding is mechanically possible — but it has not been built, tested, or signed off.

The shape below is a plausible projection from the UDL; treat it as **unverified** until a binding ships.

```javascript
const { PineBillingSdk, TransportType, CloudType } = require("pine-billing");

const config = {
    defaultTimeoutMs: 60_000,
    logLevel: null,
    transport: TransportType.CLOUD,
    appToApp: null,
    applicationId: null,
    cloud: {
        baseUrl: "https://...",
        type: CloudType.SANDBOX,
        connectTimeoutMs: 10_000,
        readTimeoutMs: 30_000,
    },
    padController: null,
};
const sdk = new PineBillingSdk(config, /*appToAppBridge*/ null, /*platformBridge*/ null);
```

For real-world integration today, use the Android (Kotlin / Java) or JVM bindings — see `languages/android/` and `languages/jvm/`.
