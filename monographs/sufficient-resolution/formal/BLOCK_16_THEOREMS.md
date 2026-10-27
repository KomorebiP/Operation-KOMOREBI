# Block 16 — Calibration-to-operator certification

Komorebi P. · 14 September 2026 · Sufficient Resolution v0.16.0

This block adds **44 theorem/lemma declarations in six production modules** and
**52 enumerated named declarations**. The selected v0.15.0 predecessor has 954
theorems in 87 modules and 1107 enumerated names. The cumulative source inventory
is therefore **998 theorem/lemma declarations in 93 modules and 1159 enumerated
named declarations**. Counts include helpers, definitions, examples, and classical
specializations; they are not counts of independent discoveries or novelty claims.

## Mathematical contract

A calibration synthesis `U : K →L[ℝ] G` is allowed to be redundant. The positive
exact-frame theory assumes a bounded reconstruction `R : G →L[ℝ] K` with

    U.comp R = id.

For true and model operators `A,C : G →L[ℝ] V`, and a measured calibration-response
operator `Y : K →L[ℝ] V`, the calibration errors are

    ||Y - A U|| <= etaCal,
    ||Y - C U|| <= fit.

The theorem does not infer `etaCal`; it converts a justified calibration-truth
allowance and measured model fit into a whole-operator allowance.

## 1. Split and redundant calibration frames

`CalibrationFrame.Frame` contains `synthesis`, `analysis`, and the exact reconstruction
identity. The synthesis need not be injective or square. Lean proves

    T = (T U) R,
    A-C = ((A U)-(C U)) R,
    ||A-C|| <= ||A U-C U|| ||R||.

Hence

    ||C-A|| <= (etaCal+fit) ||R||.

If a separate bound `||R|| <= kappa` is supplied, Lean proves the immediately
checkable specialization

    ||C-A|| <= (etaCal+fit) kappa.

Exact calibration identifies the global operator: if `Y=A U` and `Y=C U`, then
`A=C`. `ofEquiv` recovers the square/invertible calibration case as a specialization.

Principal declarations:
`CalibrationFrame.Frame.factor_through_frame`, `difference_factorization`,
`difference_norm_le`, `measured_operator_bound`,
`measured_operator_bound_of_analysis_bound`, `exact_calibration_identifies`,
`CalibrationFrame.equiv_calibration_bound`.

## 2. Calibration-generated uncertainty enters the existing recovery theory

Define

    generatedDelta F etaCal fit = (etaCal+fit) ||F.analysis||.

`CalibrationRecovery.generated_operator_bound` proves that this quantity is a valid
whole-operator allowance. If data noise, calibration-truth error, and model-calibration
fit all tend to zero, then `generatedDelta` tends to zero.

For any family of sources already accepted by the source-bound-free generalized
discrepancy rule using this generated allowance, Lean proves strong convergence to
the fixed identifiable true source. For an arbitrary true source `g`, the source-error
norm tends to the norm of its true-kernel component.

Principal declarations:
`generatedDelta_tendsto_zero`, `calibrated_norm_control`, `calibrated_true_residual`,
`calibrated_consistent`, `calibrated_error_norm_limit`.

## 3. Parameter feasibility and selection from calibration

The calibration allowance can be fed into the existing feasibility-aware discrepancy
selector. Under

    generatedDelta * ||p|| < (tau-1) eta,

with positive data allowance and `tau>1`, Lean proves existence of an accepted source,
constructs a noncomputable selected source, and proves its norm is at most `||p||`.
A ratio form is also checked:

    generatedDelta <= gamma eta,
    gamma ||p|| < tau-1.

For changing calibration/model data, the selected sources converge when the data,
calibration-truth, and model-fit allowances vanish and the pointwise feasibility
condition holds.

Principal declarations:
`CalibrationSelection.exists_accepted_from_calibration`, `selectedSource_accepted`,
`selectedSource_norm`, `exists_accepted_of_calibration_ratio`,
`calibrated_selected_consistent`.

## 4. Hierarchical calibration

Split calibration frames compose. If `E : J -> K` and `F : K -> G` are split frames,
then their composite is a split frame `J -> G`, with reconstruction map equal to the
composition of the stage analyses. Lean proves

    ||analysis(F ∘ E)|| <= ||analysis(E)|| ||analysis(F)||,

and therefore

    ||C-A|| <= (etaCal+fit) ||analysis(E)|| ||analysis(F)||.

This is a genuine multistage calibration theorem, not a restatement that each stage is
separately invertible.

Principal declarations:
`CalibrationHierarchy.comp`, `comp_analysis_norm_le`, `hierarchical_operator_bound`.

## 5. Approximate reconstruction frames

Exact frame reconstruction can be relaxed. Let `U : K -> G`, `R : G -> K` satisfy

    ||I - U R|| <= rho,     rho < 1.

For any bounded `T : G -> V`, Lean proves

    ||T|| <= ||T U|| ||R|| / (1-rho).

Thus measured calibration data imply

    ||C-A|| <= (etaCal+fit) ||R|| / (1-rho).

The proof uses the exact decomposition

    T = (T U) R + T (I-U R).

At `rho=0` it reduces to the exact split-frame estimate. The theorem does not claim a
useful bound when the reconstruction defect reaches one.

Principal declarations:
`ApproximateCalibration.approximate_factorization`, `approximate_frame_bound`,
`measured_approximate_operator_bound`, `exact_reconstruction_specialization`.

## 6. The unobserved-direction obstruction

The boundary is formally sharp in kind. Calibrate only the first coordinate of
`R^2` via

    U(t) = (t,0).

For any scalar `s`, define

    C_s(x,y) = s y.

Lean proves

    C_s U = 0

for every `s`, while `||C_s||=s` for nonnegative `s`. Consequently, for every real
`M` there exists an operator agreeing perfectly on the entire calibration subspace but
having norm larger than `M`.

It also proves that this partial calibration map is not surjective. Therefore exact
calibration on a proper source subspace cannot control untested directions.

Principal declarations:
`CalibrationExamples.partial_not_surjective`, `unseen_comp_partial`, `unseen_norm`,
`arbitrarily_large_unseen_error`, `perfect_partial_calibration_unbounded`.

A redundant positive example is also checked: two calibration coordinates synthesize a
one-dimensional source and a bounded analysis recovers it exactly.

## 7. Exact-rational executable companion

Run

    python scripts/calibration_certificate.py --input examples/calibration_input.json --output certificate.json
    python scripts/check_calibration.py

The checker receives the calibration synthesis/reconstruction matrices, measured
calibration outputs, candidate model, and an external calibration-truth allowance. It
does **not** receive the true operator. It uses conservative exact-rational entrywise-l1
matrix bounds to generate a finite-dimensional operator-error allowance, including the
approximate-frame factor `1/(1-rho)`.

The deterministic suite checks 72 systems: 36 approximate-frame cases and 24 redundant
exact-frame cases, with 289 exact assertions and six malformed/nonspanning controls
rejected. These are implementation checks in a conservative matrix norm, not proofs of
the generic Hilbert operator-norm theorems. Python and parsing are not formally verified.

## Boundaries

The calibration-truth allowance remains external. This block does not derive it from
individual noisy calibration samples, stochastic assumptions, or physical instrumentation.
It does not infer operator accuracy from a nonspanning calibration family. The numerical
checker is not Lean-verified. No nonlinear, positive, integral, arithmetic, or Langlands
realization theorem follows.
