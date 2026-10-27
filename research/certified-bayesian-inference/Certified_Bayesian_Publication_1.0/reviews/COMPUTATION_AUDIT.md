# Publication computation audit

This record audits the finite worked examples and figure data for *Certified Bayesian Inference: Packet Updates, Posterior Guarantees, and Arithmetic Certificates*. It does not replace the universal proofs or rerun the Lean kernel.

## Contract and interpretation

The coefficient domain is the exact rational field implemented by Python `fractions.Fraction`. Input integers and rational or decimal strings represent exact numbers. Raw JSON floating-point values are rejected by the retained producer. The fixed model is

\[
P=LL^{\mathsf T},\quad R=NN^{\mathsf T}+\sigma I,\quad S=HPH^{\mathsf T}+R,
\quad C=PH^{\mathsf T},\quad F(B)=C-BS.
\]

The checked input family consists of the archived two-dimensional coordinate model and two-dimensional rotated singular-prior model, plus the retained seven-case cache diagnostic and six-shape output diagnostic. The model is fixed throughout each execution. Complete self-adjoint mutually orthogonal packet families are supplied, and positive exact tolerances are used. No random sampling is involved. The posterior formulas denote the explicit chosen Gaussian posterior version, with equality to a canonical Bayesian posterior interpreted evidence-almost everywhere as in the source theorems.

A successful run establishes that these finitely many exact calculations agree with their documented contracts and archived deterministic outputs. A mismatch would identify an algebraic, implementation, data, or provenance defect requiring investigation. Passing does not prove the universal assertions, certify arbitrary JSON parsing, establish hardware floating-point execution, or prove practical scalability.

## Authoritative source and reproduction

The immutable baseline is `source/FD_Certified_Inference_Core_v1.0.0_Checked`. The publication script is `scripts/verify_publication_examples.py`. It imports the retained producer and independently computes innovation matrices, rational inverses, posterior formulas, residual matrices, packet energies, Joseph factors, interval comparisons, and a coupling-cost surrogate. Retained diagnostic commands are `checks/test_cached.py` and `checks/test_posterior_output.py`, each run with an output path outside the baseline and bytecode writing disabled.

The new bounded run is recorded in `reviews/exact_run/manifest.json`. Its contract is `reviews/exact_contract.json`, and its scientific outputs are:

- `reviews/exact_run/result.json`;
- `reviews/exact_run/cache_diagnostics.json`;
- `reviews/exact_run/output_diagnostics.json`.

The actual argv, Python version, input hashes before and after execution, output hashes, timestamps, elapsed time, process exit code and resource caps are recorded in that version 2 manifest. The installed mathbox computation-audit validator accepted the completed evidence record with `--root` output/input freshness checking. The bounded runner enforced a 45-second wall-clock cap, 40 CPU-second cap, 2 GiB address-space cap and one-core affinity; a one-thread numerical-library cap is cooperative. The completed run did not reach a resource bound.

`reviews/exact_example_results.json` is an exact byte copy of the scientific result used by the figure generator. All 940 files in the baseline were hashed before and after and remained unchanged. The source snapshot hash appears in the result. No fresh Lean process ran, so the publication's Lean evidence remains archived evidence.

For a narrow repeat without provenance wrapping:

```bash
python3 scripts/verify_publication_examples.py --output reviews/local_exact_replay/result.json
python3 scripts/bayes_figures.py
```

For a new provenance-wrapped run, use the recorded contract and the installed mathbox runner with a fresh output directory. Do not overwrite the recorded run directory or silently treat an unvalidated scaffold as evidence.

## Independent checks and exact outcomes

The publication script passed 236 assertions. The retained independent cache diagnostic passed 1,068 assertions with 9 expected rejections. The retained independent output diagnostic passed 398 assertions with 3 expected rejections. These are finite assertions and support checks, not counts of independent mathematical discoveries.

The independent posterior calculation uses Gauss-Jordan rational inversion, while the Joseph covariance is assembled directly from factor columns, instead of calling the producer's covariance graph. At every recorded state it verifies

\[
\Sigma(B)=\Sigma(K)+(B-K)S(B-K)^{\mathsf T},\qquad K=CS^{-1},
\]

and checks the explicitly calculated shared-input coupling cost

\[
\|(B-K)(y-Hm)\|^2+\operatorname{tr}((B-K)S(B-K)^{\mathsf T})
\le \frac{\sigma+\|y-Hm\|^2}{\sigma^2}\|F(B)\|_F^2.
\]

This is an exact bounded validation of the algebraic surrogate; the coupling interpretation and Wasserstein theorem remain the source theorem's mathematical obligations. The diagnostic does not compute or claim equality to the optimal Wasserstein distance.

