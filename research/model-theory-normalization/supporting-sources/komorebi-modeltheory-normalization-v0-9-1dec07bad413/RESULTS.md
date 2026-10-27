# Retained results — Model-Theory Normalization v0.9

## Cold Lean run

PASS: 53 local modules, 79 tasks,
1701 named declarations, all 203 exact result/count pairs.
All inputs unchanged. Only Classical.choice, Quot.sound, propext occur. The positive control
accepted and seven false/placeholder controls rejected. Completed task-time sum:
504.966923 seconds. This is audit/proof-checking time, not the
arithmetic solver's modeled cost or a performance benchmark.

## Independent Python port audit

PASS in one recorded execution of 2.279922 seconds. This includes
instrumentation and exhaustive tests, not a comparative runtime measurement.

| Check | Count |
|---|---:|
| ordered_answers | 203 |
| canonical_values | 203 |
| deterministic_arithmetic_units | 203 |
| complete_cost_bound | 203 |
| initial_normalization_count | 203 |
| literal_source_binding | 203 |
| literal_answer_binding | 203 |
| literal_cost_binding | 203 |
| literal_modulus_binding | 203 |
| accepted_tests | 667 |
| queue_decisions | 1,636 |
| arithmetic_units | 295,173 |
| bezout_values | 8,256 |
| bezout_exact_units | 8,256 |
| gcd_exact_units | 8,256 |
| euclid_depth_bound | 8,256 |
| exhaustive_membership_value | 56,552 |
| membership_cost_bound | 56,552 |
| successful_membership_exact_count | 28,705 |
| residue_exact_units | 56,552 |
| residue_coset_value | 56,552 |
| generating_lists | 2,045 |
| exact_insertion_decomposition | 3,976 |
| exact_normalization_units | 3,976 |
| independent_insert_value | 3,976 |
| fuel_exhaustion_unresolved | 1 |
| fuel_exhaustion_initial_cost | 1 |
| invalid_input_rejections | 6 |

Exhaustive generating lists of lengths zero, one and two for modulus/dimension
pairs [[1, 2], [2, 0], [2, 2], [3, 2], [4, 2], [6, 2], [8, 1], [9, 1], [12, 1]], with every candidate vector. Signed
Bezout tests use q=1..64 and a=-64..64. All 203 inherited fixtures keep their exact
ordered answers and canonical bases. The total across the suite is 295,173 modeled
arithmetic units, 667 acceptances and 1,636 queue decisions.

Large case201: 2,465 arithmetic units, two acceptances, five decisions; bound
17,092,754. Descending-torsion case202: 696 units, 24 acceptances, 48 decisions;
bound 57,086. These are exact counters in the stipulated model, not seconds or
machine instructions. Both values and counts are asserted and kernel-computed in
CostedComputed16, not supplied as inputs to the algorithm.

The port meters individual primitives independently of the symbolic count formulas.
It reproduces the exact formulas, all frozen answers, and the all-fuel boundary
checks. Six invalid-input controls reject. Source/action/observation/modulus/test/
counter literals are reparsed and bound to the independently supplied source.

## Preservation and replay

All 530 inherited Lean library sources under formalization/ and five copied Python baselines match their
predecessor bytes. The full original v0.8 ZIP matches its archived SHA256. The audit
compares directly with the old port on every source, but does not claim a full
rerun of every prior audit. Fresh-extraction scope and outcomes are in the separate
Komorebi_ModelTheory_Normalization_v0.9_EXTRACTED_REPLAY.json.

## Interpretation

Universal conclusions are the exact accepted Lean statements. Finite tests validate
implementation conventions, not every future Python run. Unit-cost semantics,
native execution costs, bit costs and proof checking are different quantities.
