# Trace/moment residual certification and exact completion

Outcome: proved as written; finite performance evidence separately bounded.

The route began from the v0.7 obstruction: a single operator-norm residual
produced valid but unusably wide deep-tail intervals.  The new input is the
exact PSD decomposition `A^T A = B^T B + F^T F`, which exposes residual trace,
square trace, and spectral cap.  These yield a trace--Frobenius--cap MGF
envelope and moment rank bounds.  When the residual rank becomes affordable,
a streamed residual QR/SVD completion restores the exact core rather than
continuing worst-case tail bounding.

See `PROOF_AUDIT_TRACE_MOMENT_RESIDUAL.md`, `random_mgf_audit.csv`,
`trace_cap_range_core_audit.csv`, and `residual_completion_audit.csv`.