### Coordinate fixture

The exact selected labels are `0,1,0,1,0,1`. The final gain is `(228/343,57/343)^T`, after six updates. The exact posterior gain is `(2/3,1/6)^T`. The final exact score is `34/117649`, and the successful rounded score at precision 12 is `481/1048576`. The precision-4 verifier fails with score `25/16`. The sufficient theorem-backed fallback precision is 72 and is not needed by these probes. Output precision is 32, and every reported center/radius array is reproduced and independently checked against the final Joseph parameters.

The exact posterior covariance is

\[
\begin{pmatrix}4/3&-2/3\\-2/3&5/6\end{pmatrix},
\]

while the final Joseph covariance is

\[
\frac1{117649}\begin{pmatrix}156868&-78432\\-78432&98041\end{pmatrix}.
\]

Their exact positive semidefinite excess is `[[16,4],[4,1]]/705894`. Packet cache invariants, untouched-entry reuse and the contraction inequality are checked before every completed update.

### Rotated singular-prior fixture

The selected labels are `0,0,0,0`. The final gain is the constant 2-by-2 matrix with entry `203/625`, after four updates. The exact posterior gain is constant `1/3`, the posterior mean is zero, and the posterior covariance is constant `1/3`. The final Joseph covariance is constant `130379/390625`. The exact score is `3072/390625`, the precision-12 rounded score is `9111/1048576`, and the precision-4 score `435/64` fails. The fallback precision is again 72 and output precision is 32. The complementary packet residual remains exactly zero throughout.

### Boundary examples

For the scalar independently rounded cache, the ideal first update gives gain and residual both `1/3`. At zero fractional precision, each rounds downward to zero. The stored score becomes zero while the true residual score is two. The independent rounded verifier rejects this gain at epsilon `1/10`. This is a counterexample to a center-only rounded-cache invariant, not a failure of the released exact cached algorithm.

For covariance centers, exact PSD covariance `[[1/4,3/4],[3/4,9/4]]` down-rounds at precision one to `[[0,1/2],[1/2,2]]`. The vector `(-3,1)` has quadratic value `-1`. Thus independent entrywise centers cannot automatically define a covariance. Interval arrays retain their enclosure meaning.

The hand dyadic example `x=1/3,p=4` returns center `5/16` and radius `1/16`, enclosing the value in `[1/4,3/8]`. Three finite greedy scan examples verify maximum choice, seed-preserving ties and duplicate coverage.

## Figures and numerical rendering

`scripts/bayes_figures.py` creates 20 PDF and PNG figures. `reviews/figure_catalogue.json` records each caption, exact scope, input references and both output hashes, together with the exact data hash, generator hash and numerical plotting-library versions. Exact fractions are converted to floating plotting coordinates only for rendering. Gaussian contours are numerical renderings of exact matrices, explicitly labeled as such; they are one-standard-deviation level sets rather than confidence regions or interval-certified curves. Singular-prior finite line segments illustrate scale and are not the entire unbounded support.

All 20 figures were inspected using contact sheets, with full-resolution checks of the densely annotated energy panels, precision plot, output-interval zoom, benchmark comparison and matrix/cache examples. The automated canvas check finds no drawn text outside the canvas. Precision and output-interval supplemental annotations were moved below their axis labels; matrix entries use contrast-sensitive text. All files are now stable. Future generator writes use atomic temporary-file replacement to avoid exposing a partially written PDF to a concurrent manuscript build.

Figure 19 reads only `results/FULL_COST_BENCHMARK.json`. Its times are archived September 2026 measurements for dimensions at most eight. Producer values are five-run medians; export and per-instance Lean checking have one measurement each. Their sum is an accounting estimate, not a sampled end-to-end latency distribution. The figure makes no fresh speed, large-scale, optimized BLAS/GPU, or general superiority claim.

## Result and remaining limits

**Implementation and finite assertions verified in the stated range.** The deterministic coordinate and rotated outputs reproduce the archived producer results after excluding nondeterministic timing fields. Their cached and recomputed trajectories agree. Fresh source and result provenance is validated.

Structural identities supported by these checks include complete packet energy accounting, selected/unselected cache preservation, Joseph covariance excess, fixed graph outward enclosure and deterministic greedy ties. Their generality is supplied by the archived formal theorem chain, not inferred from a larger number of numerical examples.

Fresh Lean compilation was unavailable in this environment. Universal parser refinement, hardware floating-point execution, rounded selective caches, executable sampling, changing models/packets and sequential filtering remain outside this publication's completed contract.
