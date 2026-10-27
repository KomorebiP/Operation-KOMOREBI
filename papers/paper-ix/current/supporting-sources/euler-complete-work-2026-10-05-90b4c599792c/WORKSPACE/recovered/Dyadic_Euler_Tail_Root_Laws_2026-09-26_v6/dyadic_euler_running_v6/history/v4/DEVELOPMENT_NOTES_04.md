# Development and provenance — continuation 04

## Mathematical correction

The v3 inequality delta>2d_i was a sufficient strong-Hensel condition. Describing it as an exact root-emergence threshold was not justified. No counterexample to the implication was found; the sharpness interpretation was the error.

The v4 separating-ball argument replaces that interpretation. At a regular wall, the exact threshold is delta>=d_i+k_i, with a proved no-root statement below it. For j=5, the sharp stages are 3,4,6, not the earlier sufficient stages 3,5,7.

At j=17 the lower perturbation is not a unit (its reduction is 1+X). Applying the regular-wall necessity statement there would be invalid. That family is handled by its own finite coefficient certificates and the general eventual-separation theorem.

## Computation and environment

The ZIP had no readable extracted text through the file reader. Its mounted bytes were therefore inspected and extracted with Python/container tools. The original archive was not edited.

An optional probe for the `flint` Python module failed with `ModuleNotFoundError`. The new implementation does not require it. Exact modular Bernoulli computation uses a derived distribution identity and Python's standard-library integers and fractions.

No assertion failure or timeout occurred in the retained v4 scientific audit. Historical v3 timeout records remain in `DEVELOPMENT_FAILURES_03.md`; they are not newly executed v4 failures.

One primary-source lookup for a separate Strassmann note was unavailable; the argument used here does not depend on that missing note. Accessible NIST Bernoulli references and Keith Conrad's Hensel/Weierstrass notes were read. The factorization is also proved constructively in the current note.

The computation-audit manifest validator was readable through the supplied skill resource but was not mounted as a filesystem script. Its implementation was transcribed into `support/validate_manifest.py` and executed on the v4 manifest with output hashes checked. A separate pass checked the input hashes recorded under `mathematics.inputs`.

The manifest is schema version 1. It records run metadata and actual hashes but does not have a version-2 bounded-runner trace, machine-checkable resource caps, or a Git revision. No such provenance is implied by a passing validation.

## Evidence boundary

The fresh v4 checker, result JSON, and manifest constitute the new execution record. Older notes and logs are preserved as inherited artifacts, not universally re-certified. The original tail checks use a formula distinct from the factorized polynomial evaluator; both modular paths use a Bernoulli routine separately tested against exact rational recurrence and finite power sums.

No Lean compilation, theorem-prover acceptance, or historical novelty review was performed. The finite-degree reduction at arbitrary r is proved, but no universal simple-root assertion or unconditional finite-precision multiple-root decision algorithm is claimed.
