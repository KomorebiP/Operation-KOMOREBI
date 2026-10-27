# Block 13 — Inexact discrepancy certificates

Komorebi P. · 14 September 2026 · Sufficient Resolution v0.13.0

## Mathematical contract

A fixed bounded linear operator A:G→V between complete real inner-product spaces.
For λ>0, the existing constructed Tikhonov source is

xλ = (A* A + λ I)⁻¹ A* v.

The supplied computed source x need not satisfy the normal equation. Its **actual**
normal residual is r=(A* A + λ I)x−A*v. The measured fitting norm m need not be exact,
but an enclosure |m−‖Ax−v‖|≤ω must be justified. A true-data noise allowance η is a
separate hypothesis: ‖Ag−v‖≤η for the intended fixed source g.

No closed range, finite dimension, injectivity, or separately prescribed parameter
schedule is required for the positive mathematical results. The scalar examples
and finite rational evaluator do not replace these universal proofs.

## 1. Two different residual scales

`InexactResidual.correction_identity` and `correction_bound` prove

x−xλ = (A*A+λI)⁻¹r,
‖x−xλ‖ ≤ ‖r‖/λ.

`image_resolvent_bound_squared` and `image_resolvent_bound` prove the sharper data bound

4λ ‖A(A*A+λI)⁻¹r‖² ≤ ‖r‖²,
‖A(x−xλ)‖ ≤ ‖r‖/(2√λ).

The proof uses the actual normal-operator energy identity and completes a square.
It does not multiply the source bound by ‖A‖. `fitting_residual_difference` applies
the reverse triangle inequality to obtain

|‖Ax−v‖ − ‖Axλ−v‖| ≤ ‖r‖/(2√λ).

Source error and fitting error therefore need distinct budgets.

## 2. Protected measurements

Suppose ‖r‖≤λκ and ‖r‖≤2√λ ξ, and |m−‖Ax−v‖|≤ω.
If

η+ω+ξ ≤ m ≤ τη−ω−ξ,

then the exact source xλ satisfies

η ≤ ‖Axλ−v‖ ≤ τη,

and ‖x−xλ‖≤κ. These conclusions are `measured_band_transfer` and
`InexactDiscrepancy.measured_certificate`.

The measured interval is nonempty exactly when

2(ω+ξ) ≤ (τ−1)η.

This concerns available scalar margin, not existence of a computed source meeting
all certificate fields. The midpoint ((τ+1)η)/2 is in the interval whenever that
condition holds. `relative_margins` supports allocation using multiples of η.

## 3. General near-accepted outputs and mixed branches

`NearAccepted A v η τ κ x` means there exists an **actual** output y accepted by the
inherited discrepancy rule, with ‖x−y‖≤κ. The witness is not an assumed new inverse.
It is produced from normal residual bounds and protected fitting measurements.

The small-data branch is also certified: if ‖v‖≤τη and ‖x‖≤κ, then y=0 is an
accepted comparison output. A measured bound m+ω≤τη suffices when |m−‖v‖|≤ω.
Thus arbitrary mixtures of the small-data and positive-parameter branches are
covered by the same convergence theorem.

With P=P_(ker A)⊥, the checked finite estimates include

‖x‖ ≤ ‖Pg‖+κ,
‖Ax−Ag‖ ≤ (τ+1)η+‖A‖κ,
‖P_ker A x‖ ≤ κ.

The final estimate distinguishes numerical kernel leakage from the true source's
irrecoverable kernel component. Perturbing a certified output by at most h changes
its source-error budget from κ to κ+h.

## 4. Strong consistency of inexact solves

`InexactConsistency.near_consistent` proves, for arbitrary filter-indexed families,

‖Ag−vᵢ‖≤ηᵢ, NearAccepted(...,κᵢ,xᵢ), ηᵢ→0, κᵢ→0
⇒ xᵢ→Pg.

The proof selects the exact accepted witnesses, applies the inherited exact
consistency theorem to them, and uses the vanishing correction estimate.

