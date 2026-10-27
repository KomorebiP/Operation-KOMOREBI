# Next-block route record

Base checkpoint: v11 continuation, SHA256
588640ecfc3faba00ff98bea0e82b1c6586cead970f2ecc4a6ad1a5c745761be.
Inherited active-release recorded source commit:
2196889b5030c2cadb0c188fb7e771d6185f314e.
This checkout was restored from the archive. The predecessor commit is provenance,
not a claim that the current filesystem is that Git checkout.

Goal: move from a certified represented gain to a usable certified output of
posterior parameters, preserving the actual-law and singular-covariance boundary.

1. Directly treat rounded covariance centers as a valid covariance.
   Rejected by the explicit two-dimensional rank-one counterexample in
   PosteriorOutputBoundary.lean. Reopening requires a PSD-preserving construction.
2. Return rounded noise factors and certify their changed Gaussian law.
   Mathematically plausible, but requires a new common-noise transport bound and
   representation semantics. Deferred, not counted as completed.
3. Return dyadic interval arrays for the parameters of the already certified law.
   Selected and implemented. Compositional ball bounds yield a computable output
   precision, then the law identity and actual return connect the data to v11.

Success criterion: actual pinned Lean compilation, complete axiom audit, source
and dependency receipts, and concrete checked returned arrays. Numerical agreement
alone is not success. Full architecture completion is not inferred from this block.

Next high-value routes: certify a point-valued factor output or sampler if needed
by the product; otherwise validate one genuine packet-selective update policy.
The latter needs a concrete update rule and bounds for cross-packet effects.
