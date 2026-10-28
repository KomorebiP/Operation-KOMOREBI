# Research software

**All software is beta and work in progress.** Each component documents its supported inputs, dependencies, and qualification scope.

The [corrected SRIC admission 0.3.3 source edition](sric-admission-v0.3.3/README.md) includes bounded admission and CLI regression checks. It remains a prototype; real-model execution is pending.

## Independent libraries

| Library | Purpose |
|---|---|
| [Komorebi Math](https://github.com/KomorebiP/komorebi-math) | Python objects and algorithms for finite operator systems, packets, coordinates, signals, arithmetic, and certificates. |
| [Polyphase Float](https://github.com/KomorebiP/polyphase-float) | C arithmetic with explicit precision and rounding, constant computation, and selected special functions. |

## Packages in this collection

| Package | Purpose | Files |
|---|---|---|
| [AM-SPD](komorebi-am-spd/) | Finite image decomposition and reconstruction with retained residuals. | [Open edition](komorebi-am-spd/) |
| [Quadratic-Form Engine / K-COS](../papers/quadratic-form-kcos/) | The earlier mathematical companion and numerical engine. | [Open edition](../papers/quadratic-form-kcos/) |
| [Certified Inference](../docs/works/certified-inference.md) | A finite certified-inference core with executable Lean sources and worked constructions. | [Lean](certified-inference/Komorebi/) · [Code](certified-inference/checks/) · [Work page](../docs/works/certified-inference.md) |
| [Constructive Repair](../docs/works/constructive-repair.md) | Constructive repairs, examples, and the accompanying reference implementation. | [PDF](constructive-repair/monograph/Constructive_Repair.pdf) · [Text](constructive-repair/monograph/Constructive_Repair.tex) · [Lean](constructive-repair/lean/) · [Code](constructive-repair/python/komorebi_repair/) · [Work page](../docs/works/constructive-repair.md) |
| [RRCT](../docs/works/packages-rrct.md) | The v0.60 persistent fuzzy J-Space bridge implementation. | [Code](rrct/src/) · [Work page](../docs/works/packages-rrct.md) |
| [Universal Generative Deformation Calculus](../docs/works/universal-generative-deformation.md) | A reference Python package, examples, tests, and editable mathematical manuscript. | [PDF](universal-generative-deformation/paper/Universal_Generative_Deformation_Calculus.pdf) · [Text](universal-generative-deformation/paper/Universal_Generative_Deformation_Calculus.tex) · [Code](universal-generative-deformation/generative_deformation/) · [Work page](../docs/works/universal-generative-deformation.md) |
| [Large Signal Model software](../docs/works/large-signal-model.md) | Imported source material; scientific scope, completion, and proof or experiment evidence still need assessment. | [PDF](large-signal-model/paper/Projector_Resolved_Large_Algebraic_Signal_Model.pdf) · [Text](large-signal-model/paper/Projector_Resolved_Large_Algebraic_Signal_Model.tex) · [Code](large-signal-model/src/) · [Work page](../docs/works/large-signal-model.md) |

Additional implementations accompany the [research programs](../research/README.md) and [experimental laboratories](../experiments/README.md). Their software has the same beta / work-in-progress status.

Use a component's documented installation and examples. A mathematical result in an accompanying paper does not expand the tested platform, numerical range, or supported input contract of its software.

[Software guide](../docs/LIBRARIES.md) · [Collection](../README.md)
