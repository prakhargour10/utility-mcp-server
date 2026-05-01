# Concept: binding-aliases

> **AI INSTRUCTIONS:** When the user requests docs by language name, resolve to the binding directory using the alias table below.

## Why aliases exist

The MCP `get_documentation_list` endpoint accepts a few short language
names that don't match this bundle's binding directories one-for-one.
The most common collision is **Kotlin**, which can mean either
"Kotlin on Android (the Pinelabs PoS device case)" or "Kotlin on the
desktop / server JVM".

The vast majority of Kotlin requests originate from Android merchant
apps integrating against a Pinelabs terminal. Backend-Kotlin
developers (Ktor, Spring, microservices) are a minority but a real
audience. Resolving naively to one or the other gets the wrong
content most of the time, so we alias explicitly.

## Alias table

| User-supplied name | Resolves to | Notes |
|---|---|---|
| `kotlin` | `languages/android/` | Default: Kotlin on Android. Most callers. |
| `kotlin-android`, `android-kotlin`, `android` | `languages/android/` | Explicit Android. |
| `kotlin-jvm`, `kotlin-desktop`, `kotlin-server`, `jvm` | `languages/jvm/` | Desktop / server JVM. |
| `java` | `languages/jvm/` | Java is JVM-only in this bundle (Android Java callers should pass `android` and use the Java samples there). |
| `java-android`, `android-java` | `languages/android/` | Java on Android. |
| `swift`, `ios`, `objective-c`, `objc` | `languages/ios/` | Roadmap. |
| `python`, `py` | `languages/python/` | Roadmap. |
| `node`, `nodejs`, `js`, `javascript`, `typescript`, `ts` | `languages/nodejs/` | Roadmap. |
| `c`, `cpp`, `c++` | `languages/c/` | Roadmap. |

## Backend Kotlin disambiguation

Backend Kotlin developers MUST explicitly request `kotlin-jvm` or
`jvm`. A bare `kotlin` request returns Android docs.

## Next docs

`overview`, `versioning-and-support`.
