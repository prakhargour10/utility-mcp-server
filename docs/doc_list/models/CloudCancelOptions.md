# Model: `CloudCancelOptions` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Cloud cancel extras. Required when the active transport is Cloud. **All four fields are mandatory.**

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `merchant_id` | `string` | yes | |
| `security_token` | `string` | yes | Per-call token; never log. |
| `identity` | `CloudIdentity` | yes | |
| `amount` | `string` | yes | Charge amount, validated `^[0-9]+$`. |

## MUST

- Populate all four fields.
- `amount` matches the original Cloud charge amount as paise digits.
- Never log `security_token`.
- Use the `PlutusTransactionReferenceID` as the `event_id` argument to `cancel` on Cloud — NOT the SDK-allocated UUID.

## MUST NOT

- Do not omit any field. All four are required.
- Do not pass `CancelOptions::Cloud` on a non-Cloud active transport — raises `InvalidInput`.

## Cross-references

`CancelOptions`, `CloudIdentity`, `apis/cancel`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
