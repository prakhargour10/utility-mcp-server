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
from a background `Executor`, `kotlinx.coroutines` `Dispatchers.IO`, or
a `WorkManager` worker.

```kotlin
lifecycleScope.launch(Dispatchers.IO) {
    sdk.doTransaction(request, listener)
}
```

The guard does NOT apply to `disconnect()`, `isConnected()`, or
`setTransport()` — they are short — but emitting them on a background
thread anyway is harmless and keeps the codebase consistent.

### JVM (desktop / server)

There is no main-thread guard on the JVM binding (no concept of "the UI
thread" generically). The merchant is responsible for not blocking
Swing's EDT or JavaFX's Application Thread:

```kotlin
// Swing
SwingUtilities.invokeLater {
    button.isEnabled = false
}
Thread {
    try {
        sdk.doTransaction(request, listener)
    } catch (e: SdkException) { /* … */ }
}.start()

// JavaFX
Platform.runLater { button.isDisable = true }
val task = object : Task<Unit>() {
    override fun call() { sdk.doTransaction(request, listener) }
}
Thread(task).start()
```

## 2. Where listener callbacks fire

`TransactionListener`, `TestPrintListener`, and `DiscoveryListener`
callbacks are invoked from an **SDK-internal worker thread**:

* They are **never** called on the merchant's calling thread.
* They are serialised per listener — `on_started`, `on_success`, and
  `on_failure` never overlap.
* They MUST NOT block (they would stall the SDK worker).
* They MUST NOT touch UI directly — marshal back to the platform UI
  thread first.

### Android — marshal pattern

```kotlin
override fun onSuccess(result: TransactionResult) {
    val main = Handler(Looper.getMainLooper())
    main.post {
        Toast.makeText(context, "Charge ok: ${'$'}{result.eventId}", Toast.LENGTH_LONG).show()
    }
}
```

### JVM — marshal pattern

```kotlin
// Swing
override fun onSuccess(result: TransactionResult) {
    SwingUtilities.invokeLater { resultLabel.text = "ok ${'$'}{result.eventId}" }
}

// JavaFX
override fun onSuccess(result: TransactionResult) {
    Platform.runLater { resultLabel.text = "ok ${'$'}{result.eventId}" }
}

// Headless / server
override fun onSuccess(result: TransactionResult) {
    completion.complete(result)   // CompletableFuture<TransactionResult>
}
```

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

## Next docs

`lifecycle`, `error-handling`, per-binding `integration.md`.
