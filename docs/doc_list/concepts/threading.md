# Concept: threading

> **AI INSTRUCTIONS:** Use this file to enforce correct thread placement of every blocking SDK call and every listener callback. Threading bugs are the #1 source of integration failures — generate dispatch code defensively.

## Two distinct threading concerns

The SDK has two threading boundaries the merchant code must respect:

1. **Where blocking SDK methods may be called.**
2. **Where listener callbacks fire.**

They are independent and both MUST be handled.

## 1. Where blocking SDK methods may be called

Every transport-touching method on `PineBillingSdk` blocks the calling
thread for the duration of the operation:

* `do_transaction`, `test_print` — block until the listener has been
  notified (cardholder PIN entry can take up to 245 s on
  PADController / Cloud).
* `cancel`, `check_status` — block on Cloud until the HTTPS round-trip
  completes (bounded by `connect_timeout_ms` + `read_timeout_ms`).
* `connect`, `disconnect`, `ping`, `run_self_test`, `get_logs`,
  `get_terminal_info` — block on transport I/O.
* `restart`, `set_transport`, `upload_imei_list`,
  `is_connected` — short, but still synchronous.

### Android

The Android façade enforces a **main-thread guard**: every blocking
method on `com.pinelabs.billing.sdk.PineBillingSdk` throws
`IllegalStateException` if invoked on the main (UI) thread. Dispatch
from a background `Executor`, `kotlinx.coroutines` `Dispatchers.IO`,
or a `WorkManager` worker.

```kotlin
lifecycleScope.launch(Dispatchers.IO) {
    sdk.doTransaction(request, listener)
}
```

### JVM (desktop / server)

There is no main-thread guard on the JVM binding (no concept of "the UI
thread" generically). The merchant is responsible for not blocking
Swing's EDT or JavaFX's Application Thread. Dispatch via
`Executors.newSingleThreadExecutor()` or your stack's async primitive.

## 2. Where listener callbacks fire

`TransactionListener`, `TestPrintListener`, and `DiscoveryListener`
callbacks are invoked from an **SDK-internal worker thread**:

* They are **never** called on the merchant's calling thread.
* They are serialised per listener — `on_started`, `on_success`, and
  `on_failure` never overlap.
* They MUST NOT block (they would stall the SDK worker).
* They MUST NOT touch UI directly — marshal back to the platform UI
  thread first.

## Listener callback contract — clarifying questions

The questions below were raised during integration; the answers are
fact-checked against the UDL contract (`pine_billing.udl` lines
708–732) and the Android façade source. Where the answer cannot be
inferred from source it is marked **TODO** and surfaced to the MCP
team.

### Q: Are `on_started` and `on_success` / `on_failure` on the same SDK worker thread?

**A: Yes.** All three fire from the SDK-internal worker thread that
drives the operation. The UDL doc-comment guarantees they are
serialised per listener — they never overlap, but they do share the
same worker thread.

### Q: If `cancel()` succeeds mid-flight, does `on_failure` fire? With what variant?

**A:** On Cloud, `cancel` is a synchronous blocking call that returns
when the upstream confirms; the in-flight `do_transaction` listener
then fires `on_failure(SdkError.Cancelled)` once the SDK observes the
cancellation. On AppToApp / PADController v1 `cancel` raises
`SdkError.NotSupported` immediately and never affects an in-flight op.

### Q: Is `sdk.doTransaction(...)` from inside `onSuccess` / `onFailure` safe?

**A: NO** — those callbacks run on the SDK worker thread. Re-entering
the SDK from the same worker risks deadlock. **Always marshal to a
fresh executor / dispatcher first.**

```kotlin
override fun onSuccess(result: TransactionResult) {
    chainExecutor.execute {                       // fresh executor
        sdk.doTransaction(nextRequest, nextListener)
    }
}
```

## Safe / unsafe to call inside callbacks

| Operation | Inside `onStarted` | Inside `onSuccess` / `onFailure` |
|---|---|---|
| Synchronous Room DAO methods | ✓ safe (already off-main) | ✓ safe |
| `LiveData.setValue` / Flow `MutableStateFlow.value=` from main observer | ✗ wrong thread — marshal first | ✗ wrong thread — marshal first |
| Touching Android `View` widgets | ✗ never from worker | ✗ never from worker |
| `sdk.doTransaction(...)` (chained transaction) | ✗ unsafe — same worker | ✗ unsafe — same worker |
| `sdk.cancel(...)` / `sdk.checkStatus(...)` | ✗ unsafe — same worker | ✗ unsafe — same worker |
| `Handler(Looper.getMainLooper()).post { … }` | ✓ marshal to main | ✓ marshal to main |
| `withContext(Dispatchers.Main)` | ✓ marshal to main | ✓ marshal to main |
| Persisting `eventId` to disk (synchronous) | ✓ required pattern | n/a |

## Stress note: `onStarted` is on the SDK worker thread, NOT main

Even though `onStarted` typically arrives within a few milliseconds of
`do_transaction` returning, it is delivered from the SDK worker
thread. Code in `onStarted` that touches UI or main-thread-only state
WILL crash on Android.

## MUST

- Always dispatch SDK calls off the platform UI thread.
- Always marshal back to the UI thread inside a callback before
  touching widgets.
- Disable the trigger control on `onStarted`, re-enable on terminal-
  state callback.

## MUST NOT

- Do not call any blocking SDK method from the Android main thread —
  it throws.
- Do not block inside any listener callback.
- Do not assume callbacks fire on the calling thread — they don't.
- Do not call `sdk.doTransaction` from inside any listener callback —
  marshal to a fresh executor first.

## Next docs

`lifecycle`, `error-handling`, per-binding `integration.md`.
