# Model: `PlatformAppToAppBridge` (callback)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Platform bridge for the AppToApp transport. The MasterApp Messenger IPC is Android-only; Rust core does not link to Android APIs. Implementor (Android binding) implements both methods.

## Methods

| Name | Signature | Notes |
|---|---|---|
| `do_transaction` | `[Throws=SdkError] TransactionResult do_transaction(string event_id, TransactionRequest request)` | Bind / send / await reply / unbind synchronously. |
| `test_print` | `[Throws=SdkError] void test_print(string event_id)` | Trigger a test print at the terminal connected to MasterApp. |

## MUST

- Surface bind / IPC failures as TransportUnavailable (synchronous setup) or TransportError (mid-flight).
- Surface reply timeout as Timeout.
- Map MasterApp BaseResponse failures and DetailResponse.ResponseCode != 0 to TransactionFailed{code,message}.

## MUST NOT

- Do not invent fields not present in the typed TransactionRequest — wire JSON is owned by this implementation.
- Do not retain references to event_id beyond the call.

## Cross-references

`constructor`, `do_transaction`, `test_print`, `TransactionRequest`, `TransactionResult`, `SdkError`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
