# Android — Errors & First-run Sanity (Pine Billing SDK 0.5.0-preview.2)

> **AI INSTRUCTIONS:** When the user reports an error from this list, use the "Cause" and "Fix" columns verbatim. Do NOT invent alternate explanations.

## First-run sanity check

After a clean integration, run the build and a single Sale once. If anything goes wrong, match the error to a row in the table; the cause is almost always a configuration miss, not an SDK bug.

| # | Symptom | Where | Cause | Fix |
|---|---|---|---|---|
| 1 | `Unresolved reference: BuildConfig` | compile | AGP 8+ disables `BuildConfig` by default. | Add `buildFeatures { buildConfig = true }`. |
| 2 | `Could not find net.java.dev.jna:jna:5.14.0` | resolve | Missing JNA dependency. | Add `implementation("net.java.dev.jna:jna:5.14.0@aar")`. **Do not drop `@aar`** — the plain JAR variant is not Android-compatible. |
| 3 | `java.lang.UnsatisfiedLinkError: dlopen failed: library "libjnidispatch.so" not found` | runtime | Used JNA plain JAR instead of `@aar`. | Switch dependency to `net.java.dev.jna:jna:5.14.0@aar`. |
| 4 | `java.lang.UnsatisfiedLinkError: dlopen failed: "libuniffi_pine_billing.so" not found` | runtime | Running on x86 / x86_64 emulator. AAR ships arm64-v8a + armeabi-v7a only. | Use a real arm64 device or an `arm64-v8a` emulator image. |
| 5 | Build fails with `2 files found with path 'lib/arm64-v8a/libc++_shared.so'` | merge | JNA AAR and the SDK AAR both ship `libc++_shared.so`. | `android.packaging.jniLibs.pickFirsts += "**/libc++_shared.so"`. |
| 6 | `kotlinOptions can not be applied` (AGP 9) | configure | `kotlinOptions { jvmTarget = "17" }` is removed in AGP 9. | Use `kotlin { compilerOptions { jvmTarget = JvmTarget.JVM_17 } }`. |
| 7 | `IllegalStateException: PineBillingSdk method called from main thread` | runtime | Called `do_transaction` / `connect` / `cancel` / etc. on `Dispatchers.Main`. | Wrap the call in `withContext(Dispatchers.IO) { … }`. |
| 8 | `error: cannot find symbol: kotlin.UInt.constructor-impl` (Java) | compile | Tried to construct `kotlin.UInt`/`ULong` directly from Java. | Use the `Unsigned` helper (`com.merchant.pos.Unsigned.toUInt(...)` / `toULong(...)`). |

## SdkError variants → triage

| Variant | Likely cause | Action |
|---|---|---|
| `InvalidInput(detail)` | Configuration or `TransactionRequest` violates a documented rule. | Read `detail`. Common: missing `transport_options.Cloud`, mismatched `transport_options` variant, `currency` not 3-uppercase ASCII, `original_event_id` mismatch. |
| `OperationInProgress(eventId)` | An earlier op has not finished. | Wait for the listener's terminal-state callback before re-issuing. |
| `NotConnected` | Active transport requires a prior `connect()`. | Today only reachable on PADController if you haven't called `connect()`. |
| `TransportUnavailable(detail)` | Active transport cannot be reached. | AppToApp: confirm `com.pinelabs.masterapp` is installed and `<queries>` block is present. PADController: confirm the upstream daemon is running on `127.0.0.1:8082`. |
| `NotSupported` | The active transport does not implement this method (see capability matrix). | Switch transport, or remove the call. |
| `Timeout` | No reply within budget. | On Cloud, follow up with `check_status`. |
| `TransactionFailed` | Terminal returned a non-success code. | Surface `failure_detail` and `terminal_response_code` to the merchant. |
| `Cancelled` | Caller-initiated cancel succeeded mid-flight (Cloud). | Re-check via `check_status` to confirm state. |
| `Network` / `ConnectionTimeout` / `ReadTimeout` / `NonSuccessHttp` | Cloud HTTP-layer failures. | Retry-with-idempotency or `check_status`. |
| `TransportError(detail)` | Transport-layer fault. | Inspect `detail`; on PADController this often means the daemon dropped the link. |
| `Internal(detail)` | SDK defect. | File an issue with `detail`, the operation, and the active transport. |

## ProGuard / R8 stripped UniFFI bindings

If you have R8 enabled and see `ClassNotFoundException: uniffi.pine_billing.…` at runtime, the consumer rules shipped inside the AAR have a known typo (they reference `uniffi.pine_billing_sdk.**`). Until the next preview, add this to your app's `proguard-rules.pro`:

```
-keep class uniffi.pine_billing.** { *; }
-keep class com.pinelabs.billing.sdk.** { *; }
```

## Where the listener callbacks come from

If you set a breakpoint inside `TransactionListener.onSuccess` and inspect the thread name, you'll see `pine-billing-sdk-worker`. That is expected. Marshal to `Dispatchers.Main` before touching UI.
