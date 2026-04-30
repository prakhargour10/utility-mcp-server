# Language: Node.js

> **AI INSTRUCTIONS:** Use this file when TARGET_LANGUAGE = `nodejs`. Node bindings ship as a native addon with prebuilt binaries.

## Distribution

- **npm package:** `@pinelabs/pine-billing-sdk`
- **Binaries:** prebuilt for darwin-x64, darwin-arm64, linux-x64, linux-arm64, win32-x64
- **Module type:** CommonJS + ESM dual
- **Download:** `get_sdk(artifact_key="nodejs-npm")`

## Install

```bash
npm install @pinelabs/pine-billing-sdk
# or
yarn add @pinelabs/pine-billing-sdk
# or
pnpm add @pinelabs/pine-billing-sdk
```

If the install fails on a platform without a prebuilt binary, install the toolchain (Rust + cargo + clang/MSVC) and re-run `npm rebuild`.

## Environment requirements

| Item | Required |
|---|---|
| Node.js | 18 LTS or 20 LTS |
| Outbound HTTPS to `CLOUD_BASE_URL` | yes for Cloud |
| TypeScript (optional) | 5+ — `.d.ts` ships in package |

## SDK construction

```typescript
import {
  PineBillingSdk, SdkConfig, CloudConfig, CloudType, TransportType, LogLevel,
} from "@pinelabs/pine-billing-sdk";

const config: SdkConfig = {
  defaultTimeoutMs: 60_000,
  logLevel: LogLevel.Info,
  transport: TransportType.Cloud,
  cloud: {
    type: CloudType.Ism,
    baseUrl: "https://api.pinelabs.example",
    connectTimeoutMs: 5_000,
    readTimeoutMs: 245_000,
  } satisfies CloudConfig,
};

const sdk = new PineBillingSdk(config, /*appToAppBridge*/ null, /*platformBridge*/ null);
```

## Listeners

```typescript
sdk.doTransaction(req, {
  onStarted: (eventId) => { /* ... */ },
  onSuccess: (result) => { /* ... */ },
  onFailure: (err) => { /* ... */ },
});
```

Callbacks fire from a worker thread. If you build a Promise wrapper, ensure rejection on `onFailure` and resolution on `onSuccess`, and don't leak the listener.

## Code-generation directives

- Always include `import type` for `SdkError` and check via `instanceof SdkError` (the binding exports a discriminating class hierarchy).
- Never log `securityToken`, `transactionNumber`, full PAN, PIN.
- For Express / Fastify request handlers, wrap blocking calls in `await new Promise(resolve => setImmediate(resolve))` boundaries to avoid event-loop starvation.

## Next docs

- Concepts: `lifecycle`, `error-handling`.
- APIs: `do_transaction`, `cancel`, `check_status`.
- Models: `SdkConfig`, `CloudConfig`, `TransactionListener`, `TransactionRequest`.
