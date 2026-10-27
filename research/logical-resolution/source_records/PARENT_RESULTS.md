# Retained execution — Logical Resolution v0.1

## Lean

PASS: 8 library modules, 14 expected-outcome tasks,
73 named theorems (50 new),
132 named declarations. The final inner cold audit measured
6.876101 seconds. This is one execution measurement, not a
performance benchmark. Only Classical.choice, Quot.sound, propext occurred. Library warnings
are errors and every accepted input hash is unchanged. Three rejection controls
behaved as intended. Details: `results/LEAN_AUDIT.json` and `evidence/lean_cold/`.

## Finite Python audit

PASS: 38,077 check calls in 0.406497 seconds,
seed 2026092101, 28 finite systems. This is a finite audit, not
38,077 independent mathematical results.

| Check | Count |
|---|---:|
| arbitrary_delay_next_word | 24 |
| arbitrary_delay_same_prefix | 24 |
| bad_observation_transport | 1 |
| bfs_vs_partition | 4,911 |
| bounded_depth_quantifier_congruence | 7,509 |
| compiled_defining_formula | 4,911 |
| compiled_formula_quantifier_free | 28 |
| distinguishing_formula_negative | 4,374 |
| distinguishing_formula_positive | 4,374 |
| distinguishing_formula_rank_zero | 4,374 |
| existential_counterexample_source | 1 |
| existential_counterexample_target | 1 |
| full_equality_boundary | 1 |
| input_hashes_unchanged | 1 |
| invalid_transition_rejected | 1 |
| malformed_formula_rejected | 1 |
| nonsurjective_quantifier_transport_rejected | 1 |
| out_of_scope_variable_rejected | 1 |
| quantified_quotient_preservation | 7,509 |
| quotient_local_certificate | 28 |
| state_equality_not_in_fragment | 1 |
| unknown_value_rejected | 1 |

The formula-preservation counter includes both quantifier-free and quantified
formulas. Twenty-four randomized systems plus a concrete 8-state system, a
64-state system, an empty system, and a system with no operations/observations
make up the 28 fixtures. Sixty-four formulas per fixture are generated, of
operational depth at most three and quantifier rank at most three. The 64-state
fixture has rank capped at one. Assignments are exhaustive when their count is
at most sixteen and otherwise six are deterministically sampled. All source
state pairs are exhausted for partition/compiled-formula/witness comparisons.
Delayed-observation tests cover horizons 0..23. The infinite-stream theorem is
a separate universal Lean proof, not a finite-stream extrapolation.

The evaluator and finite discovery algorithm are not formally verified executable
programs. There is no model-training run, structural holdout evaluation, or
minimum-formula-size theorem. The finite discovery code builds actual witnesses
and is checked against an independent partition-refinement route, but no claim
of automatic synthesis in arbitrary infinite theories follows.

## Provenance

`LEAN_MANIFEST.json` and `PYTHON_MANIFEST.json` are version-2 records binding
execution inputs before/after, declared results, logs, commands and versions.
Both validators passed with root-relative byte verification. The full parent
v0.4 is preserved but not recompiled: only its two imported semantic modules are
replayed in the current cold build. Mathematical interpretation is self-review.
