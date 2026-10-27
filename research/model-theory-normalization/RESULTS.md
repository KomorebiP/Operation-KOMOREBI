# Retained results — v0.10

## Cold Lean audit

PASS: nine modules; 159 named declarations; 105 theorems (78 generic, 27 examples).
17 expected-outcome tasks completed. Sum of subprocess runtimes: 52.769184 seconds.
This is an execution receipt, not a comparative performance claim. All pinned
accepted source hashes were unchanged. The positive control accepted and six
invalid controls were rejected for their claims. Only standard axioms occurred.

## Independent Python audit

PASS: 119,732 individual checks; 203 full discovery fixtures.
All values use exact integer/Boolean arithmetic. Random wide cases use seed
2026092110. Native integer arithmetic supplies independent scalar reference results.

| Check | Count |
|---|---:|
| `unsigned_add` | 8,192 |
| `adder_cost_length` | 8,192 |
| `subtractor_borrow_identity` | 8,192 |
| `subtractor_cost_length` | 8,192 |
| `unsigned_multiply` | 4,096 |
| `multiply_quadratic_budget` | 4,096 |
| `unsigned_divmod` | 7,936 |
| `division_quadratic_budget` | 7,936 |
| `signed_add` | 4,225 |
| `signed_add_budget` | 4,225 |
| `signed_multiply_budget` | 4,225 |
| `signed_subtract_budget` | 4,225 |
| `signed_subtract` | 4,225 |
| `signed_multiply` | 4,225 |
| `signed_euclidean_divmod` | 8,224 |
| `signed_division_budget` | 8,224 |
| `residue_multiply` | 4,900 |
| `residue_wide_product_budget` | 4,900 |
| `residue_add` | 4,900 |
| `residue_add_budget` | 4,900 |
| `wide_padded_multiply` | 160 |
| `wide_padded_divide` | 160 |
| `wide_signed_divide` | 160 |
| `zero_divisor_rejected` | 3 |
| `malformed_word_rejected` | 4 |
| `frozen_parent_result_count` | 203 |
| `bit_backend_discovery_answer` | 203 |
| `bit_backend_canonical_basis` | 203 |
| `same_arithmetic_opcode_counts` | 203 |
| `same_arithmetic_total` | 203 |

The declared exhaustive bounds are: unsigned pairs 0..63, unsigned division
dividends 0..255 and divisors 1..31, signed pairs -32..32, signed division
dividends -128..128 and divisors 1..32, every residue pair at moduli 1..24.
There are 160 separately seeded padded wide cases with widths drawn from
16,32,64,128,256. Finite tests do not replace generic Lean proofs.

## Full discovery port results

All 203 ordered outputs and canonical bases equal the frozen originals. Every
per-opcode arithmetic-event count matches, totaling 295,173 events. The new
declared gate/cell total is 270,165,476. The maximum input magnitude width is
42 bits; padded output storage reaches 100 bits. These are different quantities.

| Fixture | Scalar events | Gate/cell units | Maximum operand width |
|---|---:|---:|---:|
| scrambled_128bit.source | 2,465 | 14,028,031 | 42 |
| descending_torsion.source | 696 | 1,045,360 | 25 |

The port deliberately re-encodes and decodes at scalar boundaries; conversion
volume is recorded but its cost is not included. Extraction/Option interface
charges are declared port conventions, not a whole-program Lean cost theorem.
The 203 examples are inherited synthetic regressions, not new held-out discoveries.

## Lineage and replay

The frozen parent archive SHA and all 1,395 listed payload hashes were verified.
All 207 selected baseline payloads agree byte-for-byte with the parent. The
recursive ZIP font scan found no font files. No parent Lean or full Mathlib rebuild
is claimed. Final distribution and fresh-extraction results are in the separate
EXTRACTED_REPLAY.json and packaging report, rather than inferred from this note.
