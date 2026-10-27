# Block 15 — Source-bound-free generalized discrepancy

Komorebi P. · 14 September 2026 · Sufficient Resolution v0.15.0

This block adds **41 theorem/lemma declarations in six production modules** and
**45 enumerated named declarations**. The selected v0.14.0 predecessor has 913
theorems in 81 modules; the cumulative source inventory is therefore **954
theorems in 87 modules and 1107 enumerated names**. Counts include supporting
lemmas, definitions, examples and classical specializations. They are not counts
of independent discoveries or novelty claims.

## Mathematical contract

Let `A : G →L[ℝ] V` be the fixed true bounded operator and `C : G →L[ℝ] V` an
available bounded model on the same complete real inner-product spaces. Let
`v : V` be observed data. Write `eta ≥ 0` for a valid true-data allowance and
`delta ≥ 0` for a valid whole-operator allowance `‖C-A‖ ≤ delta`.

Unlike block 14, **the acceptance predicate contains no supplied source norm cap
M**. Instead it uses the candidate-dependent allowance

    candidateNoise eta delta x = eta + delta * ‖x‖.

A generalized accepted source is either the small-data zero source, or an actual
positive-parameter Tikhonov source whose model fitting residual satisfies

    candidateNoise eta delta x
      ≤ ‖C x-v‖
      ≤ tau * candidateNoise eta delta x.

The external truth assumptions remain external: a successful residual test does
not infer `‖C-A‖ ≤ delta` or `‖A p-v‖ ≤ eta`.

## 1. Candidate-dependent self-bounding

`GeneralizedDiscrepancy.regularized_norm_domination` is the central theorem.
Let `p` be any feasible comparison source satisfying

    ‖C p-v‖ ≤ eta + delta*‖p‖.

If an actual Tikhonov candidate `x` satisfies the generalized lower discrepancy
bound

    eta + delta*‖x‖ ≤ ‖C x-v‖,

then

    ‖x‖ ≤ ‖p‖.

The proof compares literal Tikhonov objectives. If `‖x‖>‖p‖`, monotonicity of the
candidate-dependent allowance makes the comparison source fit no worse than the
candidate, while the positive quadratic penalty is strictly smaller, contradicting
minimality.

Consequences under the true bounds `‖C-A‖≤delta` and `‖A p-v‖≤eta` include

    Accepted C v eta delta tau x  ==>  ‖x‖ ≤ ‖p‖,

and, for `tau ≥ 0`,

    ‖A x-A p‖ ≤ (tau+1) * (eta + delta*‖p‖).

Thus the accepted source automatically recovers the source-norm domination that
block 14 previously received through an external `M`.

Principal declarations:
`candidateNoise_nonneg`, `candidateNoise_mono_norm`, `accepted_fit`,
`accepted_lower`, `regularized_norm_domination`, `accepted_norm_control`,
`accepted_true_residual`, `accepted_consistent`.

## 2. Feasibility-aware parameter selection

Removing `M` from the acceptance predicate does **not** make parameter existence
automatic. The block therefore keeps feasibility separate from acceptance.

A sufficient pointwise condition is

    delta * ‖p‖ < (tau-1) * eta,

with `eta>0`, `tau>1`, together with the true operator/data bounds. It implies

    ‖C p-v‖ < tau*eta.

In the large-data branch `tau*eta < ‖v‖`, the inherited discrepancy existence
theorem supplies a positive parameter with residual exactly `tau*eta`. The new
self-bounding theorem then shows the resulting source satisfies the candidate-
dependent generalized band. The small-data branch returns zero.

`GeneralizedDiscrepancySelection.selectedSource` is the resulting total selected
source under these explicit hypotheses. Lean proves both acceptance and

    ‖selectedSource ...‖ ≤ ‖p‖.

The source `p` appears in this theorem-level existence proof; it is not an argument
to the generalized `Accepted` predicate itself.

Principal declarations:
`relative_accuracy_gives_strict_fit`, `relative_accuracy_requires_positive_margin`,
`positive_parameter_source`, `exists_accepted`, `selectedSource`,
`selectedSource_accepted`, `selectedSource_norm`.

## 3. Strong consistency without an external source cap

For a fixed true operator `A`, fixed identifiable source `p ∈ ker(A)⊥`, changing
available operators `C_i`, data `v_i`, and accepted generalized sources `x_i`,
Lean proves

    eta_i → 0,
    delta_i → 0
      ==> x_i → p,

