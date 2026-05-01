# Language: iOS (Swift / Objective-C) — Examples

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**
>
> This binding is documented for forward planning only. The artifact
> has not been built or published. Do NOT generate production code
> that depends on it; tell the user it is unavailable and recommend
> the `android` or `jvm` binding instead.


Speculative example of the call shape (subject to change when the
binding ships):

```swift
let sdk = try PineBillingSdk(config: config, appToAppBridge: nil, platformBridge: nil)
try sdk.doTransaction(request: request, listener: MyListener())
```

For working examples today, see `android/examples.md` or
`jvm/examples.md`.

## Next docs

`android/examples`, `jvm/examples`.
