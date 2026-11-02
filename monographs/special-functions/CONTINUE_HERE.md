# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B02**, based on repository commit
`cfff62cde8c8a5aac109fc84bf89c73b0e3daad1`. Start with
`formalization/Block02/REPORT.md`, then its claim map, declaration map,
self-review and source-bound execution receipt.

`lean/CoupledAnalytic.lean` adds 21 checked declarations: the actual recurrence
sums are holomorphic on `norm(z)^2<2` and satisfy the normalized coupled
differential equations there. Block01's 29 coupled declarations and the
39-declaration finite core retain their earlier records. The full monograph
remains open. Do not stop merely because Lean is absent from PATH.

Next executable step: for strict contractions `Q=max(q,r,a,b)<1`, construct
holomorphic primitives of the contracted products on radius `R/Q`, prove their
agreement with the old functions on radius `R`, and preserve the equations.
Then glue the unbounded radius ladder. Analytic uniqueness and the reverse
coefficient bridge still require their own proofs; Perron growth remains open.

Use `tools/verify_coupled_analytic.py` with Lean 4.34.0-rc2, Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and a fresh external work
directory. The native Windows run is distinguished from the preserved offline
Linux kit and its assembly instructions in `formalization/Block01/REPORT.md`.

The uniform-convergence and Cauchy-product route resolved the local target.
Sparse formal power-series packaging and direct derivative majorants were
deferred, not disproved. There are no delegated or delayed runs to reconcile.

Preserve both blocks' records and put the next theorem family in a new block.
The root package manifest remains an earlier release snapshot; use each
block's source-bound records for its current formal claims.
