# Resolution Semantics

[Browse hub](../BROWSE.md) / [Research programs](../browse/RESEARCH.md)

<a id="work-navigation"></a>

[Read](#read) · [Written proofs](#written-proofs) · [Lean](#lean) · [Code](#code) · [Evidence](#evidence)

**Completion:** Active development · **Lean:** Selected results recorded · **Confidence:** Recorded formal evidence

Active development with automatic checked finite-graph traversal and reconstruction, exact counts with arbitrary vertex pins, and the inherited two-world obstruction. Rank formulas, sparse forest/complexity results and wider transport and forcing claims remain open.

## Before you start

**Suggested background:** Read the problem statement, recorded scope and open questions first. The program's definitions determine its subject prerequisites.

**Recorded results and limits:** The separate Lean 4.24.0 companion checks 216 theorem declarations. It retains binary graph reconstruction, exact unpinned/partial-pin counts and the supplied-traversal solver. A new automatic constructor computes actual component indices and root walks using a checked indexed path table; every reachable pair is covered after n rounds on Fin n. The automatic solver is sound and complete for arbitrary proposed binary edge fields and pins, without caller-supplied traversals or assignment enumeration. Fifteen inherited sources are unchanged, and both two-world obstruction theorems remain axiom-free. Rank formulas, sparse forest/complexity results and wider transport/forcing claims remain outside this formal scope.

**Remaining work:** Formalize the rank formulas n-c and m-n+c. Develop a verified sparse spanning-forest implementation and state any proved complexity bounds. Preserve the reference solver, original source and earlier companions.

The background advice is an editorial starting point. The work itself states its prerequisites and hypotheses.

[Reading routes](../READING_ROUTES.md) · [Glossary](../GLOSSARY.md) · [Claim links](../CLAIM_LINKS.md#resolution-semantics) · [Download this work](../DOWNLOADS.md#resolution-semantics)

Use the links below to read this work and its supporting files. Ctrl+click (Command+click on macOS) opens a link in another tab. Your browser’s Back button returns here.

## Read

- [Edition README](../../research/resolution-semantics/README.md)
- [Read PDF](../../research/resolution-semantics/Komorebi_Resolution_Semantics.pdf)
- [Maintained edition guide](../components/RESOLUTION_SEMANTICS_LEAN.md)

[Back to work navigation](#work-navigation)

## Written proofs

Find the statement number or section in the [reading files](#read), then read its assumptions and argument. A claim map may cover only part of the written result.

- [Manuscript text (TeX)](../../research/resolution-semantics/Komorebi_Resolution_Semantics.tex)

[Find this work among other written proofs](../browse/PROOFS.md#resolution-semantics)

[Back to work navigation](#work-navigation)

## Lean

Start with the [maintained edition guide](../components/RESOLUTION_SEMANTICS_LEAN.md) and the build instructions below. Check the correspondence records to see which written claims the Lean declarations cover. Source links lead to `.lean` files. PDF guides explain the formalization.

- [Checked formal companion: source and reproduction](../../formal/resolution-semantics-v0.7.0/README.md)
- [Preserved original edition: Lean sources (directory)](../../research/resolution-semantics/formal/)

[Find this work among other Lean projects](../browse/LEAN.md#resolution-semantics)

[Back to work navigation](#work-navigation)

## Code

These links include code, examples, checks, or build tools. Read the [maintained edition guide](../components/RESOLUTION_SEMANTICS_LEAN.md) for setup instructions and what each command does. All software is beta and work in progress.

- [Code / scripts: checks](../../research/resolution-semantics/checks/)

[Find this work among other code projects](../browse/CODE.md#resolution-semantics)

[Back to work navigation](#work-navigation)

## Evidence

- [Completion, Lean coverage, confidence, and cited evidence](../STATUS_CATALOG.md#resolution-semantics)
- [Separate Lean companion replay and scope](../../verification/resolution-semantics/automatic-windows-2026-11-01-run1/receipt.json)
- [Source-file receipt (identity and availability)](../../manifests/source-imports/resolution-semantics.json)
- [All files in this source edition](../../research/resolution-semantics/)

The evidence records describe the reviews and runs completed for this edition.

[Back to work navigation](#work-navigation)

## Continue browsing

- [Previous: Prime-Contact Coherence Calculus](prime-contact-coherence.md)
- [Next: Seeded Two-Axis Calculus](seeded-two-axis.md)
- [Back to Research programs](../browse/RESEARCH.md#contents)
- [All collections](../BROWSE.md)
