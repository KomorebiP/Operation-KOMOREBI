# Literature and API boundary — v0.36

Date checked: 2026-09-12. This is primary-source/API checking, not a novelty survey.

1. Pinned Mathlib Order/KonigLemma.lean, theorem
   exists_seq_forall_proj_of_forall_finite. It requires finite base, nonempty levels,
   coherent projections and finite one-step fibres, not surjectivity. We apply it
   to the solution subtypes of actual finite coefficient levels. This is a formal
   application of a known theorem, not a new compactness principle.
2. Pinned Mathlib NumberTheory/Padics/RingHoms.lean and inherited v0.35
   PadicMatrixTowerLimit.lean. The inherited construction forms actual PadicInt
   entries and inverse entries, proves reduction specifications and extensionality.
   The new proof supplies a compatible family without assuming uniqueness.

Public API locations checked:
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Order/KonigLemma.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/NumberTheory/Padics/RingHoms.html

The exact compiler uses the pinned local source/cache, not unpinned online code.
No external arithmetic or automorphic theorem is imported in this new block.

[
  {
    "file": "Mathlib/Order/KonigLemma.lean",
    "sha256": "9b98944059a89436f8307fcbc40e969025092b393af9157009bbf01c42384f57",
    "mathlib_revision": "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"
  },
  {
    "file": "Mathlib/NumberTheory/Padics/RingHoms.lean",
    "sha256": "93ba84a94f41b266b73aaaab58a34982d0cb61cfb5bea592d05cb01ab31113c6",
    "mathlib_revision": "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"
  }
]
