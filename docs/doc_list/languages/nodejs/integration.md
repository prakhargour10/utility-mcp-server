# Language: Node.js (TypeScript / JavaScript) — Integration

> ⚠️ **ROADMAP — NOT SHIPPING IN 0.5.0-preview.2**
>
> This binding is documented for forward planning only. The artifact
> has not been built or published. Do NOT generate production code
> that depends on it; tell the user it is unavailable and recommend
> the `android` or `jvm` binding instead.


The integration patterns will mirror the Android / JVM bindings:

* construct one `PineBillingSdk` per process,
* dispatch blocking calls off the platform UI thread,
* never block inside listener callbacks.

## Next docs

`android/integration`, `jvm/integration`, `concepts/threading`.
