# Komorebi Unified Inference / Stochastic / Bayesian — continuation v3

**Active checkpoint: finite-dimensional Gaussian Bayesian conditioning is closed
under P positive semidefinite and R positive definite.**

Read `CONTINUE_HERE.md` completely, then `AUDIT.json` and the active checked
release's `README.md`, `PROOF_NOTE.md`, and `FINAL_VERIFICATION_RECEIPT.json`.

Active release: `CHECKED_RELEASES/FD_Gaussian_Bayesian_Conditioning_v0.1.0_Checked/`.

The latest source proves actual forward/reverse joint-law equality, the evidence
law, and canonical Gaussian posterior identification evidence-almost everywhere.
It does not yet connect the earlier finite-dimensional operator-norm multiscale
perturbation budgets to those actual posterior covariance operators.

The older checked chain remains byte-preserved. The prior v2 archive is retained
verbatim in `PRIOR_CHECKPOINTS/`, and its original root instructions are archived
in `HISTORY/v2_root_control/`. Historical OPEN finite-dimensional semantics labels
are superseded only by the stated new theorem. Other boundaries are unchanged.

The new 18-module layer has fresh compile and all-theorem axiom audits. Historical
releases and mathlib itself were not fully rebuilt in this turn.

`MANIFEST_SHA256.txt` is the current cumulative byte-integrity manifest. The
large pinned runtime is not embedded. Use its existing Linux/WSL copy and the
active release's `verify_blocks.py`, one Lean invocation per module.
