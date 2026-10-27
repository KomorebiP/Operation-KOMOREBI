# Retained results — Model-Theory Normalization v0.4

## Formal execution

PASS: 23 modules (12 inherited, 11 new), 30 expected-outcome tasks,
443 explicit named declarations. All accepted inputs remained unchanged.
Only propext, Classical.choice and Quot.sound occurred. Five negative controls
rejected and the positive control accepted. All local sources were compiled cold
with one Lean worker and warnings as errors. The pinned upstream cache was reused.

The six generic modules add 44 theorem declarations. The concrete reference adds
11 and the four generated traces add 64. Thus there are 119 new named theorems,
not 119 independent discoveries. All names including definitions are audited.

The cold run was performed in synchronous, hash-checked batches. A partial enclosing
call interrupted one batch after the axiom audit; completed artifacts and all input
hashes were verified before resuming. Only completion of every planned task permits
writing the PASS manifest. `compile_seconds` sums the individual completed task
runtimes (159.774812s). The separate `runtime_seconds` field
sums completed batch-invocation runtimes and excludes an interrupted invocation,
so it is not an end-to-end wall-time or performance claim.

## Exact independent Python checks

PASS: 202 frozen source/certificate pairs, 1,588 complete FIFO decisions,
643 accepted rows and 945 skipped rows. Final raw tests match the preceding
certificates. The checker imports neither Smith nor the producer. Four generated
Lean traces are deterministically reproduced and their source literals independently
compared with the separately supplied source.

| Check | Count |
|---|---:|
| deterministic_trace_regeneration | 202 |
| independent_complete_trace | 202 |
| frozen_test_list_preserved | 202 |
| accepted_bound | 202 |
| queue_accounting | 202 |
| skip_witnesses | 945 |
| accept_witnesses | 643 |
| exhaustive_coefficient_oracle_agreement | 93 |
| exhaustive_candidate_agreement | 93 |
| exhaustive_final_observations | 93 |
| exhaustive_final_span_invariant | 231 |
| reference_degenerate_boundary | 4 |
| insufficient_fuel_unresolved | 1 |
| lean_export_regeneration | 4 |
| lean_literal_source_actions | 4 |
| lean_literal_source_observations | 4 |
| lean_literal_modulus | 4 |
| lean_trace_branches | 4 |
| corrupt_trace_rejected | 10 |
| resource_cap_unresolved | 1 |
| checker_implementation_independence | 1 |

The 93 exhaustive reference fixtures are all 64 binary two-coordinate systems
with one action and one observation and all 29 scalar systems over moduli 2,3,4.
Four extra reference fixtures cover d=0, r=0, no actions, and no observations.
There are ten corrupted trace controls and one stopped resource-cap run. A stopped
run is unresolved, never a successful empty output.

Large fixture: 2^128 admissible states, two accepted tests, three skips, five
candidates, horizon one. Generic enough-fuel budget: 258. Its output is proved
via a complete symbolic queue trace, not by executing the enumerative oracle at
that scale. The delay fixture reaches horizon seven. These are existing synthetic
mechanism tests, not held-out discoveries or comparative benchmarks.

## Immediate parent replay

The independent v0.3 Python audit reran successfully in a separate extracted copy:
202 certificates and 66,428 check calls. Source/input hashes were unchanged.
`new_evidence/parent_python/REPLAY.json` records the exact scope. No new replay of
all 222 parent Lean modules is claimed.

## Artifact and trust boundary

The immutable parent ZIP is retained in history and every inherited Lean source
is byte-identical. Final integrity/extracted-copy outcomes are recorded separately
in the packaging report. Python executable correctness, proof interpretation and
informal source fidelity are not established merely by the finite test counts.
Universal claims refer to the precise accepted Lean statements.
