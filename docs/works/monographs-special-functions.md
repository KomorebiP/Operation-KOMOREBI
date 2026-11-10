# Special Functions

[Browse hub](../BROWSE.md) / [Books and companion volumes](../browse/MONOGRAPHS.md)

<a id="work-navigation"></a>

[Read](#read) · [Written proofs](#written-proofs) · [Lean](#lean) · [Code](#code) · [Evidence](#evidence) · [Worked examples](#worked-examples-for-this-work)

**Completion:** Reading edition complete · **Lean:** Selected results recorded · **Confidence:** Recorded formal evidence

Cyclic families, sequence constructions, reciprocal structure, and exact methods.

## Before you start

**Suggested background:** Begin with the introduction and glossary. Then use the volume's own definitions to identify the background needed for its subject.

**Recorded results and limits:** The proofread reading volumes are accompanied by 536 registered theorem names: 39 inherited finite-core names and 497 coupled-companion names. Blocks 18 to 20 prove typed evaluation results, a source-bound imperative model equivalent to the specification, and selected arithmetic lowering against a typed expression interpreter. Correctness of the Python implementation remains conditional on AST parsing and extraction, the fixed statement and control-flow template, and the semantics of the standard primitives. No verified general Python compiler or whole-book percentage is claimed. The remaining obligations in groups J, F, H, I, and A through E remain open. Ordinary type convergence remains conditional.

**Remaining work:** Formalize the remaining statement and control-flow fragment or verify the AST extraction boundary. Retain explicit assumptions about the parser, Python, Fraction, and the libraries, along with the remaining obligations in groups J, F, H, I, and A through E.

The background advice is an editorial starting point. The work itself states its prerequisites and hypotheses.

[Reading routes](../READING_ROUTES.md) · [Glossary](../GLOSSARY.md) · [Claim links](../CLAIM_LINKS.md#monographs-special-functions) · [Download this work](../DOWNLOADS.md#monographs-special-functions)

### Worked examples for this work

These introductory calculations lead into this work’s subject. The source and evidence links below retain the work’s recorded scope.

- [24. Calculate coefficients of contracted feedback](../examples/24_CONTRACTED_FEEDBACK.md) · [Terms and source routes](../LEARNING_MAP.md#contracted-feedback)

**Complete demonstration with runnable code:** [Komorebi sequence shapes](../demonstrations/SEQUENCE_SHAPES.md) · [Stirling, Bell, and Fubini](../demonstrations/STIRLING_BELL_FUBINI.md).

### Explore Special Functions

[Books, five families, and the coupled-function lab](../SPECIAL_FUNCTIONS.md)

[Guided reading](https://KomorebiP.github.io/Operation-KOMOREBI/read/monographs-special-functions/start.html) · [Expanded visual lessons](https://KomorebiP.github.io/Operation-KOMOREBI/read/monographs-special-functions/atlas/index.html) · [Interactive coupled-function laboratory](https://KomorebiP.github.io/Operation-KOMOREBI/special-functions-lab.html)

Use the links below to read this work and its supporting files. Ctrl+click (Command+click on macOS) opens a link in another tab. Your browser’s Back button returns here.

## Read

- [Read online: chapters, proof appendices, figures and glossary](https://KomorebiP.github.io/Operation-KOMOREBI/read/monographs-special-functions/index.html)
- [Edition README](../../monographs/special-functions/README.md)
- [Read PDF](../../monographs/special-functions/books/Special_Functions.pdf)
- [Expanded Visual Guide (current PDF)](../../monographs/special-functions/books/Expanded_Visual_Guide.pdf)
- [Resolution and Coupled Atlas (current PDF)](../../monographs/special-functions/books/Resolution_and_Coupled_Atlas.pdf)
- [Packet Realization Core and correction register (PDF)](../../monographs/special-functions/series/Komorebi_Special_Functions_Consolidated_Manuscript_v0.1.pdf)
- [Original Series Collected Reader (PDF)](../../monographs/special-functions/series/Komorebi_Special_Functions_Complete_Reader_v0.1.pdf)
- [Earlier visual guide (historical PDF)](../../monographs/special-functions/research/visual_guide.pdf)
- [Rights and reuse](../../monographs/special-functions/RIGHTS_AND_REUSE.md)

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Written proofs

Find the statement number or section in the [reading files](#read), then read its assumptions and argument. A claim map may cover only part of the written result.

- [Manuscript text (TeX)](../../monographs/special-functions/monograph/main.tex)
- [Proof map and appendices (TeX)](../../monographs/special-functions/monograph/sections/proof_map.tex)
- [Coupled formal claim map](../../monographs/special-functions/formalization/Block01/CLAIM_MAP.json)
- [Block17 claim map](../../monographs/special-functions/formalization/Block17/CLAIM_MAP.json)
- [Block17 recorded execution receipt](../../monographs/special-functions/formalization/Block17/evidence/receipt.json)
- [Block17 source publication inventory](../../monographs/special-functions/formalization/Block17/SOURCE_MANIFEST.json)
- [Block20 claim map](../../monographs/special-functions/formalization/Block20/CLAIM_MAP.json)
- [Block20 recorded replay](../../monographs/special-functions/formalization/Block20/evidence/receipt.json)
- [Blocks18-20 reader publication inventory](../../monographs/special-functions/formalization/Block20/PUBLICATION_MANIFEST.json)

[Find this work among other written proofs](../browse/PROOFS.md#monographs-special-functions)

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Lean

Start with the [edition guide](../../monographs/special-functions/README.md) and the build instructions below. Check the correspondence records to see which written claims the Lean declarations cover. Source links lead to `.lean` files. PDF guides explain the formalization.

- [Current formalization checkpoint and continuation](../../monographs/special-functions/current/README.md)
- [Block20 source-expression scope and recorded replay](../../monographs/special-functions/formalization/Block20/REPORT.md)
- [Historical Block01 formal status](../../monographs/special-functions/LEAN_STATUS.md)
- [Block01 recurrence companion report](../../monographs/special-functions/formalization/Block01/REPORT.md)
- [Finite core and coupled Lean sources (directory)](../../monographs/special-functions/lean/)
- [Coupled recurrence, local convergence and recovery (Lean)](../../monographs/special-functions/lean/CoupledFormal.lean)
- [Coupled formal claim map](../../monographs/special-functions/formalization/Block01/CLAIM_MAP.json)
- [Block17 claim map](../../monographs/special-functions/formalization/Block17/CLAIM_MAP.json)
- [Block17 recorded execution receipt](../../monographs/special-functions/formalization/Block17/evidence/receipt.json)
- [Block17 source publication inventory](../../monographs/special-functions/formalization/Block17/SOURCE_MANIFEST.json)
- [Typed evaluation result (Lean)](../../monographs/special-functions/lean/CoupledEvaluationResult.lean)
- [Source-bound imperative model (Lean)](../../monographs/special-functions/lean/CoupledPythonSource.lean)
- [Imperative refinement (Lean)](../../monographs/special-functions/lean/CoupledPythonRefinement.lean)
- [Typed expression interpreter (Lean)](../../monographs/special-functions/lean/CoupledExpressionSemantics.lean)
- [Source-derived expression data (Lean)](../../monographs/special-functions/lean/CoupledSourceExpressions.lean)
- [Expression lowering and enclosure composition (Lean)](../../monographs/special-functions/lean/CoupledExpressionRefinement.lean)
- [Block20 claim map](../../monographs/special-functions/formalization/Block20/CLAIM_MAP.json)
- [Block20 recorded replay](../../monographs/special-functions/formalization/Block20/evidence/receipt.json)
- [Blocks18-20 reader publication inventory](../../monographs/special-functions/formalization/Block20/PUBLICATION_MANIFEST.json)

[Find this work among other Lean projects](../browse/LEAN.md#monographs-special-functions)

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Code

These links include code, examples, checks, or build tools. Read the [edition guide](../../monographs/special-functions/README.md) for setup instructions and what each command does. All software is beta and work in progress.

- [Code / scripts: tools](../../monographs/special-functions/tools/)
- [Exact coupled-function regression (Python)](../../monographs/special-functions/tools/check_coupled_exact.py)

[Find this work among other code projects](../browse/CODE.md#monographs-special-functions)

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Evidence

- [Completion, Lean coverage, confidence, and cited evidence](../STATUS_CATALOG.md#monographs-special-functions)
- [Latest recorded written review](../SPECIAL_FUNCTIONS_SOURCE_EXPRESSIONS_BLOCK20.md)
- [Source-file receipt (identity and availability)](../../manifests/source-imports/monographs-special-functions.json)
- [All files in this source edition](../../monographs/special-functions/)

The evidence records describe the reviews and runs completed for this edition.

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Continue browsing

- [Previous: Large Signal Model](monographs-large-signal-model.md)
- [Next: Machine Societies](monographs-machine-societies.md)
- [Back to Books and companion volumes](../browse/MONOGRAPHS.md#contents)
- [All collections](../BROWSE.md)
