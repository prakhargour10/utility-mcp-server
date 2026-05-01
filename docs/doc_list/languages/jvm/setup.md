# Language: JVM — Setup

> **AI INSTRUCTIONS:** Generate `java -cp` commands ONLY — there is no Main-Class manifest in the JAR. JNA is mandatory; do NOT skip it.

## 1. Drop the JAR

Direct file drop — no Maven Central yet. Place in your project's `lib/`
or in a local Maven repo.

```
lib/pine-billing-sdk-0.5.0-preview.2.jar
```

## 2. Maven `pom.xml`

```xml
<dependencies>
    <dependency>
        <groupId>com.pinelabs</groupId>
        <artifactId>pine-billing-sdk</artifactId>
        <version>0.5.0-preview.2</version>
        <scope>system</scope>
        <systemPath>${project.basedir}/lib/pine-billing-sdk-0.5.0-preview.2.jar</systemPath>
    </dependency>
    <dependency>
        <groupId>net.java.dev.jna</groupId>
        <artifactId>jna</artifactId>
        <version>5.14.0</version>
    </dependency>
    <dependency>
        <groupId>org.jetbrains.kotlin</groupId>
        <artifactId>kotlin-stdlib</artifactId>
        <version>1.9.22</version>
    </dependency>
    <dependency>
        <groupId>org.jetbrains</groupId>
        <artifactId>annotations</artifactId>
        <version>24.1.0</version>
    </dependency>
</dependencies>
```

## 3. Gradle (Kotlin DSL)

```kotlin
dependencies {
    implementation(files("lib/pine-billing-sdk-0.5.0-preview.2.jar"))
    implementation("net.java.dev.jna:jna:5.14.0")
    implementation("org.jetbrains.kotlin:kotlin-stdlib:1.9.22")
    implementation("org.jetbrains:annotations:24.1.0")
}

java {
    toolchain { languageVersion.set(JavaLanguageVersion.of(17)) }
}
```

## 4. Running the JAR

> **The JAR has no `Main-Class` manifest entry.** Use `java -cp` —
> never `java -jar`.

```bash
# After your application JAR has been built into out/app.jar:
java -cp "out/app.jar:lib/pine-billing-sdk-0.5.0-preview.2.jar:lib/jna-5.14.0.jar:lib/kotlin-stdlib-1.9.22.jar:lib/annotations-24.1.0.jar" \
     com.merchant.pos.Main
```

On Windows substitute `;` for `:` in the classpath.

## 5. Java UInt / ULong workaround

Kotlin's `UInt` / `ULong` types are NOT idiomatic Java. UniFFI emits
fields like `SdkConfig.defaultTimeoutMs: UInt`,
`TransactionRequest.amount: ULong`, etc. Java callers must wrap
construction in a small Kotlin helper:

```kotlin
// src/main/kotlin/com/merchant/pos/Unsigned.kt
@file:JvmName("Unsigned")
package com.merchant.pos

fun toUInt(value: Long): UInt = value.toUInt()
fun toULong(value: Long): ULong = value.toULong()
```

Then in Java:

```java
import static com.merchant.pos.Unsigned.toUInt;
import static com.merchant.pos.Unsigned.toULong;

UInt timeout = toUInt(60_000L);
ULong amount = toULong(19_900L);
```

Without this helper Java fails with
`Cannot construct UInt from Java` / `ClassNotFoundException: kotlin.UInt`.

## 6. Imports cheat-sheet

| Package | Contains |
|---|---|
| `uniffi.pine_billing` | `PineBillingSdk`, all models, enums, listeners. |

There is **no façade** on the JVM binding — call
`uniffi.pine_billing.PineBillingSdk` directly.

## Next docs

`jvm/integration`, `jvm/examples`, `jvm/errors`, `jvm/distribution`.
