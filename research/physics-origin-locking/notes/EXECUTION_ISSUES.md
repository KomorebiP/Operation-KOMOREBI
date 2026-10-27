# Execution and validation issues

1. One batched numerical command reached its wall-clock limit after all nine named runs had printed completion. Each saved JSON and NPZ pair was subsequently read and independently recomputed at its stored mode snapshots. Interrupted commands were not treated as proof of completion by themselves.
2. The first independent complex-amplitude cross-check used tolerances that gave a normalized mode-energy difference of 2.03e-7. Tightening its tolerances reduced the difference to 3.31e-9. The exploratory result is retained separately.
3. A strict absolute hyperboloid residual test failed in the highly occupied, changed-model long runs. Terms of order 1e10 are subtracted to reconstruct an invariant equal to 1. A further tight integration did not cure this diagnostic, so the failure remains reported. It is not silently replaced with a looser tolerance. The origin-branch accepted runs have much smaller absolute residuals.
4. The fast-expansion momentum-cutoff test fails even after the finite quadrature has converged. This is a scientific boundary of the finite instantaneous subtraction and the specified initial state, not a failed solver exit.
5. The framing error concerning q=4 versus q=0 is documented in CORRECTION_LOCKING_TARGET.md. No input benchmark or old source was changed to conceal it.

6. A terminal-session invocation was rejected because streaming execution was unavailable. No result was attributed to it. Ordinary execution successfully ran the audit. Mode snapshots were subsequently reduced to 21 exact samples per run for delivery, without altering the complete saved diagnostic time series or any crossing values. The delivered files are reaudited.
