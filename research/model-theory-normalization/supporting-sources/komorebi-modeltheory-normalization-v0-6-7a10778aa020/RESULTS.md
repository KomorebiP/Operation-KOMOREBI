# Retained results — Model-Theory Normalization v0.6

## Completed cold Lean audit

PASS: 39 modules, 48 logical audit stages,
55 actual Lean commands, 1536 named declarations.
All 203 source fixtures were actually executed by the kernel through the new
incremental solver, without supplied branch evidence or coefficient enumeration.
Axiom collection was divided into eight source-preserving groups after interrupted
monolithic attempts. Completed task runtime sum: 768.238586s.
Elapsed protocol time includes intervals and interruptions and is not a benchmark.
All accepted inputs stayed unchanged. Seven negative controls and one positive
control behaved as intended. Detailed logs and the protocol revision are retained.

## Independent Python port audit

PASS: 0.452410s in one recorded run, seed 2026092106.
This timing is not a comparative speedup or a performance guarantee.

| Check | Count |
|---|---:|
| frozen_ordered_discovery_results | 203 |
| deterministic_statistics | 203 |
| one_gcd_per_insertion_column | 203 |
| membership_division_bound | 203 |
| accepted_tests | 667 |
| queue_decisions | 1,636 |
| literal_source_transcription | 203 |
| literal_answer_transcription | 203 |
| literal_modulus_transcription | 203 |
| exhaustive_basis_image | 2,045 |
| exhaustive_membership | 56,552 |
| exact_integer_reconstruction | 28,705 |
| exhaustive_generating_lists | 2,045 |
| bezout_determinant_identity | 8,256 |
| independent_smith_membership | 1,080 |
| representative_shift_invariance | 1,080 |
| coupled_torsion_anchor | 1 |
| invalid_input_or_cap_controls | 10 |

The modular span oracle was exhausted on every generating list of length 0, 1 or 2
for (m,d)=(1,2),(2,0),(2,2),(3,2),(4,2),(6,2),(8,1),(9,1),(12,1), with every
candidate vector. This includes composite moduli, the trivial ring and dimension0.
Bezout identities cover q=1..64 and a=-64..64. Ninety separately seeded random
prime-power configurations were compared with the inherited Smith module solver,
12 queries each, plus integer representative shifts. No floating arithmetic.

All 203 frozen ordered test lists match. In total: 667 accepts and 1,636 queue
decisions. The large 2^128-state source returns two tests in five decisions; the
Python port stores eight rows and performs sixteen Bezout updates. The descending
24-test torsion source stores one row and performs 24 updates in 48 decisions.
The largest observed STORED basis coefficient in the Python suite was 730 bits;
this does not bound larger intermediate operands or arbitrary inputs.

## Parent replay and extraction

The immediate frozen v0.5 Python audit reran in an isolated extracted copy and
passed all 203 old trace tests and 6,674 exhaustive old membership comparisons.
Its record is v06_evidence/parent_replay/REPLAY.json. No full parent Lean rebuild
is claimed. Distribution integrity must be checked before rerunning audits because
new execution records rewrite timestamps and current outputs.

The exact final archive's fresh-copy verification is recorded in the separate
Komorebi_ModelTheory_Normalization_v0.6_EXTRACTED_REPLAY.json. It is not inferred
from these construction-time results.
