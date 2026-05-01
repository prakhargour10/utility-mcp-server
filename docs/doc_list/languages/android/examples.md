# Android — Examples (Pine Billing SDK 0.5.0-preview.2)

> **AI INSTRUCTIONS:** Compose-by-default. Always disable the trigger control on `onStarted` and re-enable on a terminal-state callback. Always marshal to `Dispatchers.Main` before touching UI from inside listener callbacks.

## Compose: a Sale screen

```kotlin
package com.merchant.pos

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import com.pinelabs.billing.sdk.PineBillingSdk
import uniffi.pine_billing.*

class CheckoutViewModel(app: android.app.Application) : AndroidViewModel(app) {
    private val sdk: PineBillingSdk get() = (getApplication<PineBillingApp>()).sdk

    var inFlight by mutableStateOf(false); private set
    var lastResult by mutableStateOf<TransactionResult?>(null); private set
    var lastError by mutableStateOf<String?>(null); private set

    fun startSale(amountPaise: ULong, invoice: String) {
        if (inFlight) return
        inFlight = true; lastResult = null; lastError = null
        val request = TransactionRequest(
            amount = amountPaise,
            currency = "INR",
            billingRefNo = invoice,
            invoiceNo = invoice,
            transactionType = TransactionType.SALE,
            originalEventId = null,
            referenceId = null,
            metadata = null,
            merchantId = null,
            terminalId = null,
            allowedPaymentModes = null,
            transportOptions = null,
        )
        viewModelScope.launch(Dispatchers.IO) {
            try {
                sdk.doTransaction(request, object : TransactionListener {
                    override fun onStarted(eventId: String) {
                        // Persist eventId BEFORE returning. Synchronous Room writes are safe here.
                    }
                    override fun onSuccess(result: TransactionResult) {
                        viewModelScope.launch(Dispatchers.Main) {
                            lastResult = result; inFlight = false
                        }
                    }
                    override fun onFailure(error: SdkException) {
                        viewModelScope.launch(Dispatchers.Main) {
                            lastError = error.message ?: error::class.simpleName
                            inFlight = false
                        }
                    }
                })
            } catch (e: SdkException) {
                withContext(Dispatchers.Main) {
                    lastError = e.message ?: e::class.simpleName
                    inFlight = false
                }
            }
        }
    }
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                val vm: CheckoutViewModel = viewModel()
                Column(Modifier.padding(24.dp)) {
                    Text("POS Checkout", style = MaterialTheme.typography.headlineSmall)
                    Spacer(Modifier.height(16.dp))
                    Button(
                        enabled = !vm.inFlight,
                        onClick = { vm.startSale(amountPaise = 19_900uL, invoice = "INV-001") },
                    ) { Text(if (vm.inFlight) "Awaiting terminal…" else "Charge ₹199.00") }

                    vm.lastResult?.let { r ->
                        Spacer(Modifier.height(24.dp))
                        Text("Status: ${r.status}")
                        r.transactionId?.let { Text("Txn id: $it") }
                        r.maskedPan?.let { Text("PAN: $it") }      // debug only — never INFO
                        r.amount?.let { Text("Amount: $it") }
                    }
                    vm.lastError?.let { Text("Error: $it") }
                }
            }
        }
    }
}
```

### Populated `TransactionResult` fields, by transport (Sale / Success)

| Field | AppToApp | Cloud | PADController |
|---|---|---|---|
| `event_id` | ✓ SDK uuid | ✓ SDK uuid | ✓ SDK uuid |
| `status` | ✓ | ✓ (`Pending` possible) | ✓ |
| `transaction_id` | ✓ acquirer ref | ✓ `PlutusTransactionReferenceID` | ✓ when echoed |
| `approval_code` | ✓ when present | ✓ when present | ✓ when present |
| `masked_pan` | ✓ when present | ✓ when present | ✓ when present |
| `card_brand` | ✓ when present | ✓ when present | ✓ when present |
| `payment_mode` | ✓ when present | ✓ when present | ✓ when present |
| `amount` | ✓ paise | ⚠ unit best-effort — see Notes | ✓ paise |
| `terminal_response_code` | ✓ on failure | ✓ on failure | ✓ on failure |
| `failure_detail` | ✓ on failure | ✓ on failure | ✓ on failure |
| `cloud` (`CloudTransactionData`) | ✗ | ✓ when echoed | ✗ |

> **Note (Cloud `amount`):** the upstream Cloud response sometimes returns the amount as the original wire string. The SDK best-effort-parses it back to paise; if the upstream field is malformed the SDK leaves `amount = null` and exposes the raw value via `cloud.raw_response`. Never trust `result.amount` for reconciliation on Cloud — use the merchant's own books.

## Java sample (Sale)

```java
package com.merchant.pos;

import com.pinelabs.billing.sdk.PineBillingSdk;
import uniffi.pine_billing.*;

public final class SaleJava {
    public static void start(PineBillingSdk sdk, String invoice) {
        TransactionRequest req = new TransactionRequest(
            Unsigned.toULong(19_900L),
            "INR", invoice, invoice,
            TransactionType.SALE,
            null, null, null, null, null, null, null
        );
        sdk.doTransaction(req, new TransactionListener() {
            @Override public void onStarted(String eventId) { /* persist */ }
            @Override public void onSuccess(TransactionResult result) { /* finalise order */ }
            @Override public void onFailure(SdkException error) { /* dispatch */ }
        });
    }
}
```

> Java samples require the `Unsigned` helper (`com.merchant.pos.Unsigned`). See `integration.md` § "Java interop".

## Cloud `cancel` / `check_status`

```kotlin
val cancelOpts = CancelOptions.Cloud(CloudCancelOptions(
    merchantId = "MID-12345",
    securityToken = BuildConfig.CLOUD_TOKEN,
    identity = CloudIdentity.Imei(storeId = "STORE-1", imei = "353000000000000"),
    amount = "19900",                              // string, paise
))
sdk.cancel(plutusTxnRefId, cancelOpts)             // event_id == TransactionResult.transaction_id

val statusOpts = CheckStatusOptions.Cloud(CloudCheckStatusOptions(
    merchantId = "MID-12345",
    securityToken = BuildConfig.CLOUD_TOKEN,
    identity = CloudIdentity.Imei(storeId = "STORE-1", imei = "353000000000000"),
))
val status = sdk.checkStatus(plutusTxnRefId, statusOpts)
```

## PADController `restart`

```kotlin
val sdk = PineBillingSdk(
    context, config, AndroidSystemBridge(context)   // platformBridge required for restart
)
withContext(Dispatchers.IO) { sdk.restart() }
```
