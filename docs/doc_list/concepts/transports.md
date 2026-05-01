# Concept: transports

> **AI INSTRUCTIONS:** Use this file to choose the correct transport and to validate that a generated call is supported on the active transport.

## Available transports

| TransportType | Where it works | Wire | Discovery? | Cancel? | Diagnostics? |
|---|---|---|---|---|---|
| `AppToApp` | Android only | Pinelabs MasterApp Messenger IPC | no | no (v1) | no |
| `Cloud` | any host | HTTPS REST | no | yes (req. options) | no |
| `PadController` | any host with a PADController gateway daemon listening on TCP loopback (default `127.0.0.1:8082`) | TCP-loopback to gateway | ✗ in v1 | ✗ in v1 | ✗ in v1 |
| `Tcp` | placeholder in v1 | TBD | ✗ | ✗ | ✗ |

## Choosing

- **Android merchant app talking to a paired Pinelabs PoS:** `AppToApp`.
- **Server-side merchant (any host, any language):** `Cloud`.
- **Host with a PADController gateway daemon attached to a terminal:**
  `PadController`. The host can be Android, Linux, macOS, or Windows —
  what matters is that the daemon is listening locally; the SDK speaks
  TCP loopback to it.
- **`Tcp`:** do not use in v1. `set_transport(Tcp)` may raise
  `NotSupported`.

## Required config per transport

| Transport | SdkConfig sub-config | Per-call extras |
|---|---|---|
| `AppToApp` | `app_to_app: AppToAppConfig`, `application_id` | `TransportOptions::AppToApp` (optional NCMC/GST fields) |
| `Cloud` | `cloud: CloudConfig` | `TransportOptions::Cloud` **REQUIRED** on `do_transaction`; `CancelOptions::Cloud` REQUIRED on `cancel`; `CheckStatusOptions::Cloud` REQUIRED on `check_status` |
| `PadController` | `pad_controller: PadControllerConfig` (defaults `127.0.0.1:8082`, `connect_timeout_ms=5_000`, `socket_timeout_ms=245_000`) | `TransportOptions::PadController` (loose key/value extras) |

## Switching transports

Use `set_transport(kind)`. It implicitly disconnects the previous
transport. The matching sub-config MUST be present in `SdkConfig` at
construction time, even if `kind` is not the initial transport.

## Capability matrix (authoritative)

See `capabilities` for the full table — the v1 PADController matrix
is much narrower than the protocol family suggests.

## Next docs

`capabilities`, `error-handling`, `distribution`, `threading`.
