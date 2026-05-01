# JVM — Examples (Pine Billing SDK 0.5.0-preview.2)

## Cloud Sale (Kotlin)

```kotlin
import uniffi.pine_billing.*

fun runSale(sdk: PineBillingSdk) {
    val txnOpts = TransportOptions.Cloud(CloudTransactionOptions(
        merchantId = "MID-12345",
        securityToken = System.getenv("CLOUD_TOKEN"),
        identity = CloudIdentity.Imei(storeId = "STORE-1", imei = "353000000000000"),
        transactionNumber = "TX-001",
        sequenceNumber = "1",
        allowedPaymentMode = "ALL",
        totalInvoiceAmount = "19900",
        txnType = "SALE",
        autoCancelDurationMinutes = 5u,
    ))
    val request = TransactionRequest(
        amount = 19_900uL,
        currency = "INR",
        billingRefNo = "INV-001",
        invoiceNo = "INV-001",
        transactionType = TransactionType.SALE,
        originalEventId = null,
        referenceId = null,
        metadata = null,
        merchantId = null,
        terminalId = null,
        allowedPaymentModes = null,
        transportOptions = txnOpts,
    )
    sdk.doTransaction(request, object : TransactionListener {
        override fun onStarted(eventId: String) { /* persist */ }
        override fun onSuccess(result: TransactionResult) { /* finalise */ }
        override fun onFailure(error: SdkException) { /* dispatch */ }
    })
}
```

## Cloud Sale (Java)

> Java samples require `Unsigned` (`com.merchant.pos.Unsigned`). See `setup.md` § 5.

```java
import uniffi.pine_billing.*;
import com.merchant.pos.Unsigned;

public final class Sale {
    public static void run(PineBillingSdk sdk) {
        TransportOptions txnOpts = new TransportOptions.Cloud(new CloudTransactionOptions(
            "MID-12345",
            System.getenv("CLOUD_TOKEN"),
            new CloudIdentity.Imei("STORE-1", "353000000000000"),
            "TX-001", "1", "ALL", "19900", "SALE",
            Unsigned.toUInt(5L)
        ));
        TransactionRequest req = new TransactionRequest(
            Unsigned.toULong(19_900L), "INR", "INV-001", "INV-001",
            TransactionType.SALE, null, null, null, null, null, null, txnOpts
        );
        sdk.doTransaction(req, new TransactionListener() {
            @Override public void onStarted(String eventId) { }
            @Override public void onSuccess(TransactionResult result) { }
            @Override public void onFailure(SdkException e) { }
        });
    }
}
```
