# Concept: capabilities

> **AI INSTRUCTIONS:** Use this matrix to refuse to emit a method call when the active transport does not support it. The SDK will raise `NotSupported` at runtime; catching it earlier in generated code is preferred.

| Capability | AppToApp | Tcp ※ | Cloud | PADController (BT/USB/Serial) |
|---|---|---|---|---|
| `do_transaction` / `test_print` | ✓ | ✓ | ✓ ✚ | ✓ |
| `cancel` | `NotSupported` | ✓ | ✓ ✚ | ✓ |
| `check_status` | `NotSupported` | ✓ | ✓ ✚ | ✓ (in-memory) |
| `connect` / `disconnect` / `is_connected` | no-op † | ✓ | no-op (HTTPS per call) | ✓ |
| `discover_terminals` | `NotSupported` | ✓ | `NotSupported` | ✓ ‡ |
| `ping` / `run_self_test` / `get_logs` / `get_terminal_info` | `NotSupported` | ✓ | `NotSupported` | ✓ |
| `restart` | `NotSupported` | `NotSupported` | `NotSupported` | ✓ (requires `PlatformBridge`) |
| `upload_imei_list` | `NotSupported` | `NotSupported` | ✓ | `NotSupported` |

**†** AppToApp binds the MasterApp service per call. `connect` / `disconnect` are accepted as no-ops; `is_connected` returns true only mid-call.

**◊** AppToApp protocol exposes neither cancel nor reconciliation endpoints.

**‡** PADController discovery is transport-specific: Bluetooth ✓; USB and Serial enumerate the device list known to the PADController.

**※** Tcp is a v1 placeholder; calls may raise `NotSupported`.

**✚** Cloud `do_transaction` resolves with `TransactionStatus.Pending`; the merchant drives settlement via `check_status`. Cloud `cancel` / `check_status` require `*Options::Cloud`.

## Next docs

`transports`, `error-handling`.
