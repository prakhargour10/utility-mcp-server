# Python — Distribution (Pine Billing SDK 0.5.0-preview.2)

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**

The Python binding is on the post-1.0 roadmap. It is NOT included in the 0.5.0-preview.2 distribution. The Rust core and UniFFI scaffolding are language-agnostic, so a Python binding is mechanically possible — but it has not been built, tested, or signed off.

The shape below is a plausible projection from the UDL; treat it as **unverified** until a binding ships.

```python
from pine_billing import PineBillingSdk, SdkConfig, CloudConfig, CloudType, TransportType

config = SdkConfig(
    default_timeout_ms=60_000,
    log_level=None,
    transport=TransportType.CLOUD,
    app_to_app=None,
    application_id=None,
    cloud=CloudConfig(
        base_url="https://...",
        type=CloudType.SANDBOX,
        connect_timeout_ms=10_000,
        read_timeout_ms=30_000,
    ),
    pad_controller=None,
)
sdk = PineBillingSdk(config=config, app_to_app_bridge=None, platform_bridge=None)
```

For real-world integration today, use the Android (Kotlin / Java) or JVM bindings — see `languages/android/` and `languages/jvm/`.
