# Continue from v0.32 — Nonsemisimple Frobenius Norm

Read README.md and RESEARCH_BOUNDARY.md. Preserve the exact v0.31 parent SHA
and the audited distinction between a genuine representation root and a point
of an artificially enlarged equation system.

The strongest result is primary_norm_range_ker in PrimaryBlockNorm.lean,
composed with prescribed_primary_power_iff in NonsemisimpleFrobeniusLifting.lean.
Prime-power degree needs no primary decomposition. GeneralDualMatrixNorm.lean
constructs the actual dual-number matrix comparison. UnipotentNormExamples.lean
shows why eigenvalues alone are insufficient.

The next internal problem should be the **simultaneous** norm image on a
nilpotent primary block. Start from the actual old localization map, not from
separate roots. One x is shared by all degree restrictions; local z_i can vary.
Alternatively, construct the true mixed-characteristic coefficient-layer action.
Do not report either problem as solved by the current single-prescription theorem.

Run verify.py with the pinned portable kit, using --max-modules 4 and --resume
when execution wrappers are bounded. Every module needs an observed zero code;
inspect the all-named-constant axiom audit. Run checks/exact_norm_checks.py too.
Do not add a full historical replay claim merely because the immediate closure passes.
