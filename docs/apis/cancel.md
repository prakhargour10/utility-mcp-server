# API: `cancel`

> **AI INSTRUCTIONS:** This file describes the public method `cancel` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
cancel(string event_id, CancelOptions? options)
```

## Purpose

Best-effort cancel of an in-flight op identified by event_id. If the terminal already committed, the op is NOT cancelled and eventual outcome is Success.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `event_id` | `string` | yes | AppToApp/TCP/PADController: the SDK-allocated UUID from on_started. Cloud: the PlutusTransactionReferenceID echoed in TransactionResult.transaction_id. |
| `options` | `CancelOptions?` | conditional | Required for Cloud (CancelOptions.Cloud{amount,merchant_id,security_token,identity}); MUST be null for other transports. |


## Returns

void on accepted-by-transport. Synchronous; on Cloud bounded by cloud.connect_timeout_ms + read_timeout_ms.

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — Cloud transport without options, non-Cloud transport with options, malformed amount.
- **`SdkError.NotSupported`** — Active transport has no cancel mechanism (today: AppToApp).
- **`SdkError.TransportError / Timeout / Network / ConnectionTimeout / ReadTimeout / NonSuccessHttp`** — Cloud HTTP-layer failures.

## MUST

- Use the exact event_id from on_started (or the cloud reference for Cloud).
- Wrap the call in the platform-idiomatic async primitive (it blocks).

## MUST NOT

- Do not assume cancel succeeded means the transaction did not happen — re-check via check_status.

## Per-language call shape

```kotlin
// Kotlin
val sdk = PineBillingSdk(config, /*appToAppBridge*/null, /*platformBridge*/null)
```
```swift
// Swift
let sdk = try PineBillingSdk(config: config, appToAppBridge: nil, platformBridge: nil)
```
```python
# Python
sdk = PineBillingSdk(config=config, app_to_app_bridge=None, platform_bridge=None)
```
```javascript
// Node.js
const sdk = new PineBillingSdk(config, /*appToAppBridge*/null, /*platformBridge*/null);
```
```c
/* C */
PineBillingSdk* sdk = pine_billing_sdk_new(&config, NULL, NULL, &err);
```
> The above is the constructor shape; for non-constructor APIs use
> `sdk.cancel(...)` (idiomatic casing per language: camelCase
> Kotlin/Swift/JS, snake_case Python/C).

## Next docs to fetch

- Models: `CancelOptions`, `CloudCancelOptions`, `CloudIdentity`, `SdkError`
- Concepts: `eventid-and-reconciliation`, `lifecycle`, `error-handling`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
