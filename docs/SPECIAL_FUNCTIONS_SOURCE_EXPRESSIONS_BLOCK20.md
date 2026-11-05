# Special Functions: source execution and arithmetic interpretation

**Recorded checkpoint: SF-LEAN-B20, 4 November 2026.**

The new companions connect exact evaluation metadata, source execution and
arithmetic interpretation to the canonical coupled special functions.
There are 536 registered theorem names: 39 inherited finite-core names and
497 across the coupled companions. Counts include supporting lemmas and do
not measure whole-book formalization or independent discoveries.

## Three linked steps

| Companion | What is checked | Record |
|---|---|---|
| Block18: typed evaluation result | Metadata, N+1 retained coefficients, exponent 2N+3, both real intervals and complex disk error | [Report](../monographs/special-functions/formalization/Block18/REPORT.md) |
| Block19: source-bound imperative refinement | Separate arrays, guarded loop/reverse fold, exact seven-field dictionary, modeled errors, raw conversion front end, totality and determinism in the model | [Report](../monographs/special-functions/formalization/Block19/REPORT.md) |
| Block20: typed expression interpretation | Selected source arithmetic is interpreted in Lean and checked against the separately lowered operations for all values in its source-variable profiles | [Report](../monographs/special-functions/formalization/Block20/REPORT.md) |

Block18 adds 17 named theorems, Block19 adds 35 and Block20 adds 19. The
Block20 replay passes 29 stages with three fresh compilations/kernel replays,
19 theorem axiom audits, ten expression mutation controls, the retained binder
controls and five expected Lean rejections. Earlier modules retain their
source/object/receipt-checked evidence; Mathlib is cached. Review is author
self-review and replay uses the same kernel. This reading guide performs no
new Lean execution.

## Inspect and reproduce

[Open the Lean source inspector](https://KomorebiP.github.io/Operation-KOMOREBI/lean/monographs-special-functions/index.html)
or start with [the formal source index](SPECIAL_FUNCTIONS_FORMAL_SOURCES.md).
The new [expression interpreter](../monographs/special-functions/lean/CoupledExpressionSemantics.lean),
[source expression data](../monographs/special-functions/lean/CoupledSourceExpressions.lean)
and [lowering proof](../monographs/special-functions/lean/CoupledExpressionRefinement.lean)
are selected with their local imports and audit files.

[Claim map](../monographs/special-functions/formalization/Block20/CLAIM_MAP.json)
· [Replay receipt](../monographs/special-functions/formalization/Block20/evidence/receipt.json)
· [Publication inventory](../monographs/special-functions/formalization/Block20/PUBLICATION_MANIFEST.json)

The native replay command and dependency pins are in the companion report.
Source inspection, native replay and browser import availability are separate
capabilities; the inspector does not promise that every Mathlib import is
available in the browser compiler.

## What remains conditional

Actual Python correctness still assumes a faithful AST parser/source-data
extractor, the fixed statement/control template and standard integer/Fraction,
container, type-tag and library semantics. The selected arithmetic lowering
is kernel-checked; the entire Python translator, CPython and library internals
are not verified. Unexpected machine failures and side-effectful custom
objects remain outside the mathematical execution model.

The next structural task is to formalize the remaining statement/control
fragment or verify AST extraction. Other J/F/H, I and A-E obligations remain;
ordinary type convergence stays conditional and G.2 retains its nonzero-defect
guard. The current books and original calculator are unchanged.

[Work and evidence](works/monographs-special-functions.md)
· [Special Functions reading hub](SPECIAL_FUNCTIONS.md)
· [Maintained continuation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/monographs/special-functions/current/CONTINUE_HERE.md)
