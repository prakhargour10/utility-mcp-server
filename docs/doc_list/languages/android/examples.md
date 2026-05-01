# Language: Android — Examples

> **AI INSTRUCTIONS:** Use the patterns below verbatim where possible. Do NOT swap the imports for `uniffi.pine_billing.PineBillingSdk` — Android merchants must use the `com.pinelabs.billing.sdk.PineBillingSdk` façade so the main-thread guard fires.

## Full doTransaction example — Kotlin

```kotlin
package com.merchant.pos

import android.content.Context
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.pinelabs.billing.sdk.PineBillingSdk
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import uniffi.pine_billing.AppToAppConfig
import uniffi.pine_billing.SdkConfig
import uniffi.pine_billing.SdkException
import uniffi.pine_billing.TransactionListener
import uniffi.pine_billing.TransactionRequest
import uniffi.pine_billing.TransactionResult
import uniffi.pine_billing.TransactionType
import uniffi.pine_billing.TransportType

class ChargeActivity : AppCompatActivity() {

    private val sdk: PineBillingSdk by lazy {
        PineBillingSdk(
            applicationContext,
            SdkConfig(
                defaultTimeoutMs = 60_000u,
                logLevel = null,
                transport = TransportType.APP_TO_APP,
                appToApp = AppToAppConfig(userId = "POS-USER", version = "1.0"),
                applicationId = BuildConfig.PINELABS_APP_ID,
                cloud = null,
                padController = null,
            ),
        )
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_charge)

        val charge = findViewById<Button>(R.id.charge)
        charge.setOnClickListener { onChargeClicked(charge) }
    }

    private fun onChargeClicked(button: Button) {
        button.isEnabled = false
        val request = TransactionRequest(
            amount = 19_900uL,
            currency = "INR",
            billingRefNo = "INV-2025-001",
            invoiceNo = "INV-2025-001",
            transactionType = TransactionType.SALE,
            originalEventId = null,
            referenceId = "order-${System.currentTimeMillis()}",
            metadata = null,
            merchantId = null,
            terminalId = null,
            allowedPaymentModes = null,
            transportOptions = null,
        )
        val listener = object : TransactionListener {
            override fun onStarted(eventId: String) {
                // Persist eventId against the merchant order id BEFORE returning.
            }
            override fun onSuccess(result: TransactionResult) {
                postToUi {
                    button.isEnabled = true
                    Toast.makeText(this@ChargeActivity,
                        "Charged: ${result.eventId}", Toast.LENGTH_LONG).show()
                }
            }
            override fun onFailure(error: SdkException) {
                postToUi {
                    button.isEnabled = true
                    Toast.makeText(this@ChargeActivity,
                        "Failed: ${error::class.simpleName}", Toast.LENGTH_LONG).show()
                }
            }
        }

        // CRITICAL: dispatch off the main thread; the façade's guard
        // throws IllegalStateException otherwise.
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                sdk.doTransaction(request, listener)
            } catch (e: SdkException) {
                postToUi {
                    button.isEnabled = true
                    Toast.makeText(this@ChargeActivity,
                        "Rejected: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    private fun postToUi(action: () -> Unit) =
        Handler(Looper.getMainLooper()).post(action)
}
```

## Full doTransaction example — Java

```java
package com.merchant.pos;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.Button;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.pinelabs.billing.sdk.PineBillingSdk;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import uniffi.pine_billing.AppToAppConfig;
import uniffi.pine_billing.SdkConfig;
import uniffi.pine_billing.SdkException;
import uniffi.pine_billing.TransactionListener;
import uniffi.pine_billing.TransactionRequest;
import uniffi.pine_billing.TransactionResult;
import uniffi.pine_billing.TransactionType;
import uniffi.pine_billing.TransportType;

public class ChargeActivity extends AppCompatActivity {

    private PineBillingSdk sdk;
    private final ExecutorService io = Executors.newSingleThreadExecutor();
    private final Handler main = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_charge);

        SdkConfig config = new SdkConfig(
            /*defaultTimeoutMs*/ kotlin.UInt.constructor-impl(60_000),
            /*logLevel*/ null,
            TransportType.APP_TO_APP,
            new AppToAppConfig("POS-USER", "1.0"),
            BuildConfig.PINELABS_APP_ID,
            /*cloud*/ null,
            /*padController*/ null
        );
        sdk = new PineBillingSdk(getApplicationContext(), config, /*platformBridge*/ null);

        Button charge = findViewById(R.id.charge);
        charge.setOnClickListener(v -> onChargeClicked(charge));
    }

    private void onChargeClicked(Button button) {
        button.setEnabled(false);
        TransactionRequest request = /* build TransactionRequest as in the Kotlin example */ null;
        TransactionListener listener = new TransactionListener() {
            @Override public void onStarted(String eventId) { /* persist */ }
            @Override public void onSuccess(TransactionResult result) {
                main.post(() -> {
                    button.setEnabled(true);
                    Toast.makeText(ChargeActivity.this,
                        "Charged: " + result.getEventId(), Toast.LENGTH_LONG).show();
                });
            }
            @Override public void onFailure(SdkException error) {
                main.post(() -> {
                    button.setEnabled(true);
                    Toast.makeText(ChargeActivity.this,
                        "Failed: " + error.getClass().getSimpleName(), Toast.LENGTH_LONG).show();
                });
            }
        };
        io.execute(() -> {
            try { sdk.doTransaction(request, listener); }
            catch (SdkException e) { /* main.post(...) */ }
        });
    }
}
```

> Java callers MUST construct unsigned values via Kotlin helpers — see
> `jvm/examples.md` for the full UInt/ULong workaround. The
> pseudo-construction `kotlin.UInt.constructor-impl` shown above is
> illustrative; in real code use a thin Kotlin helper file.

## Next docs

`android/errors`, `android/distribution`, `apis/do_transaction`.
