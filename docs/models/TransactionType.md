# Model: `TransactionType` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Operation kind. Individual transports may reject types they don't support (returns SdkError.NotSupported).

## Values

| Value | Notes |
|---|---|
| `Sale` | Standard charge. |
| `Refund` | Reverse a previous Sale; original_event_id required. |
| `Void` | Reverse before settlement; original_event_id required. |
| `PreAuth` | Reserve funds; settle later via Capture. |
| `Capture` | Settle a prior PreAuth; original_event_id required. |
| `BalanceInquiry` | Read balance; not all transports support this. |

## MUST

- Set TransactionRequest.original_event_id iff value ∈ {Refund, Void, Capture}.

## MUST NOT

- Do not set original_event_id for Sale, PreAuth, BalanceInquiry.

## Cross-references

`TransactionRequest`, `SdkError`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
