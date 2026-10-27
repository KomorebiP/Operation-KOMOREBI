# Retained results — Logical Resolution v0.2

## Lean

PASS: 13 modules, 112 named theorems, 196 explicit named declarations and 23
expected-outcome tasks. The inner cold audit measured 18.341894
seconds on this execution. This is not a benchmark or speedup comparison.
Only Classical.choice, Quot.sound and propext occur. Eight inherited Lean files
remain byte-identical. The six expected-negative controls all reject, and both
positive controls accept. Accepted source hashes before and after agree.

## Independent finite reference audit

PASS: **39,262 check calls**, seed 2026092102, measured
0.497473 seconds for the inner audit. Finite checks are not
independent discoveries and do not replace universal proofs.

| Check | Count |
|---|---:|
| all_graph_standard_translation | 6,144 |
| backforth_vs_extension_types | 4,608 |
| empty_existential | 1 |
| empty_universal | 1 |
| explicit_noninjective_relational_quotient | 1 |
| explicit_relational_quotient_truth | 24 |
| independent_satisfaction_translation | 9,772 |
| inputs_unchanged | 1 |
| invalid_quotient_relation | 1 |
| malformed_matrix | 1 |
| nested_binder_control | 1 |
| noncommuting_word_translation | 1 |
| nonsurjective_quantified_map | 1 |
| one_class_at_rank_zero | 1 |
| one_step_backforth_failure | 1 |
| out_of_scope_variable | 1 |
| quantified_relational_transport | 4,443 |
| rank_one_backforth_preservation | 7,104 |
| relational_transport_contract | 16 |
| reversed_word_mutation_detected | 1 |
| same_model_atomic_agreement | 1 |
| same_model_rank_one_separation | 1 |
| standard_backend_transport | 4,443 |
| state_equality_not_in_source_fragment | 1 |
| three_classes_at_rank_one | 1 |
| translation_rank | 2,688 |
| unknown_literal | 1 |
| unknown_relation | 1 |
| wrong_binder_mutation_detected | 1 |


The 28 random and degenerate models receive 96 generated formulas each. Formula
arities range from zero through two, quantifier rank at most two, word length at
most two. Assignments are exhausted when their number is at most 16 and otherwise
six deterministic samples are used. Empty state/value domains and an empty
operation/observation/relation signature are included.

Sixteen relation-reflecting surjective pullback pairs receive 64 formulas each.
The same formulas are evaluated independently using both the source syntax and
the target falsum/imp/all syntax. All 512 directed relations on three vertices
are separately exhausted under identity dynamics and constant observations.
All ordered state pairs are checked for rank-one matching; four quantified query
templates are tested. This finite back-and-forth audit has identity dynamics and
must not be presented as an exhaustive all-operation-system audit.

Mutation controls change the newest bound level and reverse a noncommuting word.
Shape, scope, relation, literal and surjectivity errors are rejected. Exact counts
and all input hashes are retained in results/PYTHON_AUDIT.json.

## Predecessor

The frozen v0.1 Python audit reproduced 38,077 checks. Seed, detailed checks,
fixtures, bounds and total all match the saved deterministic fields. Its runtime
record naturally differs. The original archive was not mutated. All eight parent
Lean modules are rebuilt in the new 13-module cold run, not merely imported from
old local object files. The deeply embedded Representation Calculus archive was
not separately rerun.

## Evidence

LEAN_MANIFEST.json and PYTHON_MANIFEST.json record the actual commands, accepted
inputs before/after, outputs, logs, dependency versions, declared scope and caps.
Both validate with tools/validate_manifest.py and root-relative hash checking.
FILE_MANIFEST.json concerns distribution integrity, which must be checked BEFORE
rerunning audits. Fresh-extraction replay is recorded in the companion external
JSON so rerun output cannot invalidate the frozen release's own manifest.

Semantic review is self-review; the universal statements are precisely those in
the Lean files. The translator implemented in Lean has proved satisfaction
correctness. The separate Python translator/evaluator is an implementation audit,
not verified extraction of that Lean definition.
