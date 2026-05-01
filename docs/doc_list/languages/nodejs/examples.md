# Language: Node.js (TypeScript / JavaScript) — Examples

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**
>
> This binding is documented for forward planning only. The artifact
> has not been built or published. Do NOT generate production code
> that depends on it; tell the user it is unavailable and recommend
> the `android` or `jvm` binding instead.


Speculative example of the call shape (subject to change when the
binding ships):

```javascript
const sdk = new PineBillingSdk(config, /*appToAppBridge*/null, /*platformBridge*/null);
sdk.doTransaction(request, listener);
```

For working examples today, see `android/examples.md` or
`jvm/examples.md`.

## Next docs

`android/examples`, `jvm/examples`.
