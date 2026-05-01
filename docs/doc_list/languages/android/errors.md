# Language: Android — Errors (root-cause-indexed)

> **AI INSTRUCTIONS:** When the user reports a runtime error, look it up in this table FIRST before generating any fix. Each row is keyed by the symptom the merchant sees in `logcat` or a stack trace.

## Common runtime failures

### `java.lang.UnsatisfiedLinkError: dlopen failed: library "libuniffi_pine_billing.so" not found`

**Root cause:** The native library was stripped from the APK or the
device's ABI is not in the AAR.

**Fix:**

1. Confirm the AAR was placed under `app/libs/` and `implementation(files("libs/pine-billing-sdk-0.5.0-preview.2.aar"))` is in the dependency block.
2. The AAR ships only `arm64-v8a` and `armeabi-v7a`. Emulator images
   targeting `x86` / `x86_64` are unsupported in `0.5.0-preview.2`.
3. If you use `splits` or `abiFilters`, ensure `arm64-v8a` (and
   `armeabi-v7a` if you target older devices) is included.
4. Do NOT use `useLegacyPackaging = true` for `jniLibs` — it confuses
   `System.loadLibrary` on some OEM ROMs.

### `java.lang.IllegalStateException: PineBillingSdk.doTransaction() must not be called from the Android main thread`

**Root cause:** The façade's main-thread guard fired. You called a
blocking SDK method from the UI thread.

**Fix:** Dispatch from `Dispatchers.IO`, an `Executor`, or a
`WorkManager` worker. See `android/integration.md` § Threading.

### `bindService(...)` returns `false` (visible as `SdkException.TransportUnavailable`)

**Root cause (Android 11+):** Missing `<queries>` block in
`AndroidManifest.xml`. `PackageManager` filters out packages your app
hasn't declared visibility for, so `bindService` cannot resolve the
upstream PoS package.

**Fix:** Add the `<queries>` block from `android/setup.md` § 3.

**Other root causes:**

* The upstream Pinelabs PoS package is not installed on the device.
* The `applicationId` you supplied is not provisioned for this device.
* `appToApp.version` is not `"1.0"`.

### `SdkException.NotSupported: …`

**Root cause:** The active transport doesn't implement the called
capability in v1. See `concepts/capabilities.md`.

**Fix:** Either (a) `setTransport(...)` to one that does, or (b)
remove the call. Most commonly: PADController v1 implements only
`do_transaction` + probe-style `connect`/`disconnect`/`is_connected` +
`restart`. Everything else (`cancel`, `check_status`, `test_print`,
discovery, diagnostics) raises `NotSupported`.

### Listener callback never fires; logs say nothing

**Root cause:** R8 / ProGuard stripped your listener's methods. The
SDK invokes them via UniFFI's reflection-style dispatch.

**Fix:** Add the keep rules from `android/setup.md` § 4. Verify by
running a `release` build with `-printusage` and confirming your
listener class is retained.

### `SdkException.OperationInProgress(activeEventId)`

**Root cause:** You called `doTransaction` / `testPrint` /
`discoverTerminals` while another listener-style op is in flight on
the same SDK instance.

**Fix:** Disable the trigger control on `onStarted`, re-enable on
`onSuccess` / `onFailure`. If you need to abort, call
`cancel(activeEventId, ...)` (Cloud only — see capability matrix).

### `SdkException.TransportUnavailable("…AAR…native lib…")`

**Root cause:** Native lib loaded but the upstream service couldn't be
bound. Often: testing on an emulator, or device booted without the
PoS service.

**Fix:** Run on a real Pinelabs-paired device. Check `adb shell pm
list packages | grep pinelabs`.

## How to capture diagnostics

```kotlin
catch (e: SdkException) {
    Log.e("PineBilling",
        "variant=${e::class.simpleName} msg=${e.message}", e)
}
```

NEVER log:

* `request.metadata`,
* `result.maskedPan` above debug,
* `cloudConfig.securityToken` or any per-call security token,
* card data, PIN, or full PAN.

## Next docs

`android/distribution`, `concepts/error-handling`, `models/SdkError`.
