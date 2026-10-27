# Komorebi Unified Inference / Stochastic / Bayesian — v14

Author: Komorebi P. Date: 2026-09-12.
Active release: CHECKED_RELEASES/FD_Certified_Inference_Core_v1.0.0_Checked.
Parent archive SHA256: 8f6bde58df0b6b18388f60adff4a22e5fed0a69d0a8f66321922452950cf3ba7.

## Frozen first-release claim

Certified Inference Core 1.0.0 completes the declared finite-dimensional,
one-observation inference reference system. For valid exact factor-coded rational
model data, positive noise floor, complete self-adjoint rational packet families,
a covering output-label scan and positive rational epsilon/delta, the canonical
program Komorebi.CachedPosterior.runCached returns a result satisfying ResultValid:

    W2(actual Bayesian posterior, Joseph Gaussian at returned gain) <= epsilon,

passing candidate/tolerance checks, plus outward-rounded mean/covariance intervals
of that same approximation with every radius <= delta. Covariance centers do not
independently define a certified law; delta is not exact-posterior coordinate error.
The parser/exporter are outside universal refinement. A generated Lean instance
certifies its explicit rational data only after actual successful compilation.

## Newly closed mathematical and implementation block

Exact cache state stores G_a = Q_a F(B), e_a = ||G_a||_F^2 and total = sum e_a.
With T = I - tau S and tau = 1/(sigma + trace S), a selected update maintains

    B' = B + tau G_a,       G_a' = G_a T,
    e_a' = ||G_a'||_F^2,    total' = total - e_a + e_a'.

Other output-packet cache entries are unchanged. Initialization and preservation
of every invariant are proved. Cache selection equals the v13 maximum-energy rule;
its trajectory equals the recomputed exact greedy trajectory. Inherited contraction
therefore supplies computed finite fuel. Cached exact-score tests use epsilon^2/4
slack; full rounded verification runs only after that test passes. A sufficient
verification fallback must then succeed. The returned gain is tied to an actual
permitted iterate. The v12 output theorem completes the same returned result.

Main declarations in namespace Komorebi.CachedPosterior:
  initialState_valid, step_valid, total_eq_residual_energy, score_eq,
  chosen_eq, trajectory_gain, trajectory_score_at_fuel,
  solveCached_terminates, cached_solver_gain_origin,
  cached_solver_reaches_posterior_tolerance,
  runCached_terminates, runCached_sound.

The cached selective branch uses exact rational updates and cache values. The
v11 rounded FULL-update solver remains a separate checked branch. Do not combine
these facts into a rounded selective-update theorem.

## Concrete checked results

Coordinate case: six cached updates, selections 0,1,0,1,0,1,
gain (228/343,57/343)^T, 12-bit certificate score 481/1048576, epsilon=1/20.
Singular rotated case: four updates, selections 0,0,0,0,
gain (203/625)ones(2,2), 12-bit certificate score 9111/1048576, epsilon=1/4.
Both use 32-bit parameter output with delta=1/1000. These full-program examples
check selections, actual returns, interval arrays and posterior guarantees.
The stricter exact-score margin explains the extra iteration relative to v13.

Twenty-one additional benchmark candidate certificates (seven models, three modes)
are checked for posterior tolerance. They do not certify Python timing traces or
all timed numeric arrays. Universal output correctness, two full-program instances,
and independent diagnostic formulas cover the declared output obligations.

## An unsuccessful route and honest performance result

Independently rounding gain and cached residual centers breaks cache validity.
A kernel-checked scalar counterexample has cached score zero but true score two;
the independent final verifier rejects it. A rounded cache with propagated error
bounds remains open. No unsafe success theorem is exported for this route.

The bounded benchmark uses dimensions <=8, five repetitions after warmup, identical
exact arithmetic backend/tolerance/output contracts, and an efficient full Richardson
baseline. Caching makes selective iteration roughly 1.9-5.6 times faster than full
packet recomputation. Total producer ratios are only about 1.01-1.17. No overall
advantage over the efficient full baseline is established. Final verification,
output, and Lean checking dominate much of this tested range. BENCHMARK_REPORT.md
includes export and actual per-candidate checking costs; counters are not a formal
bit-complexity theorem and this is not a scalability demonstration.

## Attribution and evidence

The bounded primary-literature review identifies established overlap with
Gauss-Southwell/block descent, cached gradients, pathwise conditioning/Wasserstein
error and formally checked arithmetic certificates. It supports conservative
attribution, not a priority or breakthrough claim. No new external theorem is an
unproved Lean dependency. See LITERATURE_COMPARISON.md for sources and search limits.

All 117 active modules were freshly compiled after their project caches were removed;
86 inherited source modules are unchanged. Pinned mathlib caches were reused.
All 543 theorem/lemma declarations are axiom-audited; 127 are new support,
universal, concrete and benchmark declarations, not independent discoveries.
Only propext, Classical.choice and Quot.sound occur. Runtime: Lean 4.34.0-rc2,
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06, one thread, warnings as errors.
Final successful source/attempt/log/compiled-output/direct-dependency hashes match.
Three invalid Lean controls rejected; 1,068 diagnostic assertions and nine expected
producer rejections passed. Final Mathbox computation manifest validation passed.
Failures remain preserved. This is a clean build and adversarial self-review,
not an independent external audit. The PowerShell launcher was not run on Windows.

## Reproduction and future work

Read the active README for the proof-producing reference CLI and clean-build command.
Runtime binaries are distributed separately; restoration metadata is retained.
Resource caps may prevent completion. Python success remains provisional until its
exported explicit Lean instance compiles. No bounded-hardware guarantee follows
from the ideal finite-fuel theorem.

The scoped first-release theorem and artifact are complete. Future capabilities
are separate: performance at meaningful scale, faster full certificate checking,
rounded selective updates/approximate selection, hierarchy-changing refinement,
sequential filtering, uncertain inputs, parser refinement, point-valued factors or
sampling, and hardware arithmetic. Independent external review is still welcome.
Do not reopen completed foundations without identifying a concrete defect, and do
not treat these extension goals as silently proved by the first-release label.
