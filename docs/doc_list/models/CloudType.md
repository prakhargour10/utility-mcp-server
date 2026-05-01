# Model: `CloudType` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Cloud transport sub-mode. Single variant for v1; additional variants will be added in future minor releases.

## Variants

| Name | Notes |
|---|---|
| `Ism` | Pinelabs ISM cloud endpoint. |

## MUST

- Generated `when` / `switch` matches MUST include a default arm — this is an open enum.

## Cross-references

`CloudConfig`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
