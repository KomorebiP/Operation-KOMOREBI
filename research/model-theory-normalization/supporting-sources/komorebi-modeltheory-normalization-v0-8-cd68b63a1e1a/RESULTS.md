# Retained results — Model-Theory Normalization v0.8

## Completed cold Lean run

PASS: 49 local modules, 82 tasks,
1633 named declarations audited. All 203 fixtures directly
execute the bounded algorithm. Six intended false/placeholder controls reject and
one positive accepts. Only Classical.choice, Quot.sound, propext occur.
Completed task-time sum: 239.128812 seconds, not a benchmark.
No final cold task timed out or failed. Input and retained output hashes were
verified unchanged. Development attempts are separate and documented.

## Exact independent Python port audit

PASS: seed 2026092108, one execution 1.154034 seconds.
Timing includes instrumentation and tests, not a comparison with another solver.

| Check | Count |
|---|---:|
| frozen_ordered_outputs | 203 |
| same_canonical_basis | 203 |
| deterministic_port | 203 |
| temporary_magnitude_cap | 203 |
| temporary_bit_budget | 203 |
| insert_level_count | 203 |
| insertion_product_count | 203 |
| normalization_division_count | 203 |
| normalization_product_count | 203 |
| membership_level_bound | 203 |
| source_row_operand_bound | 203 |
| literal_source | 203 |
| literal_output | 203 |
| literal_modulus | 203 |
| accepted_tests | 667 |
| queue_decisions | 1,636 |
| bezout_identity | 32,832 |
| bezout_coefficients | 32,832 |
| euclid_peak | 32,832 |
| euclid_binary_depth | 32,832 |
| fibonacci_signed_stress | 320 |
| exhaustive_basis_image | 2,045 |
| exhaustive_canonical_order | 2,045 |
| exhaustive_membership | 56,552 |
| exact_integer_reconstruction | 28,705 |
| exhaustive_temporary_cap | 2,045 |
| signed_insertion_general_cap | 357 |
| signed_canonical_equality | 357 |
| independent_smith_membership | 1,080 |
| representative_invariance | 90 |
| actual_temporary_exceeds_modulus | 1 |
| coupled_congruence_retained | 1 |
| invalid_or_cap_rejections | 9 |

All lists of zero, one or two generating rows are exhausted for
[[1, 2], [2, 0], [2, 2], [3, 2], [4, 2], [6, 2], [8, 1], [9, 1], [12, 1]], and every candidate vector is checked. Bezout inputs
are q=1..64, a=-256..256; 320 additional signed Fibonacci pairs stress long
Euclidean recursions. Ninety random prime-power configurations receive twelve
independent Smith membership comparisons each. Arithmetic is exact.

## Measured temporaries versus proved budgets

Across all 203 sources, maximum instrumented core magnitude length is
42 bits; persistent entries reach 25 bits.
The large eight-coordinate source modulo 65536 returns two tests in five decisions:
42 measured temporary bits, 17 stored bits, and a conservative proved magnitude
budget of 289 bits. The one-coordinate modulus-2^24 stress source returns 24 tests
in 48 decisions: 25 measured temporary bits and conservative budget 75 bits.
These are finite measurements of the specified port's arithmetic, not universal
maxima or a wall-time speedup. Source row arithmetic is logged separately.

## Reproduction boundaries

The isolated v0.7 Python audit was rerun successfully; its record is retained in
v08_evidence/parent_replay. No full old Lean suite replay is claimed. All parent
sources and the immediate parent ZIP are preserved unchanged. Final distribution
integrity and fresh-extraction checks belong to the external replay report.
