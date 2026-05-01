# Language: JVM — Examples

> **AI INSTRUCTIONS:** The Java examples below MUST use the Kotlin `Unsigned` helper — UniFFI's `UInt` / `ULong` types are not directly constructible from Java.

## Full doTransaction example — Kotlin

```kotlin
package com.merchant.pos

import uniffi.pine_billing.*
import java.util.concurrent.Executors
import java.util.concurrent.CountDownLatch

fun main() {
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
    PineBillingSdk(config, null, null).use { sdk ->
        val request = TransactionRequest(
            amount = 19_900uL,
            currency = "INR",
            billingRefNo = "INV-2025-001",
            invoiceNo = "INV-2025-001",
            transactionType = TransactionType.SALE,
            originalEventId = null,
            referenceId = "order-abc",
            metadata = null,
            merchantId = System.getenv("MERCHANT_ID"),
            terminalId = System.getenv("TERMINAL_ID"),
            allowedPaymentModes = null,
            transportOptions = TransportOptions.Cloud(CloudTransactionOptions(
                merchantId = System.getenv("MERCHANT_ID"),
                securityToken = System.getenv("CLOUD_SECURITY_TOKEN"),
                identity = CloudIdentity.Imei("STORE-POS-001", "353…"),
                transactionNumber = "T-001",
                sequenceNumber = "1",
                allowedPaymentMode = "10",
                totalInvoiceAmount = "19900",
                txnType = 1,
                originalPlutusTransactionReferenceId = null,
                autoCancelDurationMinutes = 5u,
            )),
        )

        val done = CountDownLatch(1)
        val listener = object : TransactionListener {
            override fun onStarted(eventId: String) {
                println("started $eventId")
            }
            override fun onSuccess(result: TransactionResult) {
                println("ok ${result.eventId} status=${result.status}")
                done.countDown()
            }
            override fun onFailure(error: SdkException) {
                println("fail ${error::class.simpleName}: ${error.message}")
                done.countDown()
            }
        }

        Executors.newSingleThreadExecutor().execute {
            try { sdk.doTransaction(request, listener) }
            catch (e: SdkException) {
                println("rejected: ${e.message}")
                done.countDown()
            }
        }
        done.await()
    }
}
```

## Full doTransaction example — Java

> Requires the `com.merchant.pos.Unsigned` Kotlin helper from
> `jvm/setup.md` § 5.

```java
package com.merchant.pos;

import static com.merchant.pos.Unsigned.toUInt;
import static com.merchant.pos.Unsigned.toULong;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import uniffi.pine_billing.*;

public final class Main {

    public static void main(String[] args) throws Exception {
        SdkConfig config = new SdkConfig(
            toUInt(60_000L), null, TransportType.CLOUD, null, null,
            new CloudConfig(
                CloudType.ISM,
                System.getenv("CLOUD_BASE_URL"),
                toUInt(5_000L), toUInt(245_000L)
            ),
            null
        );

        try (PineBillingSdk sdk = new PineBillingSdk(config, null, null)) {
            TransactionRequest request = new TransactionRequest(
                toULong(19_900L), "INR", "INV-2025-001", "INV-2025-001",
                TransactionType.SALE, null, "order-abc", null,
                System.getenv("MERCHANT_ID"), System.getenv("TERMINAL_ID"),
                null,
                new TransportOptions.Cloud(new CloudTransactionOptions(
                    System.getenv("MERCHANT_ID"),
                    System.getenv("CLOUD_SECURITY_TOKEN"),
                    new CloudIdentity.Imei("STORE-POS-001", "353…"),
                    "T-001", "1", "10", "19900", 1, null, toUInt(5L)
                ))
            );

            CountDownLatch done = new CountDownLatch(1);
            TransactionListener listener = new TransactionListener() {
                @Override public void onStarted(String eventId) { System.out.println("started " + eventId); }
                @Override public void onSuccess(TransactionResult result) {
                    System.out.println("ok " + result.getEventId());
                    done.countDown();
                }
                @Override public void onFailure(SdkException error) {
                    System.out.println("fail " + error.getClass().getSimpleName());
                    done.countDown();
                }
            };

            ExecutorService pool = Executors.newSingleThreadExecutor();
            pool.submit(() -> {
                try { sdk.doTransaction(request, listener); }
                catch (SdkException e) {
                    System.out.println("rejected: " + e.getMessage());
                    done.countDown();
                }
                return null;
            });
            done.await();
            pool.shutdown();
        }
    }
}
```

## Running

```bash
# Compile (assuming all jars are in lib/):
javac -cp "lib/*" -d out src/main/java/com/merchant/pos/*.java
kotlinc -cp "lib/*" -d out src/main/kotlin/com/merchant/pos/*.kt

# Run with java -cp (NOT java -jar — there is no Main-Class manifest).
java -cp "out:lib/pine-billing-sdk-0.5.0-preview.2.jar:lib/jna-5.14.0.jar:lib/kotlin-stdlib-1.9.22.jar:lib/annotations-24.1.0.jar" \
     com.merchant.pos.Main
```

## Next docs

`jvm/errors`, `jvm/distribution`, `apis/do_transaction`,
`models/SdkConfig`.
