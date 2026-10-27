# External and project sources for v0.28.0

The new proofs rely on the actual pinned local mathlib source, particularly Mathlib/Data/Matrix/Mul.lean and Mathlib/Data/Matrix/Basic.lean at aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

Public primary documentation consulted: https://leanprover-community.github.io/mathlib4_docs/Mathlib/Data/Matrix/Mul.html (accessed September 13, 2026). It documents mulVec, mulVec_add, mulVec_mulVec, basis-column evaluation and matrix extensionality. The moving public docs do not substitute for the compiled pinned source.

The project baseline is AVOC_Formal_v0.27.0.zip, SHA-256 1a297f2532feb962462f302a5ec10462b5e923d8c6cbf6bc4425771a90596f67. Its 7,409 internal listed hashes passed before changes. The new version preserves its non-audit mathematical modules byte-for-byte.

Affine composition and basis determination are standard mathematics. The contribution here is the checked AVOC implementation/extension and its explicit typed, cost and execution boundaries, not a historical priority claim.