`scaled_normal_consistent` specializes this to the **actual** scale
κᵢ=‖rᵢ‖/λᵢ and data budget ξᵢ=‖rᵢ‖/(2√λᵢ), with the stated measurement margins.
No extra assumption λᵢ→0 or ηᵢ/√λᵢ→0 is imposed. The rule and its protected margins
are indispensable hypotheses, not a guarantee for arbitrary λᵢ.

`noise_scaled_solver_consistent` gives the sufficient stopping tolerance
‖rᵢ‖≤λᵢ cηᵢ for a fixed c, retaining the image and measurement margins.

`near_error_norm_limit` retains

‖xᵢ−g‖→‖P_ker A g‖.

A source-condition rate is retained too: if g=A*w and a nonnegative R satisfies
2‖w‖(τ+1)η≤R², then ‖x−g‖≤κ+R. No rate for arbitrary identifiable sources is inferred.

## 5. Squared certificate soundness

`PositiveCertificate` is an explicit record with positive λ, nonnegative ρ,κ,ξ,ω,m,
and the following fields:

‖r‖²≤ρ²,
ρ²≤(λκ)²,
ρ²≤4λξ²,
max(0,m−ω)²≤‖Ax−v‖²≤(m+ω)²,
η+ω+ξ≤m≤τη−ω−ξ.

`certificate_sound` proves that this record implies NearAccepted for the actual
source. `certificate_consistent` and `certificate_error_limit` establish convergence
and the kernel-ambiguity limit for any family of such records and valid vanishing
noise/source budgets.

The squared enclosure is proved equivalent to |m−‖Ax−v‖|≤ω. No replacement norm
or numerical square root is used to make the claim true.

If the normal residual itself is evaluated approximately, the additional result
`uncertain_normal_certificate` accepts rhat with ‖r−rhat‖≤ν, ‖rhat‖≤ρhat and uses
ρhat+ν as the envelope in both budgets. This does not estimate the forward operator.

## 6. Checked sharpness and failure examples

- The identity scalar operator at λ=1 attains the image correction bound.
- The zero scalar operator attains the source correction bound.
- For fixed A=0, λ=s>0, data v=s, candidate x=1: normal-residual norm=s and fitting
  norm=s tend to zero as s→0, but x remains one unit from the minimum-norm source.
  The example also has a valid noise allowance η=s relative to the true source 0.
  The raw discrepancy lies in [η,τη] for any τ≥1. The scaled residual ‖r‖/λ=1 does
  not vanish. Thus unscaled normal residuals and an apparent discrepancy band alone
  do not force correct minimum-norm convergence.
- Separate identity examples falsely pass an unprotected discrepancy interval if
  the solver margin or the measurement margin is omitted.
- Excessive error budgets can leave no protected scalar measurement interval.

These are actual real-operator Lean statements, not finite empirical observations.

## 7. Concrete nonexact certificate

The Lean record `InexactExamples.scalarCertificate` and the rational CLI both use
A=1, v=4, λ=1, x=201/100, η=1, τ=3, κ=1/50, ρ=1/50, ξ=1/100, m=2, ω=1/100.
The exact comparison is xλ=2, while the candidate is genuinely different.

Normal residual: 1/50. Actual source and image correction: 1/100.
Actual fitting norm: 199/100. Reported measurement: 2 with error allowance 1/100.
Protected interval: [51/50,149/50]. The exact fitting norm 2 lies in [1,3].

The CLI additionally demonstrates an inexact normal evaluation rhat=1/100 with
error allowance ν=1/100. The formal generic theorem covers that extra enclosure.

## Status boundaries

The operator and ambient real Hilbert metrics are fixed. η must be a valid true-data
noise allowance. The scalar margin certificate does not infer unknown noise,
operator error, or universal feasibility. κ→0 is sufficient, not asserted necessary
in every favorable fixed-operator case. Infinite limits are separate Lean proofs;
the rational algorithms and their parsers are tested but not formally verified.
No positive, integral, nonlinear, arithmetic, or Langlands realization is established.
