# Pinned primary dependencies

The source and compiled-object audit uses the exact Mathlib revision:

    aeb72f1e9981b6d35b426b16dca7759be3e7ba06

The principal classical ring-decomposition source is:

    https://raw.githubusercontent.com/leanprover-community/mathlib4/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/RingTheory/SimpleModule/WedderburnArtin.lean

Main dependency declarations integrated in the manuscript correspondence:

- `IsSemisimpleRing.exists_ringEquiv_pi_matrix_divisionRing`
- `IsSemisimpleModule.exists_linearEquiv_fin_dfinsupp`

The compatible natural-factor module construction is new source in `PaperICompletion8.ProductPresentation` and `PaperICompletion8.SemisimpleExistence`. Its uses of simple-module embeddings and Schur bijectivity are visible in those proof bodies and the printed public types/proofs.

Official kernel implementation, at the pinned compiler revision:

    https://raw.githubusercontent.com/leanprover/lean4/6a10ac8c22beadecabdbb0919c2b50214762f91d/src/Lean/Environment.lean

Runtime helper classification is inherited unchanged from the accepted Block 07 audit. Whole-closure replay uses the pinned official kernel API, not a new independent proof kernel. Actual runtime-file hashes, compiler version and all nine dependency Git revisions are checked in the execution receipt rather than inferred from these links.
