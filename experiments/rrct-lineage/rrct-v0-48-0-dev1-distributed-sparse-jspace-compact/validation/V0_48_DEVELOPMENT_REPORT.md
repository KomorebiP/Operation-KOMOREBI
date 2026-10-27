# RRCT v0.48 Development Report

## Status

`V048_DISTRIBUTED_SPARSE_JSPACE_ENDPOINTS_MET` on the exposed development cohort.

Development seeds: `48011, 48017, 48023, 48029`

- Trials per seed: 32
- Unique world cases: 128
- Matched mode decisions: 1152
- Declared endpoints met: 28 / 28

## Principal exposed results

- Mean local report R², Agent A: 1.000000
- Mean local report R², Agent B: 1.000000
- Mean local workspace variance fraction, Agent A: 0.114708
- Mean local workspace variance fraction, Agent B: 0.114720
- Minimum canonical correlation: 0.999894
- Mean cross-agent alignment R²: 0.999863
- Minimum cross-agent frame cosine: 1.000000
- Mean support agreement: 1.000000
- Minimum dynamic support count: 16
- Full shared task/report/flexible-reuse/closure: all 1.0
- Message-only task accuracy: 1.000000
- Message-only distributed-J-space closure: 0.000000
- Message-shuffle task accuracy: 0.203125
- Message-shuffle structural closure: 1.000000
- Ablated task accuracy: 0.078125
- New-partner unadapted accuracy: 0.255208
- New-partner remapped accuracy: 1.000000

## Development changes before freezing

1. Added two independently discovered local Jacobian workspaces.
2. Added overcomplete opposing concept frames and sparse nonnegative support.
3. Added cross-agent frame transport and token correspondence.
4. Added distributed access receipts bound to both local access receipts and the v0.47 pair workspace.
5. Added directed shared-concept swaps, selective ablation, capacity interference, provenance, recurrence, and partner-remapping probes.
6. Replaced an initially linear flexible-query decoder with a shared-state readout followed by multiple deterministic downstream functions, so one shared state is genuinely reused rather than separately decoded for each query.
7. Strengthened the feedback challenge so one-round evidence is intentionally ambiguous while three-round reopened interaction is sufficient.
8. Strengthened partner recombination so pair-private message codes fail before fresh message and frame calibration.

No holdout result was used in these changes.

## Development artifact hashes

- Analysis: `fd729a2011c1c3b7e150a3a63809abaeae0661e95cb2be36a1488e1efdef4c87`
- Compact summary: `c11450ac99f3aa4905535a98027e29b4342bf442f13545b4a5719942a058b71b`
- Decision table: `ab43ce56d7d543a6463283ce57c47e11cc75181699127bf7238d732bf1b63c6f`
- Human report: `7b91e4919923bed09f0a2d05c004691b80af74b686ddcbcb46e82183df266f39`

## Boundary

Development success is not frozen evidence. The official claim depends on a fresh seed receipt, an immutable pre-outcome seal, and the post-seal holdout execution.
