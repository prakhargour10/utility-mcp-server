# JVM — Errors (Pine Billing SDK 0.5.0-preview.2)

## First-run sanity check

| Symptom | Cause | Fix |
|---|---|---|
| `UnsatisfiedLinkError: Unable to load library 'uniffi_pine_billing'` | JNA cannot find the native lib. | Set `-Djna.library.path=...` to the directory containing `libuniffi_pine_billing.{so,dylib,dll}`. |
| `NoClassDefFoundError: com/sun/jna/Library` | Missing JNA dep. | Add `net.java.dev.jna:jna:5.14.0`. |
| Java: `cannot find symbol: kotlin.UInt.constructor-impl` | Tried to construct unsigned types from Java directly. | Use the `Unsigned` helper from `com.merchant.pos.Unsigned`. |

## SdkError triage

Same variants as Android (`SdkError.InvalidInput`, `OperationInProgress`, `NotSupported`, `Timeout`, `TransactionFailed`, `Cancelled`, `Network`/`ConnectionTimeout`/`ReadTimeout`/`NonSuccessHttp`, `TransportError`, `Internal`). On JVM you will most often see Cloud HTTP-layer errors. Retry with idempotency or fall back to `check_status`.
