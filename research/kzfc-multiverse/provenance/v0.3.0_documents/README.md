# Komorebi KZFC Residual Reflection v0.3.0

A checked continuation of v0.2.0. The development now contains 65 theorem declarations, including 38 added in this block. These counts include auxiliary and interface lemmas, not 65 independent research results.

## Results of this block

1. A concrete integer-tower obstruction is nonzero globally and restricts to zero in every finite-prefix cokernel.
2. Every finite set of the equations `a(n) - 3 a(n+1) = 1` has an integer solution, but the full countable system does not.
3. For a specified test system that permits finite prefixes or the whole countable tower, `KRRAt κ` holds exactly when `aleph0 < κ`.
4. Uniform arithmetic classification: for every natural `m >= 2` and integer `c`, a sequence solving `a(n) - m a(n+1) = c` exists exactly when `m - 1` divides `c`.
5. A fine kappa-complete ultrafilter on the small subsets of the constraint index set implies fixed-domain compactness when the value domain and each constraint scope have size below kappa. Ultrafilter existence is an explicit premise.
6. The interface audit separates soundness from completeness, proves the correct direction of depth monotonicity, and shows how unrestricted reindexing can hide depth inside the piece label.

## Essential corrections to the earlier discussion

Allowing more residual depths weakens the witness assertion for fixed data. Non-flattenability in the old, fixed residual system does not prove independence from ZFC or prevent another encoding. A nonzero global derived obstruction need not have a finite-support witness. These corrections change the interpretation, not the validity of the predecessor theorem proofs.

## Proof boundary

No new axiom of set theory is proved or assumed. No relative-consistency or strong-compactness equivalence theorem is claimed. The cokernel is constructed explicitly. Its identification with the first derived inverse limit is supported by an external mathematical theorem, not yet formalized against Mathlib's right-derived functor.

## Verification

See `verification/RESULTS.json`, `verification/clean_build.log`, and `verification/axiom_audit.log`. The reproducible verifier performs a clean project build, re-elaborates every active source with warnings treated as errors, checks the axiom dependency allowlist, checks source integrity, and demands rejection of both a false proof and an intentional placeholder.

Pinned environment: Lean 4.34.0-rc2 and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Dependencies and the compiler are not bundled in this source archive.

Start with `THEORY.md`, `PROOF_BOUNDARY.md`, and `REPRODUCE.md`. The next block is specified in `CONTINUE_HERE.md`.
