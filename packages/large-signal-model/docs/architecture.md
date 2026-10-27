# Architecture

The release has a standalone signal path and an inherited categorical-frame model.
They share exact-coordinate and packet-tree machinery but are not the same interface.

The signal path accepts a finite real vector, preserves its float64 samples, computes
Fourier, residue-channel and Haar packet coordinates, and exposes complete synthesis.
FIR transfer blocks and chunked streaming are deterministic operators. They do not
learn taps automatically. Signal archives store source samples, not model weights.

The model path preserves each original categorical frame and separately constructs
bounded macro/meso/micro summaries. A declared grammar generates regressors from
those summaries, history and actions. Regression coefficients are fitted, candidates
are scored on common target coordinates, and finite-candidate weights are normalized.
The default then refits each supported candidate on all available training records.
A replay graph and heuristic planning layer use recorded transitions and predictions.

The archive is not interchangeable with a statistical state. A small reconstruction
residual does not establish predictive accuracy. A low predictive error does not
establish that a latent state is sufficient for future decisions. These are separate
contracts with separate checks.

See [the release guide](RELEASE_GUIDE.md), [claim boundary](claim-boundary.md) and
[migration notes](migration-2.3.md). The [historical paper](../paper/README.md) describes
the original architecture and retains its original experimental protocol.
