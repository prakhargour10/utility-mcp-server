# Android — Integration (Pine Billing SDK 0.5.0-preview.2)

> **AI INSTRUCTIONS:** Treat the threading and lifecycle rules as normative. Do NOT call SDK methods on the main thread inside generated code. Do NOT touch UI from inside listener callbacks without marshalling.

## Threading

- `PineBillingSdk` enforces an Android main-thread guard on every blocking call. Calling from `Dispatchers.Main` throws `IllegalStateException`.
- Listener callbacks (`TransactionListener`, `TestPrintListener`, `DiscoveryListener`) fire on an **SDK-internal worker thread**. Never touch UI directly — marshal to main first.
- Callbacks are serialised; they will not overlap for one operation.
- Calling another SDK method from inside a callback is **unsafe** (same worker; deadlock risk). Marshal to a fresh executor before re-entering the SDK.

## Lifecycle

- Construct ONCE per process, in `Application.onCreate()`. Reuse the instance.
- The façade is `AutoCloseable`. Closing is generally NOT required for the lifetime of the process; close on test teardown only.

## `applicationId` provisioning

- Read from `BuildConfig.PINELABS_APP_ID`, populated by `~/.gradle/gradle.properties` or the `PINELABS_APP_ID` env var. **Fail fast** during configuration if unset:

```kotlin
val pinelabsAppId = (project.findProperty("PINELABS_APP_ID") as String?)
    ?: System.getenv("PINELABS_APP_ID")
    ?: error("PINELABS_APP_ID not set (use ~/.gradle/gradle.properties or env)")
```

- Never hardcode the production application id in source. Sandbox value is `1001`.

## Java interop

The UDL emits `kotlin.UInt` / `kotlin.ULong` for unsigned wire fields. Java cannot construct these directly. Add this helper to your codebase **once**:

```kotlin
package com.merchant.pos

/**
 * Java interop helper for UniFFI-generated `kotlin.UInt` / `kotlin.ULong` parameters.
 * UniFFI emits these as Kotlin's unsigned types, which Java cannot construct directly.
 * This helper bridges with explicit range checks.
 */
object Unsigned {
    @JvmStatic
    fun toUInt(value: Long): UInt {
        require(value in 0L..0xFFFF_FFFFL) { "value $value does not fit in u32" }
        return value.toInt().toUInt()
    }

    @JvmStatic
    fun toULong(value: Long): ULong {
        require(value >= 0L) { "value $value is negative; cannot be u64" }
        return value.toULong()
    }
}
```

In Java, write `Unsigned.toUInt(60_000L)` and `Unsigned.toULong(19_900L)`. **Do NOT** use `Integers.toUInt` (does not exist) or `kotlin.UInt.constructor-impl` (internal, version-locked, breaks on Kotlin upgrades).

## Persisting `event_id`

Inside `TransactionListener.onStarted(eventId)` you MUST persist the id durably **before returning**. The SDK relies on the merchant to remember in-flight ids across crashes. Synchronous Room DAO writes are safe inside the callback. LiveData/Flow main-thread observers are not — marshal to main first.

## Cloud `transaction_id`

For Cloud transactions, also persist `TransactionResult.transaction_id` (the `PlutusTransactionReferenceID`). It is the parameter to Cloud `cancel`/`check_status`, NOT the SDK `event_id`.

## ProGuard / R8

The AAR ships `consumer-rules.pro`; you do NOT need to copy it into your app. If you have R8 enabled and see `ClassNotFoundException: uniffi.pine_billing.…` at runtime, see `errors.md` § "ProGuard / R8 stripped UniFFI bindings".

## What NOT to do

- Do not block on the main thread; the façade throws.
- Do not invoke UI APIs from listener callbacks without `Dispatchers.Main.dispatch`.
- Do not log card data, full PAN, PIN, CVV, or `securityToken`. `masked_pan` is debug-level only.
- Do not mutate `SdkConfig` after construction — pass a fresh config and reconstruct.
