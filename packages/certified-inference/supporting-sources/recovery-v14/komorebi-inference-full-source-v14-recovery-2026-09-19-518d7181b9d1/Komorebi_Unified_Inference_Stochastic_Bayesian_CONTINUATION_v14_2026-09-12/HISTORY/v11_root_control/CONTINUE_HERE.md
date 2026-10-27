# Komorebi Unified Inference / Stochastic / Bayesian — v11

Active release: CHECKED_RELEASES/FD_Roundoff_Aware_Posterior_Solver_v0.1.0_Checked.

## Newly closed and Lean-checked

1. Entire rounded gain-update graph: compute B+tau*(P H^T-B S) with the retained
   outward dyadic ball operations, including rounded model/residual evaluation
   and rounded correction. The executable precision policy proves entrywise
   update error at most h=2^(-t). Precision depends on the current represented B.
2. Rounded iteration tracking: with q the inherited squared contraction factor,
   d the number of gain entries, and the same initial gain for both trajectories,

       ||Bhat_n-Bexact_n||_F^2 <= 6 d h^2/(1-q)^2.

   Additive residual forcing is explicit. Fixed precision is NOT assumed exact.
3. Distribution-level progress plus floor. With w=(sigma+||v||^2)/sigma^2,
   a(B)=||P H^T-B S||_F^2*w and J=12 d ||S||_F^2*w/(1-q)^2,

       W2^2(actualPosterior,JosephGaussian(Bhat_n))
           <= 2 q^n a(B0)+J h^2.

4. Computed local-accuracy and horizon: t=precisionFor(J,eps^2/8),
   N=solverFuel(B0,eps/4). Every n>=N has exact certificate score <=eps^2/4.
5. Actual rounded-update/rounded-verifier solver: try any finite certificate
   precision probes followed by a sufficient verification fallback at each gain.
   On failed verification execute the rounded update. The computed finite horizon
   guarantees success for every positive rational tolerance, valid fixed model and
   complete self-adjoint rational packet geometry. A separate theorem identifies
   the returned gain as an actual rounded iterate within the fuel.

Main declarations, namespace Komorebi.RoundoffSolver:

    rounded_step_entry_error
    roundedGain_tracking
    rounded_score_geometric
    rounded_iterate_posterior_bound
    rounded_solver_reaches_posterior_tolerance
    rounded_solver_gain_origin

## Checked execution and boundary examples

Scalar P=H=R=1, m=0,y=1, B0=0, eps1/20:
t=20, conservative fuel23040, rounded iterate4=16967772033/34359738368.
The program returns that gain with 12-bit verification, score729/2097152,
and W2<=1/20. The rounded gain is proved different from exact iterate40/81.

Singular two-state prior P=ones(2), H=R=I, y=(1,-1), rotated packets, eps1/4:
t=21, fuel8534, rounded iterate3=(1372190511463/4398046511104)*ones(2).
The program returns that gain with 12-bit verification, score215859/4194304,
and W2<=1/4. Actual program returns and posterior guarantees are kernel-checked.

A fixed zero-bit scalar update maps zero to zero forever, with residual energy1.
This counterexample is checked and must not be discarded when discussing precision.

## Arithmetic and proof boundaries

Gain UPDATE EXECUTION IS NOW ROUNDED, unlike the v10 hybrid. Its exact ideal
trajectory is a proof reference, not executed to obtain the gains. Nevertheless,
model/trace-step preprocessing, precision budgets, fuel planning and terminal
comparisons use exact rational arithmetic. The initial fuel uses the exact initial
residual score. Dyadic integer parts are unbounded; finite sums follow the exact
retained ball-node semantics. This is not a theorem about IEEE-754, BLAS, overflow,
or unknown inputs. Python results are provisional until their exported Lean
instances compile. Parser/exporter fidelity and hardware-resource bounds are open.

The certified output is the mathematical Joseph Gaussian of the represented gain,
not yet a certified array of rounded posterior parameters or a sampling executable.
Explicit-versus-canonical posterior scope, singular-prior validity and positive
noise-floor assumptions are unchanged. Models/packets are fixed. No optimality,
stepwise true-error monotonicity, sequential filtering, new Ito result, performance
superiority or literature novelty is asserted.

## Strongest next bounded targets

Certify the output representation: outward-rounded posterior mean/covariance
arrays, or a separately specified sampler, rather than just their mathematical
Gaussian law. Another useful route is an independent clean release audit and
carefully scoped benchmarking. Larger extensions remain model/packet-changing
adaptation, filtering-kernel recursion, and uncertain-input semantics.
Do not reopen already checked conditioning, transport, packet-energy, exact-solver,
precision-sufficiency or rounded-update closure without an identified error.

## Verification

78 active modules passed, including 67 unchanged inherited modules freshly checked.
All 389 theorem/lemma declarations, including 63 new declarations, received an
axiom audit containing only propext, Classical.choice and Quot.sound. No active
placeholders, custom axioms or native proof shortcuts. Six corrected draft checks
and one interrupted example invocation remain in the failure records. Twelve
exact matrix diagnostics passed 1557 assertions and 8 producer rejection tests.
Three invalid Lean controls were rejected. Counts are not discovery counts.

Pins: Lean4.34.0-rc2, mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06,
one thread, warnings as errors. The active dependency slice was rebuilt; pinned
Mathlib caches reused; unrelated historical modules preserved rather than rebuilt.
All 2217 inherited checked-release files are unchanged.
