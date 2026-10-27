# Mathematical self-review: v0.7

Primary verdict for the written reductions: proved as written in the stated
positive-pivot integer / fixed-modulus setting, subject to the completed Lean
execution reported separately in RESULTS.md. This is a self-review, not an
independent researcher or referee audit.

| Obligation | Audit result | Evidence |
|---|---|---|
| Correct Euclidean sign convention | Passed | residue_coset; negative-tail kernel example |
| Exact lattice rather than saturation | Passed | integer reconstruction of the removed tail; lattice_normalize |
| Box uniqueness | Passed | leading difference is a pivot multiple strictly between -pivot and pivot; induction |
| Idempotent executable normalization | Passed | normalize_of_reduced; normalize_idempotent |
| Canonical basis for the same ambient lattice | Passed | reduced_unique; normalize_eq_iff_lattice_eq |
| Quotient by the column pivot, not row pivot | Passed | own-pivot clipping counterexample |
| Modulus kernel present in every tail | Passed | containsModulus_tail |
| Pivots divide the modulus | Passed | pivots_dvd_modulus |
| All stored normalized entries bounded | Passed | normalized_entry_bounds, including diagonal equality |
| Actual stateful loop preservation | Passed | normalizedRun_matches and normalizedRun_invariant |
| Same ordered result, not only same span | Passed | normalizedPrimeDiscover_eq_reference and eq_fast |
| All future outputs / original logical language | Passed within inherited fragment | normalizedPrimeDiscover_defines_behavior |
| General integer or composite modulus | Normalization and canonicalization covered | sufficient-fuel application remains prime-power |
| Zero dimension, trivial ring and fuel exhaustion | Passed | concrete examples and universal statements |
| Intermediate operands / end-to-end bit complexity | Not addressed by stored bound | explicit next obligation |
| Minimum modular or logical coordinates | Not asserted | triangular preimage has d auxiliary integer rows |
| Python / source translation correctness | Finite audit only | independent comparisons, not verified extraction |
| Historical novelty or broad discovery performance | Not asserted | standard arithmetic normalization; synthetic regressions |
