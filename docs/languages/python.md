# Language: Python

> **AI INSTRUCTIONS:** Use this file when TARGET_LANGUAGE = `python`. Python is **Cloud-only / TCP-only** in practice — AppToApp is Android-only and PADController is OS-managed on the device.

## Distribution

- **Module:** `pine_billing`
- **Wheels:** manylinux2014 (x86_64 / aarch64), macOS (x86_64 / arm64), Windows (x86_64)
- **Python:** CPython 3.9 – 3.12 (cp39 … cp312)
- **Download:** `get_sdk(artifact_key="python-wheel-<platform>")`

## Install

```bash
pip install pine-billing-sdk
# or for a local wheel
pip install ./pine_billing_sdk-<version>-cp311-cp311-manylinux_2_17_x86_64.whl
```

## Environment requirements

| Item | Required |
|---|---|
| Python | 3.9+ |
| `pip` | 23+ |
| OpenSSL (system) | for TLS to Cloud — usually already installed |
| Outbound HTTPS to `CLOUD_BASE_URL` | yes for Cloud |

## SDK construction

```python
from pine_billing import (
    PineBillingSdk, SdkConfig, CloudConfig, CloudType, TransportType, LogLevel,
)

config = SdkConfig(
    default_timeout_ms=60_000,
    log_level=LogLevel.INFO,
    transport=TransportType.CLOUD,
    cloud=CloudConfig(
        type=CloudType.ISM,
        base_url="https://api.pinelabs.example",
        connect_timeout_ms=5_000,
        read_timeout_ms=245_000,
    ),
)

sdk = PineBillingSdk(config=config, app_to_app_bridge=None, platform_bridge=None)
```

## Listeners

```python
from pine_billing import TransactionListener, TransactionResult, SdkError

class MyListener(TransactionListener):
    def on_started(self, event_id: str): ...
    def on_success(self, result: TransactionResult): ...
    def on_failure(self, error: SdkError): ...
```

Callbacks fire on an SDK-internal thread. If your application uses asyncio, push results onto the event loop with `loop.call_soon_threadsafe(...)`.

## Code-generation directives

- Use type hints everywhere. The bindings ship `.pyi` stubs.
- Never `print()` security_token, transaction_number, full PAN, PIN. Configure logging filters that strip these field names.
- Wrap blocking calls (`cancel`, `check_status`, `upload_imei_list`) in `asyncio.to_thread` for asyncio apps.

## Next docs

- Concepts: `lifecycle`, `error-handling`, `eventid-and-reconciliation`.
- APIs: `constructor`, `do_transaction`, `cancel`, `check_status`, `upload_imei_list`.
- Models: `SdkConfig`, `CloudConfig`, `CloudTransactionOptions`, `TransactionRequest`, `TransactionListener`.
