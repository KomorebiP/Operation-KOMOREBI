# External inputs and terminology

## Formal dependencies

The accepted modules use the recovered Lean 4.34.0-rc2 toolchain and matching Std.
The two imported project sources are pinned in `source_records/LINEAGE.json`.
No Mathlib theorem, quantifier-elimination result, compactness theorem, or external
model-theory assertion is assumed by the new formal proofs.

Lean/Std provides ordinary logic, dependent inductive types, lists, finite types,
quotients, and arithmetic proof machinery. The dependency audit records only
`propext`, `Classical.choice`, and `Quot.sound`.

## Primary documentation consulted on 2026-09-21

- Mathlib.ModelTheory.Syntax:
  https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Syntax.html
  Consulted definitions of terms, formulas, state equality, and well-scoped bound
  variables. This existing syntax is NOT imported or claimed to be newly invented.
- Mathlib.ModelTheory.Types:
  https://leanprover-community.github.io/mathlib4_docs/Mathlib/ModelTheory/Types.html
  Consulted for the distinction between model-theoretic types and this release's
  deliberately restricted observational formula family.

These are documentation references, not load-bearing theorem imports. Their web
content was read, not retained as source cache artifacts; no cached-content hash
or exact checked translation to their APIs is claimed. Online docs may change.

## Attribution and scope

Observation equivalence, truth preservation proved by formula induction, finite
partition refinement, and type-definability versus finite definability are existing
logical ideas. This release contributes a scoped integration and proofs for the
Komorebi semantic interface. No literature-novelty or priority verdict is made.
The initial generality of the brainstorm is corrected by explicit counterexamples,
not by asserting that these foundational concepts are new.
