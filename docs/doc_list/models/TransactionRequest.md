# Model: `TransactionRequest` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Inputs for a single transaction.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `amount` | `u64` | yes | Lowest currency unit (paise for INR). `0 < amount <= 99_999_999`. |
| `currency` | `string?` | no | ISO-4217. Default `"INR"`. If non-null, exactly 3 ASCII uppercase letters. |
| `billing_ref_no` | `string` | yes | Non-blank after trim. |
| `invoice_no` | `string?` | no | Forwarded verbatim. SDK enforces no shape constraint. |
| `transaction_type` | `TransactionType` | yes | |
| `original_event_id` | `string?` | conditional | Required for Refund / Void / Capture; rejected otherwise. |
| `reference_id` | `string?` | no | Max 64 chars. Echoed on `TransactionResult`. |
| `metadata` | `record<string,string>?` | no | Max 10 entries; each value max 256 chars. Never logged. |
| `merchant_id` | `string?` | conditional | Required for transports that don't derive identity from the terminal (Cloud). Omitted on the wire by AppToApp. |
| `terminal_id` | `string?` | conditional | As above. |
| `allowed_payment_modes` | `sequence<PaymentMode>?` | no | Restricts terminal-presented instruments. **Ignored on Cloud in v1.** |
| `transport_options` | `TransportOptions?` | conditional | Variant MUST match active transport. **REQUIRED on Cloud.** |

## MUST

- Pass `amount` in paise (lowest currency unit), not major units.
- For Refund / Void / Capture, set `original_event_id` to the original Sale's `event_id`.
- For Cloud, populate `transport_options` with the Cloud variant.

## MUST NOT

- Do not generate `event_id` yourself — the SDK allocates it.
- Do not log `metadata`.

## Cross-references

`TransactionType`, `PaymentMode`, `TransportOptions`, `apis/do_transaction`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
