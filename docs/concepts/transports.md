# Concept: transports

> **AI INSTRUCTIONS:** Use this file to choose the correct transport and to validate that a generated call is supported on the active transport.

## Available transports

| TransportType | Where it works | Wire | Discovery? | Cancel? | Diagnostics? |
|---|---|---|---|---|---|
| `AppToApp` | Android only | Pinelabs MasterApp Messenger IPC | no | no | no |
| `Cloud` | any | HTTPS REST V1 | no | yes (req. options) | no |
| `PadController` | device-local (Bluetooth/USB/Serial via daemon) | TCP-loopback to gateway | yes | yes | yes |
| `Tcp` | placeholder in v1 | TBD | TBD | TBD | TBD |

## Choosing

- **Android merchant app talking to a paired Pinelabs PoS:** `AppToApp`.
- **Server-side merchant (Python/Node/iOS):** `Cloud`.
- **Embedded device (Linux box) with attached terminal:** `PadController`.
- **`Tcp`:** do not use in v1. `set_transport(Tcp)` may raise `NotSupported`.

## Required config per transport

| Transport | SdkConfig sub-config | Per-call extras |
|---|---|---|
| `AppToApp` | `app_to_app: AppToAppConfig`, `application_id` | `TransportOptions::AppToApp` (optional NCMC/GST fields) |
| `Cloud` | `cloud: CloudConfig` | `TransportOptions::Cloud` **REQUIRED** on `do_transaction`; `CancelOptions::Cloud` REQUIRED on `cancel`; `CheckStatusOptions::Cloud` REQUIRED on `check_status` |
| `PadController` | `pad_controller: PadControllerConfig` (defaults are 127.0.0.1:8082) | `TransportOptions::PadController` (loose key/value extras) |

## Switching transports

Use `set_transport(kind)`. It implicitly disconnects the previous transport. The matching sub-config MUST be present in `SdkConfig` at construction time, even if `kind` is not the initial transport.

## Capability matrix (authoritative)

See `capabilities` doc for the full table.

## Next docs

`capabilities`, `error-handling`.
