# Retained results — Model-Theory Normalization v0.7

## Lean

PASS: 44 local modules, 68 expected-outcome tasks,
1601 named declarations. All 203 inherited profiles execute
the normalized algorithm by kernel reduction. All source hashes are unchanged.
Seven rejection controls and one positive control pass their required outcomes.
Only Classical.choice, Quot.sound, propext occur in the axiom audit.
Completed task runtime sum: 1052.271658 seconds. This is not a
comparative performance measurement. One 160-name axiom batch timed out at 90 seconds.
Its failed state and diagnostics are retained. The uncompleted axiom batches were
split to at most 80 names, with no changes to mathematical sources or completed
builds. The completed-task sum excludes that failed attempt, while elapsed protocol
time includes interruption and recovery. One split 80-name group also reached
its cap. Remaining drivers then used module-mode imports and completed with the
same declaration inventory and proof hashes. Both failed states are retained.
See v07_evidence/protocol_revision/.

## Exact Python port audit

PASS. Seed 2026092107; one recorded runtime 1.630249 seconds.
The baseline and new discovery use the same sources and queue policy.

| Check | Count |
|---|---:|
| ordered_discovery_results | 203 |
| baseline_statistics_reproduced | 203 |
| deterministic_new_statistics | 203 |
| per_source_stored_bit_bound | 203 |
| gcd_update_count | 203 |
| normalization_division_count | 203 |
| accepted_tests | 667 |
| queue_decisions | 1,636 |
| source_literal_transcription | 203 |
| answer_literal_transcription | 203 |
| modulus_transcription | 203 |
| exhaustive_basis_image | 2,045 |
| normalization_idempotence | 2,045 |
| exhaustive_insertion_order | 2,045 |
| exhaustive_membership | 56,552 |
| integer_reconstruction | 28,705 |
| generating_lists | 2,045 |
| general_idempotence | 150 |
| integer_lattice_row_certificate | 888 |
| unimodular_shear_canonical | 106 |
| representative_and_order_invariance | 90 |
| independent_smith_membership | 1,080 |
| coupled_constraint_retained | 1 |
| own_pivot_clipping_counterexample | 1 |
| invalid_input_or_cap_controls | 9 |

All generating lists of length zero, one and two are exhausted for
[[1, 2], [2, 0], [2, 2], [3, 2], [4, 2], [6, 2], [8, 1], [9, 1], [12, 1]], with every candidate vector. General integer-basis
checks cover 150 additional triangular inputs, and 90 random prime-power cases
are compared with the inherited independent Smith solver (12 queries each).
There are no floating-point load-bearing computations.

## Basis-entry measurements, not total memory or runtime

| Measurement across the same 203 sources | Bits |
|---|---:|
| Old basis, between complete insertions | 730 |
| Old basis, including partial updates | 730 |
| New persistent normalized basis | 25 |
| New partial pre-normalization basis | 39 |

The particular source reaching 730 previously now has maximum persistent entry
length 12. The large 2^128-state source changes from 69 to 17, and the 2^24
one-dimensional stress case remains 25. These maxima are finite implementation
observations. The universal numeric range [0,m] is separately Lean-proved.
The pre-normalization counter is NOT a bound on every temporary arithmetic operand.

## Provenance and trust

The immediate parent v0.6 Python audit reran successfully in an isolated extracted
copy. Current local dependencies are rebuilt; no full historical Lean replay is
claimed. All predecessor source bytes remain in the immutable parent ZIP.
Fresh-extraction scope is recorded separately in the external replay JSON.
The Python code and transcription are tested, not formally verified extraction.
The mathematical interpretation audit is self-review.
