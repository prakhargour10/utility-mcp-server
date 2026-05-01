# Language: C

> **AI INSTRUCTIONS:** Use this file when TARGET_LANGUAGE = `c`. The C binding is the lowest-level surface, exposed via UniFFI's C scaffolding.

## Distribution

- **Header:** `pine_billing.h`
- **Library:** `libpine_billing_sdk.so` (Linux) / `.dylib` (macOS) / `.dll` + `.lib` (Windows)
- **ABI:** stable per-minor-version; do not link against intermediate dev builds
- **Download:** `get_sdk(artifact_key="c-<platform>")`

## Environment requirements

| Item | Required |
|---|---|
| C compiler | C11 (gcc 9+, clang 12+, MSVC 2019+) |
| Build system | CMake 3.20+ or plain Makefile |
| Linker | dynamic linking against the shared lib only |

## CMake integration

```cmake
add_library(pine_billing_sdk SHARED IMPORTED)
set_target_properties(pine_billing_sdk PROPERTIES
    IMPORTED_LOCATION "${CMAKE_SOURCE_DIR}/third_party/libpine_billing_sdk.so"
    INTERFACE_INCLUDE_DIRECTORIES "${CMAKE_SOURCE_DIR}/third_party/include"
)
target_link_libraries(my_app PRIVATE pine_billing_sdk)
```

## Memory ownership

- All `*` pointers returned by SDK functions are heap-allocated by the SDK.
- Free them with the matching `pine_billing_*_free` function declared in the header.
- String fields are null-terminated UTF-8.
- Never `free()` SDK-allocated memory with `free()` — always use the SDK's free function.

## SDK construction

```c
#include "pine_billing.h"

PineBillingSdkError* err = NULL;
PineBillingSdkConfig config = {
    .default_timeout_ms = 60000,
    .transport = PINE_TRANSPORT_CLOUD,
    .cloud = &(PineBillingCloudConfig){
        .type = PINE_CLOUD_TYPE_ISM,
        .base_url = "https://api.pinelabs.example",
        .connect_timeout_ms = 5000,
        .read_timeout_ms = 245000,
    },
};
PineBillingSdk* sdk = pine_billing_sdk_new(&config, NULL, NULL, &err);
if (err) { /* dispatch by err->variant; then pine_billing_error_free(err); */ }
```

## Threading

- Listener callbacks are invoked on an SDK worker thread.
- Implementations MUST be reentrant and MUST NOT block.
- The SDK does not call `signal()` or set process-global state.

## Code-generation directives

- Always check the trailing `err` out-pointer; it is non-NULL on failure even when the return value looks valid.
- Pair every `pine_billing_*_new`/`*_clone` with the matching `*_free`. Never leak.
- Use opaque structs as opaque — do not read fields not documented in the header.

## Next docs

- Concepts: `lifecycle`, `error-handling`.
- APIs: `constructor`, `do_transaction`, `cancel`, `check_status`.
- Models: `SdkConfig`, `SdkError`, `TransactionRequest`, `TransactionResult`.
