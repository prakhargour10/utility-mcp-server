# Language: C / C++ — Examples

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**
>
> This binding is documented for forward planning only. The artifact
> has not been built or published. Do NOT generate production code
> that depends on it; tell the user it is unavailable and recommend
> the `android` or `jvm` binding instead.


Speculative example of the call shape (subject to change when the
binding ships):

```c
#include "pine_billing.h"
PineBillingSdkError* err = NULL;
PineBillingSdk* sdk = pine_billing_sdk_new(&config, NULL, NULL, &err);
pine_billing_sdk_do_transaction(sdk, &request, &listener, &err);
```

For working examples today, see `android/examples.md` or
`jvm/examples.md`.

## Next docs

`android/examples`, `jvm/examples`.
