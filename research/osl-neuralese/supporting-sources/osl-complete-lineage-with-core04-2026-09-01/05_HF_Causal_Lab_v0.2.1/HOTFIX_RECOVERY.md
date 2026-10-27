# v0.2.1 hotfix and recovery record

## Failure repaired

The v0.2.0 full run completed all four seeds for `answer_only`, `state_supervised`, and `equivalence`. It then failed at the first `operator_regularized` batch because CUDA autocast produced a half-precision encoder state while a learned transition returned a float32 tensor. Indexed assignment requires identical dtypes.

Version 0.2.1 evaluates the transition auxiliary objective in explicit FP32 outside autocast. Gradients still flow through the transition modules and encoder states.

## Recovery behavior

Resume mode:

1. Preserves `PREOUTCOME_FREEZE.json` unchanged.
2. Records the repaired source and recovery attempts in `RESUME_PROVENANCE.json`.
3. Regenerates the executable datasets from the frozen seed.
4. Rejects a mismatch in the frozen configuration, protocol, vocabulary, dataset audit, model structure, or checkpoint identity.
5. Loads completed checkpoints without retraining.
6. Recomputes every held-out, geometry, orbit, and causal audit.
7. Trains only checkpoints that do not already exist.
8. Writes new checkpoints atomically and stores their epoch histories.

The original checkpoints did not store their training histories. The final recovery metadata explicitly lists those missing histories.

## Interpretation boundary

This is a compatibility recovery of an exploratory full run. The objectives, supervision arms, holdouts, and adjudication gates are unchanged. Because the repair was made after the run began and the original CUDA attention path issued a nondeterminism warning, a strict confirmatory claim requires a clean future run from the repaired source.

The frozen logistic-regression settings are unchanged. Any convergence warning remains a caveat when interpreting neural performance relative to lexical controls.
