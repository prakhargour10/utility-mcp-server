# Concept: capabilities

> **AI INSTRUCTIONS:** Use this matrix to refuse to emit a method call when the active transport does not support it. The SDK will raise `NotSupported` at runtime; catching it earlier in generated code is preferred.
>
> The matrix below reflects what is **actually implemented in v1** of each
> adapter (SDK version `0.5.0-preview.2`). The PADController adapter ships
> with a deliberately small surface — `do_transaction`, probe-style
> connect / disconnect, and `restart` — and reports `NotSupported` for
> everything else, even the methods many merchants associate with a
> Bluetooth/USB/Serial terminal. Do not assume parity with future releases.

## v1 capability matrix (authoritative)

| Capability | AppToApp | Tcp ※ | Cloud | PADController (v1) |
|---|---|---|---|---|
| `do_transaction` | ✓ | ✗ `NotSupported` | ✓ ✚ | ✓ |
| `test_print` | ✓ | ✗ `NotSupported` | ✗ `NotSupported` | ✗ `NotSupported` |
| `cancel` | ✗ `NotSupported` ◊ | ✗ `NotSupported` | ✓ ✚ | ✗ `NotSupported` |
| `check_status` | ✗ `NotSupported` ◊ | ✗ `NotSupported` | ✓ ✚ | ✗ `NotSupported` |
| `connect` | no-op † | ✗ `NotSupported` | no-op (HTTPS per call) | ✓ (probe-only) |
| `disconnect` | no-op † | ✗ `NotSupported` | no-op | ✓ |
| `is_connected` | true mid-call only † | `false` | `false` (per-call) | tracks last probe |
| `discover_terminals` | ✗ `NotSupported` | ✗ `NotSupported` | ✗ `NotSupported` | ✗ `NotSupported` |
| `ping` | ✗ `NotSupported` | ✗ `NotSupported` | ✗ `NotSupported` | ✗ `NotSupported` |
| `run_self_test` | ✗ `NotSupported` | ✗ `NotSupported` | ✗ `NotSupported` | ✗ `NotSupported` |
| `get_logs` | ✗ `NotSupported` | ✗ `NotSupported` | ✗ `NotSupported` | ✗ `NotSupported` |
| `get_terminal_info` | ✗ `NotSupported` | ✗ `NotSupported` | ✗ `NotSupported` | ✗ `NotSupported` |
| `restart` | ✗ `NotSupported` | ✗ `NotSupported` | ✗ `NotSupported` | ✓ (requires `PlatformBridge`) |
| `upload_imei_list` | ✗ `NotSupported` | ✗ `NotSupported` | ✓ | ✗ `NotSupported` |

**†** AppToApp binds the upstream Pinelabs PoS service per call. `connect` /
`disconnect` are accepted as no-ops; `is_connected` returns `true` only
while a call is in flight.

**◊** AppToApp protocol exposes neither cancel nor reconciliation
endpoints. Use `Cloud` if you need cancel/reconciliation.

**※** `Tcp` is a v1 placeholder; every method raises `NotSupported`
until the adapter ships.

**✚** Cloud `do_transaction` resolves with `TransactionStatus.Pending`;
the merchant drives settlement via `check_status`. Cloud `cancel` /
`check_status` require `*Options::Cloud` extras.

## Roadmap (post-`0.5.0-preview.2`)

The following are **not implemented** in v1 of the PADController adapter
and are tracked for later releases:

* `discover_terminals` (Bluetooth scan, USB enumeration)
* `cancel`, `check_status`
* `test_print`
* Diagnostics: `ping`, `run_self_test`, `get_logs`, `get_terminal_info`

Do not generate code that calls any of these against PADController until
the matrix is updated.

## Next docs

`transports`, `error-handling`, `distribution`, `threading`.
