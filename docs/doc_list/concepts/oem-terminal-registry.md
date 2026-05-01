# Concept: oem-terminal-registry

> **AI INSTRUCTIONS:** Use this file when the user reports `bindService` returning false on Android 11+ and you need to advise them which `<queries>` package name to declare. The list below is **best-effort and OEM-specific** — always tell the merchant to confirm with their terminal vendor before shipping.

## Why this matters

Android 11+ (API 30+) introduced **package visibility filtering**:
`PackageManager` and `bindService` will silently fail to resolve a
target package unless your manifest declares it inside a `<queries>`
block. The Pine Billing SDK's AppToApp transport binds to the
upstream Pinelabs PoS service via an explicit `Intent`; without the
right `<queries>` entry the bind returns `false` even when the
upstream package IS installed on the device.

This surfaces from the SDK as
`SdkError.TransportUnavailable("AppToApp bridge bind failed: …")`.

## Package registry (placeholders — confirm with terminal vendor)

The actual upstream package name is **OEM-specific**. Pinelabs ships
the same Messenger IPC under different package coordinates depending
on the terminal model and OEM contract. The placeholders below
illustrate the shape; **your terminal vendor MUST confirm the exact
value before you ship to production**.

| OEM / variant | Placeholder package | Status |
|---|---|---|
| Pinelabs MasterApp (default) | `com.pinelabs.masterapp` | most common — verify |
| Pinelabs OEM alias 1 | `com.pinelabs.aliasone` | placeholder — confirm |
| Pinelabs OEM alias 2 | `com.pinelabs.aliastwo` | placeholder — confirm |

## How to discover the actual package name

On the target terminal, plug in via ADB and list installed Pinelabs
packages:

```bash
adb shell pm list packages | grep -i pine
```

The output is the source of truth for that specific device. Cross-
reference with your Pinelabs onboarding contact — the vendor's
distribution channel ties an APK build to a specific package name.

## Manifest snippet template

Once you have the confirmed name, declare it in
`app/src/main/AndroidManifest.xml`:

```xml
<queries>
    <package android:name="com.pinelabs.masterapp" />
    <!-- Add additional <package> entries if your fleet spans
         multiple OEM variants. -->
</queries>
```

## Diagnostic flow

If `bindService` returns false (visible as
`SdkError.TransportUnavailable`):

1. **First**, suspect a missing `<queries>` entry. This is the most
   common cause on Android 11+ even when the package IS installed.
2. Confirm the package is installed:
   `adb shell pm list packages | grep -i pine`.
3. Confirm the value in your manifest matches the installed package
   name verbatim.
4. Only after the above, suspect application-id provisioning,
   service signature mismatch, or upstream service crash.

## Next docs

`languages/android/setup`, `languages/android/errors`, `transports`.
