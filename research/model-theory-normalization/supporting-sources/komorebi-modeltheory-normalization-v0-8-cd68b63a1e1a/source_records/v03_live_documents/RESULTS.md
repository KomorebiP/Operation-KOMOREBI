# Retained results — M3 / Model-Theory Normalization v0.3

## Lean

**PASS:** 222 local modules, 236 expected-outcome tasks,
7,871 named declarations. The full cold run took
199.755756 seconds in the recorded environment. This is one
execution measurement, not a performance comparison or guarantee.

The core consists of 15 inherited and five new modules. All 202 generated symbolic
instances were then rebuilt. Eight axiom batches covered every inventoried name.
The positive control and five expected rejection controls behaved as specified.
Accepted source hashes were unchanged and no unexpected axioms occurred.

The 7,871 named declarations comprise 5,087 theorems, 2,562 definitions,
210 abbreviations, five structures, five inductive types and two named instances.
Most are inherited/generated certificate facts. The newly written generic core
has 32 theorem declarations, 10 definitions and one abbreviation.

## Exact finite Python audit

**PASS:** 66,428 check calls, 202 source/certificate pairs, deterministic
seed 2026092103. The recorded inner audit runtime is 1.393031
seconds. Input hashes were unchanged. No floating-point arithmetic supports the
mathematical comparisons.

| Check | Count |
|---|---:|
| independent_logical_certificate | 202 |
| rediscovered_certificate_identical | 202 |
| deterministic_logical_export | 202 |
| independent_lean_transcription | 202 |
| deterministic_lean_export | 202 |
| quantifier_free_export | 202 |
| symbolic_qf_vs_encoding | 3,232 |
| wrong_sort_rejected | 3,232 |
| test_values_reconstruct_encoding | 3,232 |
| class_formula_nonempty | 3,232 |
| class_formula_exact | 3,232 |
| class_formula_wrong_sort | 3,232 |
| growth_formula_distinguishes | 643 |
| exhaustive_finite_formula_kernel | 36,364 |
| exhaustive_wrong_sort | 8,312 |
| quantified_image_transport | 492 |
| corrupted_logical_export_rejected | 8 |
| rebound_source_rejected | 1 |
| corrupted_lean_test_transcription_rejected | 1 |
| out_of_image_class_query_rejected | 1 |
| word_order_counterexample | 1 |
| free_target_quantifier_failure | 1 |

## Tested ranges

All 202 inherited synthetic matrix cases are included unchanged. The symbolic
audit compares 16 state pairs per case; eight pairs are constructed inside the
certified encoding kernel to ensure that the equal branch is exercised. Individual
class formulas are tested on these pairs and on wrong-sort value inputs.

All 643 retained growth witnesses are checked as actual distinguishing formulas.
Forty-four small systems have at most 64 source states; every source-state pair
is checked, together with source/value-tag pairs. Five quantified formulas per
small case, plus one nested existential for source size at most 16, are checked
at the first and last source states (deduplicated when there is only one).
The source evaluator prepends bound variables; the independently implemented
primitive target evaluator appends them. The target domain is the actual image.

The eight-coordinate source modulo 65536 has 2^128 source states, two arithmetic
coordinates, two observation tests, and horizon one. It is checked symbolically,
not enumerated. The delayed example has eight tests and horizon seven. The test
cases are not a newly held-out benchmark and no learned policy was trained.

Eight logical export mutations, a rebound changed source, a changed generated
Lean test list and an out-of-image class query are rejected. The independent
checker imports neither the discoverer nor exporter. Literal-source comparison
is an executable audit, not a verified parser theorem.

## Provenance and replay

Both parent archives are frozen in history/. The lineage audit validates 425
copied payloads, including 15 Lean modules and all 404 source/certificate JSON
files. It is not a new proof rerun of the whole representation or p-adic corpus.

`LEAN_MANIFEST.json` and `COMPUTATION_MANIFEST.json` are version-two execution
records with before/after input hashes, actual commands, limits, result hashes
and logs. Both validate against this root. Distribution integrity must be checked
BEFORE rerunning scripts because replay intentionally writes new result records.

A separate fresh-extraction replay is reported beside the final ZIP. Its Lean
selection is explicitly a subset (all 20 supporting modules plus four cases),
not a second complete rebuild of all 202 generated instances.

## Interpretation

Universal claims are established by the exact Lean statements, not finite test
counts. The saved per-case Lean applications apply to all source states, arbitrary
finite future words and the full translated observational formula family. New
formulas define the matrix kernel; no new predicate naming that kernel is assumed.
The actual image is used for quantifiers. No logical-minimality or unrestricted
model-theory theorem is claimed. See NORMALIZED_CORE.md and PROOF_AUDIT.md.