provided the true bounds and acceptance hypotheses hold. The proof uses the
self-generated norm bound `‖x_i‖≤‖p‖` and the true-operator residual estimate above.

For an arbitrary true source `g`, the selected family converges to

    P_(ker A)⊥ g,

and its source-error norm tends to

    ‖P_(ker A) g‖.

The true kernel ambiguity is therefore preserved; removing `M` does not claim to
recover information annihilated by `A`.

Principal declarations:
`selected_consistent`, `selected_norm_control`,
`selected_true_residual_tendsto_zero`, `selected_from_true_source_consistent`,
`selected_error_norm_limit`.

## 4. Inexact computed sources

`GeneralizedInexact.NearAccepted` allows a computed source `x` to lie within a
source-space allowance `kappa` of an exact generalized accepted companion `y`.
Lean proves

    ‖x‖ ≤ ‖p‖ + kappa,

and

    ‖A x-A p‖
      ≤ ‖A‖*kappa + (tau+1)*(eta+delta*‖p‖).

For families,

    eta_i → 0,
    delta_i → 0,
    kappa_i → 0
      ==> x_i → p.

The implementation does not infer a `NearAccepted` witness from an arbitrary
numerical solver; this is a theorem about sources with the stated certificate.
Under the explicit source condition `p=A* w`, a squared source-error rate is also
proved.

Principal declarations:
`exact_is_near`, `near_allowance_nonneg`, `near_norm_control`,
`near_true_residual`, `near_consistent`, `near_source_condition_rate`.

## 5. Checkable relative model-accuracy conditions

A convenient sufficient condition for feasibility is

    delta ≤ gamma*eta,
    gamma*‖p‖ < tau-1,
    eta>0.

Lean derives

    delta*‖p‖ < (tau-1)*eta,

then supplies accepted sources and the corresponding consistency theorem. This
makes the scale relationship explicit: operator accuracy must improve relative
to the data-noise allowance at a rate compatible with the source being recovered.

Principal declarations:
`relative_accuracy_of_scaled_error`, `exists_accepted_of_scaled_error`,
`selected_consistent_of_scaled_error`, `fixed_ratio_margin`,
`zero_source_relative_accuracy`.

## 6. Exact feasibility and nonfeasibility examples

The identity-model scalar example is fully checked. With exact model `A=C=I`,
positive `eta`, and a suitable positive Tikhonov parameter, the candidate satisfies
the generalized discrepancy predicate and the relative-accuracy condition.

More importantly, unconditional feasibility is formally false. Take

    true A = I,
    available C = 0,
    p = v = 1,
    eta = 1/10,
    delta = 1,
    tau = 2.

The true data and operator allowances are valid, but for every positive parameter
the model's regularized source is zero and its residual is one. The generalized
candidate allowance is only `1/10`, so no generalized accepted source exists.
Lean proves both the valid true bounds and `zero_model_not_accepted`.

Therefore the block does **not** replace the old `M` assumption with a hidden
unconditional-existence assumption. Acceptance is self-bounding; feasibility still
requires an explicit model-accuracy condition or a separate certificate.

## 7. Exact-rational finite controls

Run

    python scripts/check_generalized_discrepancy.py

The deterministic suite uses `fractions.Fraction` and seed 20260914. It checks 120
scalar true/model/noise systems satisfying the relative-accuracy contract: 108 use
a positive discrepancy parameter and 12 use the small-data branch. It performs 752
exact assertions. An additional 32 zero-model parameters are sampled only as an
implementation diagnostic; the universal nonfeasibility result is the separate Lean
theorem.

These finite checks are implementation evidence, not proof of the general theorems.
Python and its arithmetic implementation are not formally verified.

## Verification boundary

Read `VERIFICATION_SUMMARY.md` and the actual report under
`verification/release_v0.15.0/`. The main run freshly compiled and same-kernel
replayed the six new modules plus their complete project dependency closure. A
separate source-only replay is recorded if its report is present. Imported Mathlib
artifacts are reused from the pinned runtime; `leanchecker` uses the same Lean kernel,
not an independently implemented verifier.

No theorem here infers true noise/operator allowances from fitting data, proves
unconditional parameter existence for poor models, verifies the numerical parser or
search algorithm, establishes nonlinear/positive/integral realization, or supplies
an arithmetic/Langlands correspondence.
