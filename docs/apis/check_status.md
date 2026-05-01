# API: `check_status`

> **AI INSTRUCTIONS:** This file describes the public method `check_status` on
> `PineBillingSdk`. Read it before emitting any code that calls this
> method. Validation rules and error semantics are normative.

## Signature (UDL canonical)

```
check_status(string event_id, CheckStatusOptions? options) -> OperationStatus
```

## Purpose

Query the lifecycle state of a prior op by event_id. Used for crash-recovery and reconciliation.

## Parameters

| Name | Type | Required | Notes |
|---|---|---|---|
| `event_id` | `string` | yes | Same semantics as cancel. |
| `options` | `CheckStatusOptions?` | conditional | Required for Cloud (CheckStatusOptions.Cloud{merchant_id,security_token,identity}); MUST be null for other transports. |


## Returns

OperationStatus. state == Unknown when SDK has no record of the id (this is a valid recovery answer, not an error).

## Delivery model

Synchronous (returns when the call completes).

## Errors thrown synchronously

- **`SdkError.InvalidInput`** — Cloud transport without options, non-Cloud transport with options.
- **`SdkError.NotSupported`** — Active transport (today: AppToApp).
- **`SdkError.Network / Timeout / ConnectionTimeout / ReadTimeout / NonSuccessHttp`** — Cloud HTTP-layer failures.

## MUST

- Treat OperationState.Unknown as 'not in this SDK instance' — proceed to reconcile via merchant records.
- On Cloud, inspect OperationStatus.cloud_transaction_data when state == Completed.

## MUST NOT

- Do not poll in tight loops; respect cloud.read_timeout_ms.

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
> `sdk.check_status(...)` (idiomatic casing per language: camelCase
> Kotlin/Swift/JS, snake_case Python/C).

## Next docs to fetch

- Models: `CheckStatusOptions`, `CloudCheckStatusOptions`, `OperationStatus`, `OperationState`, `CloudTransactionData`, `SdkError`
- Concepts: `eventid-and-reconciliation`, `result-payload`

## Notes for code generation

- Always re-fetch this doc on any new SDK_VERSION — signature and
  validation rules can change in pre-1.0 minor bumps.
- If the user's TARGET_TRANSPORT is not consistent with this method
  (see capability matrix in `concepts/capabilities.md`), refuse to
  emit the call and ask the user to switch transport.
