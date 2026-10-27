# Unified Inference Lean v0.5.0 — Checked

This checkpoint extends v0.4.0 with the continuous-time approximate-lumpability/Duhamel block.

## Verification

All final Lean source was checked with warnings treated as errors under the preserved portable runtime:

- Lean / Lake: `leanprover/lean4:v4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`

Final source inventory:

- 88 theorem declarations
- 53 definitions/abbreviations
- 1 structure
- 0 `sorry`
- 0 `admit`
- 0 custom `axiom` declarations

The final warning-as-error compile and representative `#print axioms` audit both return exit code 0. Representative central results depend only on ordinary Lean/Mathlib foundations (`propext`, `Classical.choice`, `Quot.sound`).

## New v0.5 continuous Duhamel block

For bounded linear generators `Q`, `Qbar` and an intertwiner candidate `C`, define the defect

`E = Q.comp C - C.comp Qbar`.

The source now defines the interpolation path

`F(s) = exp(sQ) (C (exp((t-s)Qbar) x))`

and proves directly that

`F'(s) = exp(sQ) (E (exp((t-s)Qbar) x))`.

By the Banach-valued fundamental theorem of calculus this gives the pointwise Duhamel identity

`exp(tQ)(Cx) - C(exp(tQbar)x) = ∫_0^t exp(sQ) E exp((t-s)Qbar) x ds`.

Under contraction assumptions

`‖exp(uQ)‖ ≤ 1` and `‖exp(uQbar)‖ ≤ 1` for `0 ≤ u ≤ t`, Lean proves the operator-norm bound

`‖exp(tQ) ∘ C - C ∘ exp(tQbar)‖ ≤ t ‖E‖`.

It also proves the pointwise state estimate

`‖exp(tQ)(Cx) - C(exp(tQbar)x)‖ ≤ t ‖E‖ ‖x‖`,

and the unit-state specialization

`‖...‖ ≤ t ‖E‖` whenever `‖x‖ ≤ 1`.

This is the continuous analytic counterpart of the discrete exact residual telescoping identity already present in v0.4.

## Existing checked layers retained

The same source retains the previously checked finite Bayes, strong lumpability, continuous exact exponential intertwining, packet stochastic-moment algebra, direct-sum/Joseph Kalman algebra, Gaussian packet independence, Caputo commutation, Volterra packet reconstruction/path composition, scalar and operator-valued memory error bounds, scalar and operator-valued finite-horizon resolvent convergence, finite exponential-memory Markovian lifts, and recursive augmented-memory Kalman closure.

## Current boundary

The major semantic gaps are now concentrated in two areas:

1. derivation of the linear SDE moment equations from a developed Itô/stochastic-integral library;
2. full measure-theoretic linear-Gaussian conditioning proving the Kalman update as conditional Gaussian Bayes.

The pinned Mathlib contains Gaussian-law infrastructure and basic Brownian-motion material, but it does not currently provide the complete stochastic-integral / linear-observation conditioning results needed to close these two statements without a substantial new foundational development.

No surrogate is counted as those theorems.
