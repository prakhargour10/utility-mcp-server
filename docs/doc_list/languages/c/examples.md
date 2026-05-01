# C — Examples (Pine Billing SDK 0.5.0-preview.2)

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

The C binding is on the post-1.0 roadmap. It is NOT included in the 0.5.0-preview.2 distribution. The Rust core and UniFFI scaffolding are language-agnostic, so a C binding is mechanically possible — but it has not been built, tested, or signed off.

The shape below is a plausible projection from the UDL; treat it as **unverified** until a binding ships.

```c
#include "pine_billing.h"

PineBillingError err = {0};
SdkConfig config = { /* … */ };
PineBillingSdk* sdk = pine_billing_sdk_new(&config, NULL, NULL, &err);
if (err.code) { /* handle */ }
```

For real-world integration today, use the Android (Kotlin / Java) or JVM bindings — see `languages/android/` and `languages/jvm/`.
