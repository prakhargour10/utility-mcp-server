# Model: `AppToAppTransactionOptions` (dictionary)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

AppToApp-specific request extras. Field names map verbatim to upstream PoS JSON keys. All optional and only emitted when populated.

## Fields

| Name | Type | Required | Notes |
|---|---|---|---|
| `gst_in` | `string?` | no | Merchant GSTIN. Maps to upstream `gstIn`. |
| `gst_brk_up` | `string?` | no | GST line-item breakup. Maps to `gstBrkUp`. |
| `service_id` | `string?` | no | NCMC service id. Maps to `serviceID`. |
| `service_mi` | `string?` | no | NCMC merchant identifier. Maps to `serviceMI`. |
| `is_transit_mode` | `boolean?` | no | NCMC transit mode flag. Maps to `isTransitMode`. |
| `payment_mode` | `string?` | no | NCMC payment-mode code (free-form). Distinct from typed `PaymentMode`. |
| `service_data` | `string?` | no | NCMC service payload. Maps to `serviceData`. |

## Cross-references

`TransportOptions`, `TransactionRequest`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
