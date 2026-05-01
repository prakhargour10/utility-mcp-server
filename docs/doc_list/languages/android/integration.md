# Language: Android — Integration

> **AI INSTRUCTIONS:** Use this file to wire the SDK into a real Android app. The patterns below are mandatory; thread / Context / lifecycle bugs are the most common integration failures.

## SDK construction

```kotlin
import android.content.Context
import com.pinelabs.billing.sdk.PineBillingSdk
import uniffi.pine_billing.AppToAppConfig
import uniffi.pine_billing.SdkConfig
import uniffi.pine_billing.TransportType

val config = SdkConfig(
    defaultTimeoutMs = 60_000u,
    logLevel = null,
    transport = TransportType.APP_TO_APP,
    appToApp = AppToAppConfig(userId = "POS-USER", version = "1.0"),
    applicationId = BuildConfig.PINELABS_APP_ID,
    cloud = null,
    padController = null,
)

// Android façade signature: (Context, SdkConfig, PlatformBridge? = null).
// The MasterAppTransport bridge is auto-built from `config.appToApp` and
// `config.applicationId`. Pass an AndroidSystemBridge as the third
// argument only if you intend to call sdk.restart() on PADController.
val sdk = PineBillingSdk(applicationContext, config)
```

Construct **once per process** and reuse — closing and re-opening per
transaction is wrong (it tears down Rust-side capability state).

## Transport selection

```kotlin
// Initial transport comes from SdkConfig.transport.
// To switch at runtime:
sdk.setTransport(TransportType.CLOUD)
```

`set_transport` requires that the matching sub-config was supplied at
construction (e.g. `cloud: CloudConfig` if you'll later switch to
Cloud).

## Lifecycle

| Hook | What to do |
|---|---|
| `Application.onCreate()` | Construct the SDK; hold it in a singleton. |
| `Activity.onCreate()` | Acquire the singleton; do NOT construct here. |
| `onDestroy()` of the last Activity | Nothing — the SDK is a process-scoped singleton. |
| Process death | The SDK's in-memory state is lost; use `check_status` (Cloud) for reconciliation. |

## Threading (mandatory)

Every blocking method on `PineBillingSdk` throws
`IllegalStateException` if called on the Android main thread. Dispatch
from a background context:

```kotlin
// Coroutines (recommended)
lifecycleScope.launch(Dispatchers.IO) {
    runCatching { sdk.doTransaction(request, listener) }
        .onFailure { /* surface error */ }
}

// Or an Executor
val io = Executors.newSingleThreadExecutor()
io.execute { sdk.doTransaction(request, listener) }
```

Listener callbacks fire on the SDK's worker thread. Marshal back to
the main thread before touching the UI:

```kotlin
override fun onSuccess(result: TransactionResult) {
    Handler(Looper.getMainLooper()).post {
        Toast.makeText(context, "OK ${result.eventId}", Toast.LENGTH_LONG).show()
    }
}
```

See `concepts/threading.md` for the full contract.

## Foreground service (recommended)

A card transaction can take up to 245 s (cardholder PIN entry). If the
user backgrounds the app mid-transaction the OS may kill the process.
Wrap the call in a foreground service:

```kotlin
class TransactionService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIF_ID, buildOngoingNotification())
        Thread {
            try { sdk.doTransaction(request, listener) }
            finally { stopSelf() }
        }.start()
        return START_NOT_STICKY
    }
    override fun onBind(intent: Intent?): IBinder? = null
}
```

## AppToApp `application_id` provisioning

`SdkConfig.applicationId` is a Pinelabs-provisioned identifier
forwarded as `Header.ApplicationId`; the upstream PoS service rejects
DoTransaction calls (`MethodId="1001"`) with an unknown id.

* Source it from `BuildConfig` populated from a non-VCS secrets file.
* NEVER inline it in Kotlin source.
* In production, `appToApp.version` MUST be `"1.0"`.

```kotlin
// gradle.properties (NOT in VCS)
PINELABS_APP_ID=…the value Pinelabs gave you…

// build.gradle.kts
buildConfigField("String", "PINELABS_APP_ID",
    "\"${project.findProperty("PINELABS_APP_ID")}\"")
```

## Restart support (PADController only)

If you've selected `TransportType.PAD_CONTROLLER` and you want
`sdk.restart()` to work, supply an `AndroidSystemBridge` at
construction:

```kotlin
val bridge = AndroidSystemBridge(
    context = applicationContext,
    restartIntent = Intent("com.pinelabs.padcontroller.ACTION_RESTART").apply {
        setPackage("com.pinelabs.padcontroller")
    },
    deliveryMode = AndroidSystemBridge.DeliveryMode.BROADCAST,
)
val sdk = PineBillingSdk(applicationContext, config, bridge)
```

The exact intent action / package / delivery mode is OEM-specific —
consult your terminal vendor.

## Next docs

`android/examples`, `android/errors`, `android/distribution`,
`concepts/threading`, `concepts/lifecycle`.
