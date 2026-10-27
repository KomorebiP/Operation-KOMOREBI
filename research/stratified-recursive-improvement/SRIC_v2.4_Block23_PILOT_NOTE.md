# Block 23 Preserved Release-Hardening Note

The scientific disposition and acceptance thresholds remained fixed, but three release-integrity defects were found and corrected before final packaging.

## 1. Numerical oversubscription

Unrestricted BLAS threading caused an apparent stall during complete replay. Canonical entry points now pin OMP, OpenBLAS, MKL, and NumExpr thread counts to one unless the caller explicitly supplies a value.

## 2. Gauge-unstable receipts

Valid eigenspaces could be serialized with different eigenvector signs or different bases inside a repeated eigenspace. These outputs were mathematically equivalent but produced different cryptographic receipts. Block 23 now canonicalizes each selected subspace by projecting the ordered ambient coordinate axes into the subspace and applying deterministic Gram-Schmidt. Receipt floats are rounded to twelve decimal places and negative zero is normalized.

## 3. Hidden-coordinate leakage in the destructive-loss witness

An early destructive-loss fixture exposed one hidden intermediate semantic coordinate when constructing its collision witness. That violated the intended ontology-withholding boundary even though the final no-go conclusion was correct. The fixture was replaced before release. It now detects identical visible observations whose **externally protected future consequences** disagree, and it never gives the compiler a hidden intermediate coordinate.

After this correction:

- all 19 automated tests pass;
- all 36 final episodes replay exactly;
- the certificate matrix remains unchanged;
- every destructive episode contains 64 exact visible collisions;
- the minimum protected future-consequence gap is 1.736704;
- the final result receipt is `213bcf9fbf62b797f9903d9e05e84e5a4036bb02c927723a4570fa44e2c674ce`.

Two isolated builds of each PDF are byte-for-byte identical under the fixed source date. No semantic gate, threshold, or final certificate was weakened during hardening.
