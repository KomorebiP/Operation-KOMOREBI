# Paper VI — fifth checked formalization block

Author: Komorebi P. · 6 September 2026 · v0.5.0

**Both remaining scoped results are complete: memory/self-energy (13.2) and canonical holomorphic naturality (15.1). The ledger now contains 33 complete results, zero partial results and zero pending results.** The three separately stated conjectures remain open.

| Count | Fourth checked block | This release |
|---|---:|---:|
| Explicit Lean theorem declarations | 310 | 341 |
| Proof modules | 42 | 47 |
| Complete manuscript results | 31 | 33 |
| Partial manuscript results | 2 | 0 |
| Namespace declarations audited | 710 | 782 |

The 31 additional supporting theorem declarations close two existing manuscript results. Namespace declarations also include definitions and generated auxiliaries. These counts concern Paper VI only.

## Fresh verification

The full root project builds with Lean 4.34.0-rc2, strict implicit-variable settings and warnings treated as errors. All explicit theorem targets and all project namespace declarations pass the real axiom audit; only `propext`, `Classical.choice`, and `Quot.sound` are allowed. Mathlib remains pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; all nine locked dependency revisions and their tracked-source cleanliness are checked. All 54 companion tests and six verifier controls pass again.

The authoritative report is `verification/verification_status.json`, supported by `lean_build.log` and `lean_axiom_audit.log`. It records `lean_kernel_checked: true` and `all_scoped_results_complete: true`. The broader `full_paper_formalized` flag remains false: it does not certify every prose sentence, figure or open conjecture. Prose-to-Lean correspondence is manually reviewed. The existing ordinary real/complex specializations, including complexification, remain disclosed mathematical specializations rather than separately counted Lean constructions.

## 13.2 — arbitrary finite nonnormal memory

`ScalarDecay` proves actual Bochner integrability and convergence to zero of complex exponential-polynomial terms under a negative real-part condition.

`NonnormalMemory` applies the generalized-eigenspace decomposition to left multiplication by the hidden generator on its finite-dimensional complex matrix algebra. The nilpotent tail vanishes, so the actual exponential has a finite component expansion. Nonzero components have eigenvalues in the original algebra spectrum. The stated strict spectral half-plane therefore gives integrability and a zero limit, without a supplied exponential-growth bound or a normality assumption.

The improper-integral fundamental theorem is applied to both derivative identities of the shifted exponential. This derives both inverse equations and identifies the integral with the actual inverse. `MatrixMemory.rectangular_memory_self_energy` then carries the integral through the literal rectangular transfer matrices and proves

`integral exp(-z*t) • (U * exp(t*A) * V) = U * (z*I - A)^(-1) * V`.

The matrix dimensions are arbitrary, including zero dimensions. The result allows nonnormal hidden generators and all nilpotent Jordan parts. The manuscript now supplies this argument instead of simply invoking the Laplace identity.

## 15.1 — canonical holomorphic matrix functions

`CanonicalJets` constructs the unique basis-free linear operator whose action on each generalized eigenspace is the finite Taylor jet. It proves that increasing the cutoff does not change this action, that an intertwiner carries each generalized eigenspace into its counterpart, and that the canonical operators intertwine even when the two dimensions differ.

`HolomorphicFinite` proves uniqueness, dependence only on the spectral jets, and the Cauchy integral formula for every local coefficient. Every declared open holomorphic neighborhood supplies admissible positive-radius closed discs around its spectral points. Their circle integrals yield the canonical coefficients, independently of the chosen radii. The final theorem is the literal rectangular matrix identity `C * F(A) = F(B) * C`.

The manuscript now explicitly uses this standard finite Taylor-jet definition of the holomorphic matrix function. This completes the theorem through a canonical construction; it does not assume that a supplied contour expression already represents `F(A)`. Disconnected neighborhoods, unequal dimensions and nilpotent Jordan parts are included. Arbitrary-contour deformation theory for general Banach algebras is outside the finite-matrix statement and is not claimed.

## Manuscript and preserved scope

The two proofs are expanded and the finite holomorphic calculus is defined explicitly. The theorem statements retain their full finite-dimensional scope. All 33 theorem-like records and the three open conjectures are retained, as is authorship Komorebi P. Earlier corrections and the fractional-operator scope explanations remain in place.

The numerical code and 19 figure pairs are unchanged. The 54 tests were rerun. The first-block 79-field numerical comparison and regenerated figures remain historical evidence; the numerical study was not repeated in this block. PDF rendering, numbering, warnings and final hashes are recorded in `verification/pdf_validation.json`.

The previous PDF and ZIP save failure was repaired during this work. The preserved fourth-block files were saved successfully before the final edition was produced. Final deliverables use regular workspace files so their bytes are available for transfer.

## Reproduction

Use the exact toolchain in `formalization/lean/lean-toolchain` and preserve `lake-manifest.json`. Obtain the dependencies and Mathlib cache, then run `lake build KomorebiPaperVI` and `lake env lean -DwarningAsError=true KernelAudit.lean`. The complete gate is `python3 verification/verify.py` with the companion Python requirements and `lake` available. Missing Lean is a verification failure, not a pass.

The producing runtime adapter is documented under `verification/runtime`; compiler, kernel and dependency sources are unchanged. The original supplied edition and earlier checked ledgers, audit evidence and reviews are preserved under `provenance`. The source archive excludes dependency caches and build products and includes its own hash manifest. Credit and licensing for the inherited adapted Mathlib integral proof remain in `THIRD_PARTY_NOTICES.md`.
