# Language: JVM — Errors (root-cause-indexed)

> **AI INSTRUCTIONS:** When the user reports a JVM runtime error, look it up here FIRST. The most common JVM-specific failures are classpath / unsigned-int / native-lib loading.

## Common runtime failures

### `no main manifest attribute, in pine-billing-sdk-0.5.0-preview.2.jar`

**Root cause:** The user ran `java -jar pine-billing-sdk-…jar`. The
JAR is **not** an executable — it's a library JAR with no
`Main-Class` manifest entry.

**Fix:** Run your own application's main class via `java -cp`:

```bash
java -cp "out:lib/pine-billing-sdk-0.5.0-preview.2.jar:lib/jna-5.14.0.jar:lib/kotlin-stdlib-1.9.22.jar" \
     com.merchant.pos.Main
```

### `java.lang.UnsatisfiedLinkError: Unable to load library 'uniffi_pine_billing'`

**Root cause:** JNA cannot find the native library inside the JAR
(usually because JNA itself is missing from the classpath, or the JAR
was rebuilt without the bundled `META-INF/jniLibs/` directory).

**Fix:**

1. Confirm `net.java.dev.jna:jna:5.14.0` is on the classpath.
2. Confirm your OS/arch is one of the bundled triples (see
   `jvm/requirements.md`).
3. As a last resort, set `-Djna.debug_load=true` on the JVM CLI to
   trace JNA's library search.

### `java.lang.ClassNotFoundException: kotlin.UInt`

**Root cause:** `kotlin-stdlib` is missing from the runtime
classpath. UniFFI emits Kotlin types for unsigned integers; even
pure-Java callers need `kotlin-stdlib`.

**Fix:** Add `org.jetbrains.kotlin:kotlin-stdlib:1.9.+` to the
classpath.

### `Cannot construct UInt from Java` (compile-time or `IllegalArgumentException` at runtime)

**Root cause:** Java cannot directly construct `kotlin.UInt` /
`kotlin.ULong`.

**Fix:** Use the `com.merchant.pos.Unsigned` Kotlin helper from
`jvm/setup.md` § 5:

```java
import static com.merchant.pos.Unsigned.toUInt;
UInt timeout = toUInt(60_000L);
```

### `SdkException.TransportUnavailable("AppToApp not available …")`

**Root cause:** AppToApp is Android-only. The JVM binding has no
upstream PoS Messenger IPC.

**Fix:** Use `TransportType.CLOUD` or `TransportType.PAD_CONTROLLER`.

### `java.net.ConnectException: Connection refused (Connection refused)` from PADController

**Root cause:** The PADController gateway daemon is not running on
the configured host/port (default `127.0.0.1:8082`).

**Fix:** Start the daemon, or set
`PadControllerConfig.host`/`port` to where it actually listens.

### `SdkException.NotSupported(…)`

**Root cause:** The active transport doesn't implement the called
capability in v1. See `concepts/capabilities.md`.

## How to capture diagnostics

```kotlin
catch (e: SdkException) {
    log.error("SdkException variant=${e::class.simpleName} msg=${e.message}", e)
}
```

NEVER log: `cloudConfig.securityToken`, `request.metadata`,
`result.maskedPan` above DEBUG, card data, PIN, full PAN.

## Next docs

`jvm/distribution`, `concepts/error-handling`, `models/SdkError`.
