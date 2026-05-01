# Language: JVM — Integration

> **AI INSTRUCTIONS:** The JVM binding has no façade. Call `uniffi.pine_billing.PineBillingSdk` directly. There is no main-thread guard — the merchant is responsible for not blocking the UI / EDT / FX thread.

## SDK construction

```kotlin
import uniffi.pine_billing.CloudConfig
import uniffi.pine_billing.CloudType
import uniffi.pine_billing.PineBillingSdk
import uniffi.pine_billing.SdkConfig
import uniffi.pine_billing.TransportType

val config = SdkConfig(
    defaultTimeoutMs = 60_000u,
    logLevel = null,
    transport = TransportType.CLOUD,
    appToApp = null,
    applicationId = null,
    cloud = CloudConfig(
        type = CloudType.ISM,
        baseUrl = System.getenv("CLOUD_BASE_URL"),
        connectTimeoutMs = 5_000u,
        readTimeoutMs = 245_000u,
    ),
    padController = null,
)
val sdk = PineBillingSdk(config, /*appToAppBridge*/ null, /*platformBridge*/ null)
```

* AppToApp is **not available** on this binding. There is no upstream
  PoS Messenger IPC primitive on a generic JVM. Use Cloud or
  PADController.

## Transport selection

```kotlin
sdk.setTransport(TransportType.PAD_CONTROLLER)
```

The matching sub-config (`padController: PadControllerConfig`) MUST
have been provided at construction.

## Threading

There is **no main-thread guard**. SDK calls block the calling thread
for the duration of the operation. The merchant must:

* dispatch from a background `Thread` / `Executor` on Swing's EDT or
  JavaFX's Application Thread,
* marshal back via `SwingUtilities.invokeLater` /
  `Platform.runLater`,
* on a headless server, wrap the call in whatever async primitive
  your stack uses (Kotlin coroutines, `CompletableFuture`, …).

```kotlin
val pool = Executors.newFixedThreadPool(4)
pool.submit {
    try { sdk.doTransaction(request, listener) }
    catch (e: SdkException) { /* … */ }
}
```

See `concepts/threading.md` for the full contract.

## Listener callbacks

Same contract as on Android: callbacks fire on an SDK-internal worker
thread, are serialised per listener, MUST NOT block, and MUST NOT
touch UI directly. Marshal to your UI thread before updating widgets.

## PADController on a server / desktop

When `transport = PAD_CONTROLLER`, the SDK opens a TCP socket to
`PadControllerConfig.host:port` (default `127.0.0.1:8082`). The host
must be reachable by the JVM process and the daemon must be running
locally — the SDK does NOT spawn the daemon.

To use `restart()`, supply a `PlatformBridge` implementation that
relaunches the daemon (e.g. via `ProcessBuilder` on Linux/macOS, or a
service-control invocation on Windows).

```kotlin
class LinuxRestartBridge : PlatformBridge {
    override fun `restartUpstreamDaemon`() {
        try {
            ProcessBuilder("/usr/bin/systemctl", "restart", "padcontroller")
                .inheritIO().start()
        } catch (e: Exception) {
            throw SdkException.TransportError("restart failed: ${e.message}")
        }
    }
}
val sdk = PineBillingSdk(config, null, LinuxRestartBridge())
```

## Cloud credentials

Source `merchantId`, `securityToken`, and `applicationId` from
environment variables or a secrets manager — NEVER inline them.

## Next docs

`jvm/examples`, `jvm/errors`, `jvm/distribution`,
`concepts/threading`.
