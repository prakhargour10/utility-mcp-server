# Model: `CloudType` (enum)

> **AI INSTRUCTIONS:** This file is the spec for the type. Use the exact field names, types, and constraints below. Do NOT add or omit fields.

## Purpose

Cloud transport sub-mode. Single variant in v1.

## Values

| Value | Notes |
|---|---|
| `Ism` | Default and only value in v1. |

## MUST

- Always set to Ism in v1.

## MUST NOT

- Do not exhaustively switch without a default arm — variants will be added.

## Cross-references

`CloudConfig`

## Per-language naming

- Kotlin/Swift/JS: PascalCase types, camelCase fields.
- Python/C: snake_case fields. Python types use PascalCase class names.
- Field names map verbatim from the UDL (snake_case) into Python/C; bindings re-case for Kotlin/Swift/JS automatically.
