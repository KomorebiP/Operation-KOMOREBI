# Retained results — Model-Theory Normalization v0.5

## Lean

PASS: 39 local modules, 47 expected-outcome tasks, 2,130 audited names.
15 new universal generic theorems; 203 generated data-replay sources.
Only Classical.choice, Quot.sound and propext occur. All six rejection controls
failed for their intended proof statements, not missing dependencies or timeouts.
Accepted inputs stayed unchanged. Completed compilation/check tasks sum to
293.552509 seconds. This is a run measurement, not a benchmark.
The elapsed batched protocol includes pauses and is recorded separately.

## Independent exact computation

PASS: 203 complete traces, **667 acceptances and 969 skips**, 1,636 decisions.
All 202 frozen ordered results agree. All 203 emitted source/evidence/modulus/result
literals were reparsed and compared with separately supplied expected inputs.

| Check | Count |
|---|---:|
| deterministic_trace_regeneration | 203 |
| independent_complete_trace | 203 |
| bounded_smith_width | 203 |
| accepted_membership_witnesses | 667 |
| skipped_membership_witnesses | 969 |
| parent_literal_result_preserved | 202 |
| literal_source_matrix_agreement | 203 |
| literal_modulus_agreement | 203 |
| literal_output_agreement | 203 |
| literal_evidence_agreement | 203 |
| exhaustive_membership_decisions | 6,674 |
| exhaustive_positive_witnesses | 4,323 |
| exhaustive_negative_witnesses | 2,351 |
| exhaustive_generator_lists | 549 |
| exhaustive_basis_provenance | 762 |
| corrupt_trace_rejected | 12 |
| cap_is_unresolved | 1 |
| independent_checker_imports | 1 |
| input_hashes_unchanged | 1 |

The exhaustive membership set contains 549 generating lists of length zero, one or
two. It covers (p,r,d)=(2,1,2),(3,1,2),(2,2,2),(2,3,1),(3,2,1), all candidate rows.
Of 6,674 decisions, 4,323 have independently reconstructed positive witnesses and
2,351 have independently verified separating witnesses. There are 762 working-basis
provenance checks. All twelve malformed/misbound traces were rejected.

The new stress source has dimension one, modulus 2^24 and 24 descending-valuation
observations. It accepts 24 tests, makes 48 decisions, but each Smith problem has at
most two rows. The old raw-row strategy reaches 24 rows on this declared fixture.
This is a matrix-size comparison, not a measured wall-time speedup.

The inherited large source has 2^128 possible initial states. Its trace has two
acceptances and three skips. The kernel checks data without enumerating those states
or the reference algorithm's coefficient tuples. No new structural holdout is claimed.

## Parent and packaging scope

The original v0.4 archive is unchanged. Its documented 202-trace Python audit was
rerun in an isolated extraction and passed; raw result is retained under v05_evidence.
This is not a fresh audit of every older p-adic or representation-theory source.
Fresh-extraction checks of this release are recorded in the separate replay report.
The optimized Python producer, parser and exporter remain unverified executables.
