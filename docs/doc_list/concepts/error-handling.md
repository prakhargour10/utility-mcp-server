# Concept: error-handling

> **AI INSTRUCTIONS:** Use this file to generate exhaustive error-handling code. Every variant of `SdkError` has a recommended recovery action.

## Error variants and recovery

| Variant | Meaning | Recovery |
|---|---|---|
| `InvalidInput(detail)` | Caller violated a documented validation rule. | Fix the input; never retry blindly. |
| `TransportUnavailable(detail)` | Transport could not be reached / bound. | Verify environment (MasterApp installed, network up); ask user. |
| `Timeout(detail)` | No reply within configured timeout. | Run `check_status(event_id)` to determine if the op committed (Cloud only). |
| `TransactionFailed(detail, terminal_response_code?)` | Terminal returned non-success. | Show user-friendly mapping of `terminal_response_code`. |
| `Internal(detail)` | SDK defect. | Capture diagnostics; report. |
| `NotConnected()` | No active link. | `connect(terminal)` first. |
| `OperationInProgress(active_event_id)` | Concurrent op. | Wait for the current op; or `cancel(active_event_id)` (Cloud only). |
| `Cancelled()` | Caller-initiated cancellation succeeded. | Treat as not-charged; reconcile. |
| `TransportError(detail)` | Mid-stream link failure. | Retry with backoff; reconcile via `check_status`. |
| `NotSupported(detail)` | Active transport lacks the capability. | Switch transport (`set_transport`) or remove the call. |
| `ConnectionTimeout(detail)` | Cloud TCP/TLS handshake exceeded budget. | Retry with longer `connect_timeout_ms`; check network. |
| `ReadTimeout(detail)` | Cloud response read exceeded budget. | `check_status` to determine outcome. |
| `Network(detail)` | DNS / TLS / socket failure. | Retry with backoff. |
| `NonSuccessHttp(status, body)` | HTTP non-2xx. | Inspect `status`; map 4xx → caller error, 5xx → retry. |

## MUST

- Match every variant exhaustively in generated `when` / `match` /
  `switch` constructs (use a default arm but always log it).
- Always log the variant name and (where present)
  `terminal_response_code`. NEVER log raw card data, PIN, full PAN,
  or tokens.
- For `Timeout` / `TransportError` / `ReadTimeout` after
  `do_transaction` was accepted (i.e. `on_started` fired), call
  `check_status(event_id)` before declaring the transaction failed
  (Cloud only — AppToApp / PADController have no `check_status`).

## MUST NOT

- Do not parse `detail` strings programmatically — they are
  diagnostic-only and worded differently per language binding.
- Do not catch `SdkError.Internal` and silently swallow.

## Next docs

`lifecycle`, `eventid-and-reconciliation`, `capabilities`.
