# Model: `PlatformAppToAppBridge` (callback interface)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Platform bridge for the AppToApp transport. The MasterApp Messenger IPC is Android-only; the Rust core must not link to any Android API. This callback interface is the boundary.

> **On Android the merchant does NOT implement this directly.** The
> `com.pinelabs.billing.sdk.PineBillingSdk` façade auto-builds a
> `MasterAppTransport` from `SdkConfig.app_to_app` and
> `SdkConfig.application_id`. On non-Android bindings (JVM, ios,
> python, …) AppToApp is unavailable — those bindings have no
> upstream Messenger IPC primitive.

## Methods

| Name | Signature | Notes |
|---|---|---|
| `do_transaction` | `do_transaction(string event_id, TransactionRequest request) -> TransactionResult` (throws `SdkError`) | Run a Sale / Refund / Void / Capture / PreAuth via the upstream Messenger transport. |
| `test_print` | `test_print(string event_id)` (throws `SdkError`) | Trigger a test print at the terminal. |

## Threading

Methods are invoked from the SDK worker thread and are allowed to block — bind / send / await reply / unbind happen synchronously inside one call.

## Error mapping

- Bind / IPC setup failure → `SdkError.TransportUnavailable`.
- Mid-flight IPC failure → `SdkError.TransportError`.
- Reply timeout → `SdkError.Timeout`.
- Upstream validation failure or non-zero `DetailResponse.ResponseCode` → `SdkError.TransactionFailed { detail, terminal_response_code }`.

## Cross-references

`apis/constructor`, `SdkError`, `TransactionResult`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
