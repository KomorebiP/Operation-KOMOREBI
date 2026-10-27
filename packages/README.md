# Research software

**All software is beta and work in progress.** Each component documents its supported inputs, dependencies, and qualification scope.

The [corrected SRIC admission 0.3.3 source edition](sric-admission-v0.3.3/README.md) includes bounded admission and CLI regression checks. It remains a prototype; real-model execution is pending.

## Independent libraries

| Library | Purpose |
|---|---|
| [Komorebi Math](https://github.com/KomorebiP/komorebi-math) | Python objects and algorithms for finite operator systems, packets, coordinates, signals, arithmetic, and certificates. |
| [Polyphase Float](https://github.com/KomorebiP/polyphase-float) | C arithmetic with explicit precision and rounding, constant computation, and selected special functions. |

## Packages in this collection

| Package | Purpose |
|---|---|
| [AM-SPD](komorebi-am-spd/) | Finite image decomposition and reconstruction with retained residuals. |
| [Quadratic-Form Engine / K-COS](../papers/quadratic-form-kcos/) | The earlier mathematical companion and numerical engine. |
| [Certified Inference](certified-inference/) | A finite certified-inference core with executable Lean sources and worked constructions. |
| [Constructive Repair](../docs/components/CONSTRUCTIVE_REPAIR.md) | Constructive repairs, examples, and the accompanying reference implementation. |
| [RRCT](rrct/) | The v0.60 persistent fuzzy J-Space bridge implementation. |
| [Universal Generative Deformation Calculus](universal-generative-deformation/) | A reference Python package, examples, tests, and editable mathematical manuscript. |
| [Large Signal Model software](large-signal-model/) | Imported source material; scientific scope, completion, and proof or experiment evidence still need assessment. |

Additional implementations accompany the [research programs](../research/README.md) and [experimental laboratories](../experiments/README.md). Their software has the same beta / work-in-progress status.

Use a component's documented installation and examples. A mathematical result in an accompanying paper does not expand the tested platform, numerical range, or supported input contract of its software.

[Software guide](../docs/LIBRARIES.md) · [Collection](../README.md)
