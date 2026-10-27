# Komorebi Unified Inference / Stochastic / Bayesian — v10

Active release: CHECKED_RELEASES/FD_Precision_Closure_v0.1.0_Checked.

## Newly closed and checked

1. Quantified outward-arithmetic precision budgets. The actual rounded evaluator
   obeys score_exact(B) <= score_p(B) <= score_exact(B)+C(B)*2^(-p), where C is
   computed from precision-independent magnitude/radius budgets through the full
   rectangular model/residual/packet graph. Lower inequality uses valid geometry.
2. Computed bit sufficiency. For delta>0,

       p* = Nat.log 2 (Nat.ceil (C/delta)) + 1

   makes C*2^(-p)<=delta for every p>=p*. Strict exact-certificate slack therefore
   forces actual successful return of certifyRounded. Score monotonicity in p
   is neither assumed nor asserted.
3. Hybrid total correctness. hybridSolve runs the retained exact solver at eps/2,
   chooses delta=eps^2/4, predicts sufficient certificate precision, and executes
   the outward evaluator. For every valid fixed model and complete packet
   geometry, eps>0 and arbitrary initial rational gain, it returns a candidate
   with passing exact checks and W2(actual posterior, Joseph approximation)<=eps.
   No extra user-supplied slack is required.
4. Early precision probing. hybridScheduled tries any finite list of probe
   precisions before the computed fallback. It also has successful termination
   and posterior soundness. certifyTagged records the actual successful precision.

Main declarations, namespace Komorebi.RoundedPosterior:

    rounded_score_inflation
    rounded_score_sandwich
    certifyRounded_of_slack
    hybrid_reaches_posterior_tolerance
    scheduled_hybrid_reaches_posterior_tolerance

## Current exact execution examples

Scalar P=H=R=1, m=0,y=1, initial gain0, eps1/20: four exact gain updates yield
B=40/81. Predicted precision61. Actual hybrid return and W2<=1/20 are kernel-checked.
Singular two-state P=ones(2), H=R=I,y=(1,-1), rotated packets, eps1/4: four exact
updates yield B=(203/625)ones(2), predicted precision72, actual return and W2 bound
kernel-checked. Scalar precision probes[4,12] return at12, before fallback61.
Four-bit score1/8 is rejected; twelve-bit score729/2097152 passes.

## Proof boundaries that remain explicit

The hybrid gain iteration is EXACT RATIONAL. Only certificate evaluation is
outward rounded. This is not a rounded gain-solver convergence theorem and does
not prove that fixed gain precision reaches arbitrary tolerances. Dyadic centers
and radii use unbounded integer parts and exact terminal scalar comparisons.
No IEEE-754/BLAS/overflow theorem, unknown-input model, verified parser/exporter,
rounded posterior-output array theorem, or hardware-resource guarantee is added.

The output certified is the mathematical Joseph Gaussian of the represented gain.
The explicit versus canonical posterior scope and singular-prior/noise-floor
hypotheses are unchanged. Model and packet families remain fixed. No resolved
model-changing solver, sequential filtering, general Ito foundation, optimal
coupling construction, performance superiority or literature novelty is claimed.

## Strongest next bounded target

Formalize additive roundoff forcing for actual rounded gain updates, derive a
quantitative error floor, and choose update precision so that this forcing and
certificate inflation together permit a positive posterior tolerance. Do not
reuse the exact Richardson contraction as though it proved rounded convergence.

Another application-level task is certifying the posterior output representation
(mean/covariance arrays or sampling) rather than only its exact mathematical law.
Larger separate routes are fixed-horizon filtering kernels, certified
model/packet-changing adaptation, independent full release review and benchmarks.
Do not reopen already checked Gaussian, metric, packet or precision-sufficiency
blocks without an identified problem.

## Verification and preservation

83 active modules passed, including 64 unchanged inherited modules freshly checked.
All 386 theorem/lemma declarations (82 new) passed axiom audit, using only
propext, Classical.choice, Quot.sound. These are declaration counts, not discovery
counts. Three concrete hybrid executions are kernel-checked. Independent exact
matrix diagnostics passed9651 assertions and14 input/export rejections. Three
invalid Lean controls were rejected. Preserve the failed draft/process records.

Pins: Lean4.34.0-rc2, mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06,
one thread, warnings as errors. Use MODULE_ORDER.json and the packaged block
verifier. No active placeholders, custom axioms or native proof shortcuts.
The remaining historical program was preserved, not all rebuilt.

All 1742 inherited checked-release files are byte-for-byte unchanged.
The v9 root documents are retained under HISTORY/v9_root_control.
Python PASS_HYBRID_PROVISIONAL is not a proof; compile the exported Lean module.
