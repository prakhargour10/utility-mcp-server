# Model: `SdkError` (error)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

All SDK failures surface as a variant of SdkError.

## Variants

| Name | Signature | Notes |
|---|---|---|
| `InvalidInput` | `InvalidInput(string detail)` | Caller-supplied input failed validation. |
| `TransportUnavailable` | `TransportUnavailable(string detail)` | Transport could not be reached / bound. |
| `Timeout` | `Timeout(string detail)` | No reply within configured timeout. |
| `TransactionFailed` | `TransactionFailed(string detail, string? terminal_response_code)` | Terminal returned a non-success response. |
| `Internal` | `Internal(string detail)` | SDK-side bug or malformed reply. Treat as defect. |
| `NotConnected` | `NotConnected()` | Caller should connect or retry. |
| `OperationInProgress` | `OperationInProgress(string active_event_id)` | Concurrent op on the same SDK instance. |
| `Cancelled` | `Cancelled()` | Caller-initiated cancellation completed. |
| `TransportError` | `TransportError(string detail)` | Mid-stream transport failure. |
| `NotSupported` | `NotSupported(string detail)` | Active transport does not support this capability. |
| `ConnectionTimeout` | `ConnectionTimeout(string detail)` | HTTP/TCP connect phase exceeded budget. |
| `ReadTimeout` | `ReadTimeout(string detail)` | HTTP response-read phase exceeded budget. |
| `Network` | `Network(string detail)` | DNS / TLS / socket failure. |
| `NonSuccessHttp` | `NonSuccessHttp(u16 status, string body)` | HTTP non-2xx. Inspect status to decide retry. |

## MUST

- Map each variant to a distinct merchant-facing recovery path.
- Log only `detail` and codes — never raw card data.

## MUST NOT

- Do not parse `detail` for control flow — it is human diagnostic only.
- Do not parse NotSupported.detail programmatically — wording varies by language binding.

## Cross-references

`error-handling`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
