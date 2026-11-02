# Quantum and Circuits

[Browse hub](../BROWSE.md) / [Books and companion volumes](../browse/MONOGRAPHS.md)

<a id="work-navigation"></a>

[Read](#read) · [Written proofs](#written-proofs) · [Lean](#lean) · [Code](#code) · [Evidence](#evidence) · [Worked examples](#worked-examples-for-this-work)

**Completion:** Reading edition complete · **Lean:** Selected results recorded · **Confidence:** Recorded formal evidence

Quantum models, channel interfaces, and circuit constructions.

## Before you start

**Suggested background:** Complex vectors and matrices, orthogonal projectors, and finite Fourier transforms for the arithmetic and symmetry parts; linear algebra and explicit gate costs for the catalytic part; Boolean functions and polynomials over the binary field for the circuit part. The introductory measurement example below offers a shorter starting point.

**Recorded results and limits:** Complete 344-page publication with explicit open research. 211 named declarations across thirteen formal modules cover selected arithmetic/circuit developments, not the full book.

**Remaining work:** Map the remaining ordinary-proof chapters and open physical targets separately from the thirteen checked modules.

The background advice is an editorial starting point. The work itself states its prerequisites and hypotheses.

[Reading routes](../READING_ROUTES.md) · [Glossary](../GLOSSARY.md) · [Claim links](../CLAIM_LINKS.md#monographs-quantum-and-circuits) · [Download this work](../DOWNLOADS.md#monographs-quantum-and-circuits)

### A route through the volume

The book asks what a change of representation makes accessible, and what it costs to reach, update, and reconstruct that representation. Its four treatments use distinct models.

| Treatment | Chapters | Question to follow |
|---|---|---|
| Arithmetic realizations | 1–2 | How does an arithmetic selector become a Fourier projector and a normalized quantum state? Begin with the twelve-dimensional example. |
| Symmetry collapse | 3–7 | When do invariant packets and moving frames give an accessible simulation? Track coordinate, update, and measurement costs alongside dimension. |
| Catalytic gate set distortion | 8–12 | Can temporarily leaving a restricted gate model reduce cost while restoring the required boundary state? Keep the gate alphabet and resource convention fixed. |
| Circuit obstructions | 13–21 | What do restoration, safe discrepancy covers, and projection imply within the stated circuit and linear-summary models? |

Start with chapters 1–2, then choose the treatment closest to your question. Appendices A–F give the formal and computational companions, claim coverage, and verification boundaries. The glossary and collected references follow them.

### Read with the evidence

The recorded formal inventory has **96 arithmetic declarations and 115 circuit declarations across thirteen modules**. These include supporting statements. They cover selected developments; the symmetry and catalytic treatments retain their written arguments and bounded computational evidence.

For circuits, the formal companion covers C01, the sharing-aware degree dependency, and the numerical C02 bound. Read the maintained claim register for C03–C08 and their written or finite evidence. Universal efficient quantum simulation, unrestricted circuit hardness, and the wider catalytic synthesis questions remain open in this edition.

[Formal replay requirements and exact coverage](../../monographs/quantum-and-circuits/release_tools/README.md) · [Current circuit claim register](../../monographs/quantum-and-circuits/sources/circuits/Komorebi_Circuit_Obstructions_Research_Edition_1.0/source/komorebi-circuit-obstructions-v1.2.0/docs/CLAIMS.md)

### Try the arithmetic phase example

Follow [the modulus-12 calculation](../demonstrations/QUANTUM_PHASE_MEASUREMENT.md#10-the-collections-modulus-12-phase-example), then [change the phase in the browser](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#physics-arithmetic-phase). Compare coherent sign replacement with coordinate dephasing. The [exact Python program](../../examples/quantum_phase_measurement.py) reproduces this finite teaching example using the standard library; it does not run Lean.

### Worked examples for this work

These introductory calculations lead into this work’s subject. The source and evidence links below retain the work’s recorded scope.

- [17. Calculate quantum measurement and dephasing](../examples/17_QUANTUM_MEASUREMENT.md) · [Terms and source routes](../LEARNING_MAP.md#quantum-measurement)

**Complete demonstration with runnable code:** [Quantum phase, measurement, and information loss](../demonstrations/QUANTUM_PHASE_MEASUREMENT.md).

Use the links below to read this work and its supporting files. Ctrl+click (Command+click on macOS) opens a link in another tab. Your browser’s Back button returns here.

## Read

- [Read online: complete volume, appendices, proofs and sources](https://KomorebiP.github.io/Operation-KOMOREBI/read/monographs-quantum-and-circuits/index.html)
- [Edition README](../../monographs/quantum-and-circuits/README.md)
- [Read PDF](../../monographs/quantum-and-circuits/volume/output/Realization_Calculus_Quantum_and_Circuits.pdf)
- [Visual guide (PDF)](../../monographs/quantum-and-circuits/sources/quantum/Quantum_Arithmetic_Complete_Release/output/Komorebi_Quantum_Arithmetic_Visual_Guide.pdf)

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Written proofs

Find the statement number or section in the [reading files](#read), then read its assumptions and argument. A claim map may cover only part of the written result.

- [Manuscript text (TeX)](../../monographs/quantum-and-circuits/volume/volume.tex)
- [Current circuit claim register (C01–C08)](../../monographs/quantum-and-circuits/sources/circuits/Komorebi_Circuit_Obstructions_Research_Edition_1.0/source/komorebi-circuit-obstructions-v1.2.0/docs/CLAIMS.md)
- [Historical circuit claim register (preserved companion)](../../monographs/quantum-and-circuits/sources/circuits/Komorebi_Circuit_Obstructions_Research_Edition_1.0/historical_companion/Komorebi_Theorem_Companion_Source/source_snapshot/docs/CLAIMS.md)

[Find this work among other written proofs](../browse/PROOFS.md#monographs-quantum-and-circuits)

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Lean

Start with the [edition guide](../../monographs/quantum-and-circuits/README.md) and the build instructions below. Check the correspondence records to see which written claims the Lean declarations cover. Source links lead to `.lean` files. PDF guides explain the formalization.

- [Formal replay: setup, pinned runtime, and coverage](../../monographs/quantum-and-circuits/release_tools/README.md)
- [Lean guide (PDF)](../../monographs/quantum-and-circuits/sources/quantum/Quantum_Arithmetic_Complete_Release/output/Komorebi_Quantum_Arithmetic_Lean_Guide.pdf)
- [Quantum Lean source snapshot](../../monographs/quantum-and-circuits/verification/quantum_fresh_20261026/fresh/)
- [Circuit Lean source snapshot](../../monographs/quantum-and-circuits/verification/circuits_fresh_20261026/fresh_source/)
- [Current circuit claim register (C01–C08)](../../monographs/quantum-and-circuits/sources/circuits/Komorebi_Circuit_Obstructions_Research_Edition_1.0/source/komorebi-circuit-obstructions-v1.2.0/docs/CLAIMS.md)
- [Historical circuit claim register (preserved companion)](../../monographs/quantum-and-circuits/sources/circuits/Komorebi_Circuit_Obstructions_Research_Edition_1.0/historical_companion/Komorebi_Theorem_Companion_Source/source_snapshot/docs/CLAIMS.md)

[Find this work among other Lean projects](../browse/LEAN.md#monographs-quantum-and-circuits)

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Code

These links include code, examples, checks, or build tools. Read the [edition guide](../../monographs/quantum-and-circuits/README.md) for setup instructions and what each command does. All software is beta and work in progress.

- [Portable formal replay wrapper (requires the external Lean kit)](../../monographs/quantum-and-circuits/release_tools/replay_formal.py)
- [Symmetry packet implementation and exact checks](../../monographs/quantum-and-circuits/sources/symmetry/Symmetry_Collapse_in_Quantum_Computation_Source/code/)
- [Catalytic gate atlas: mathematical modules](../../monographs/quantum-and-circuits/sources/catalytic/Catalytic_Gate_Set_Distortion_Monograph_Source/code/catalytic_gate_atlas/)
- [Circuit scientific replay (Python and C++17)](../../monographs/quantum-and-circuits/sources/circuits/Komorebi_Circuit_Obstructions_Research_Edition_1.0/source/komorebi-circuit-obstructions-v1.2.0/scripts/verify.py)

[Find this work among other code projects](../browse/CODE.md#monographs-quantum-and-circuits)

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Evidence

- [Completion, Lean coverage, confidence, and cited evidence](../STATUS_CATALOG.md#monographs-quantum-and-circuits)
- [Source-file receipt (identity and availability)](../../manifests/source-imports/monographs-quantum-and-circuits.json)
- [All files in this source edition](../../monographs/quantum-and-circuits/)

The evidence records describe the reviews and runs completed for this edition.

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Continue browsing

- [Previous: Machine Native Reasoning](monographs-machine-native-reasoning.md)
- [Next: Physics](monographs-physics.md)
- [Back to Books and companion volumes](../browse/MONOGRAPHS.md#contents)
- [All collections](../BROWSE.md)
