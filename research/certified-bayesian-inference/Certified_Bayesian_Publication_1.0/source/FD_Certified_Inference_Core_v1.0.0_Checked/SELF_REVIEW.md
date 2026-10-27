# Adversarial self-review

Normalized claim: for the exact finite model, complete rational self-adjoint
packets, a covering finite scan, and positive epsilon/delta, runCached returns
ResultValid for the actual returned data. Verdict: **proved as written**. The final clean build passed all 117 active
modules, and the axiom audit covered all 543 theorem/lemma declarations.
This is a self-review, not an independent human or separate-agent review.

Dependency chain:

    initialization -> cache invariant -> selected-label equivalence
    -> trajectory equivalence -> v13 finite-fuel bound -> cached search success
    -> precision-complete final rounded verifier -> actual posterior bound
    -> v12 parameter enclosures of the same returned Gaussian.

| Obligation | Finding |
|---|---|
| Cache supplied as hidden assumption | Passed: initialization and step preservation are proved. |
| Incorrect precomputed model constants | Passed: semantic theorems use prepare M; solver constructs it. |
| Selection changes under caching | Passed: chosen_eq and trajectory_gain prove exact equivalence. |
| Total-energy cancellation | Passed in exact rationals; no hardware arithmetic inference. |
| Zero/last fuel step | Passed: the last state is tested and its score bound supplies success. |
| Positive denominator/nonempty labels | Passed through inherited rate bounds and explicit seed. |
| Caller-supplied validity needed for soundness | No: final independent checker supplies soundness. |
| Returned gain tied to actual trajectory | Passed: cached_solver_gain_origin. |
| Same Gaussian in probability and output statements | Passed: reused ResultValid and represent_spec. |
| Delta interpreted as exact-posterior error | Excluded explicitly. |
| Rounded selective cache | Naive route refuted; general enclosed route remains open. |
| Benchmark fairness | Same backend, score margin, epsilon, delta and final verifier; full baseline avoids unnecessary packet scans. |
| Universal complexity inferred from counters | Excluded: counters are Python diagnostics, not bit-complexity proofs. |
| Literature supplies an unproved Lean leaf | No new external mathematical dependency. |

Independent numerical formulas reconstruct P, S, F and Joseph-factor parameters
without using the cached update equations. Seven cases include rectangular maps,
singular priors, dense and concentrated residuals, and a smaller noise floor.
The full benchmark records five timed repetitions after warmup with rotating method
order. Exported final candidates are checked separately. No speedup extrapolation
to large dimensions or hardware floating point is justified.

Proofreading self-review covers the new proof note, scope, route record, literature
comparison and benchmark report. Formulas were checked against current Lean names,
selection-side conventions, epsilon^2/4 slack, output semantics and example steps.
No mathematical-token correction or unresolved mathematical typo is recorded.
