# External mathematical and software inputs — v0.4

The new theorems reuse standard finite algebra, exact finite linear combinations,
and the existing project first-order syntax bridge. They do not claim invention
of those ingredients. Actual pinned source hashes are in
`new_evidence/BATCH_STATE.json` under runtime_hashes and
`new_evidence/ENVIRONMENT.json`.

- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- `Mathlib/GroupTheory/Coset/Card.lean`: subgroup cardinal divides ambient cardinal,
  used for the actual additive subgroup of a submodule. Primary documentation:
  https://leanprover-community.github.io/mathlib4_docs/Mathlib/GroupTheory/Coset/Card.html
- `Mathlib/LinearAlgebra/Finsupp/LinearCombination.lean`:
  `Submodule.mem_span_range_iff_exists_fun` for a finite indexed generator family,
  used to justify the executable tuple oracle. Primary documentation:
  https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/Finsupp/LinearCombination.html
- `Mathlib/Data/Nat/Log.lean`, ZMod cardinality and prime-power divisor facts:
  rank = log_p of actual finite module cardinality, not a guessed linear dimension.
- Twelve unchanged local predecessor modules implement deterministic behavioral
  semantics, true row arithmetic, the observational fragment, and standard
  first-order translation. They are rebuilt as actual dependencies.

The pinned local source and compiled proof imports determine theorem hypotheses.
The live documentation links are locators, not substitutions for those pins.
The upstream cache is reused, not a source rebuild of the entire library.
