# Finite-Time Multiscale Stochastic Refinement v0.1.0 — Checked

This package extends the abstract stochastic projector-refinement theorem with a finite-horizon Grönwall stability result.

## Main objects

For a coarse projector family `C`, fine orthogonal refinement `F`, and refinement map `ρ`, define the fine descendant norm budget below a coarse corner `(a,b)` by

`Σ_{ρ(c)=a,ρ(d)=b} ‖F_c R F_d‖`.

Here `R` is the named residual covariance forcing.

If `A0` commutes with the coarse projectors, the coarse covariance-error corner closes under the baseline propagation:

`C_a (A0 D + D A0† + R) C_b`.

Lean proves the operator-norm estimate

`‖C_a (A0 D + D A0† + R) C_b‖ ≤ 2 ‖A0‖ ‖C_a D C_b‖ + descendantBudget(R,a,b)`.

## Finite-horizon theorem

Let `D(t)` be a covariance-error operator and suppose its coarse corner is continuous on `[t0,t1]`, has the supplied right derivative, and obeys

`Ddot = A0 D + D A0† + R`.

If the fine descendant residual budget is uniformly bounded by `ε`, Lean proves

`‖C_a D(t) C_b‖ ≤ gronwallBound ‖C_a D(t0) C_b‖ (2 ‖A0‖) ε (t-t0)`.

If the initial corner is zero and `A0 ≠ 0`, this becomes the explicit exponential certificate

`‖C_a D(t) C_b‖ ≤ ε/(2 ‖A0‖) * (exp(2 ‖A0‖ (t-t0)) - 1)`.

If `A0 = 0`, Lean proves the linear form

`‖C_a D(t) C_b‖ ≤ ε (t-t0)`.

## Stochastic specialization

The package specializes `R(t)` to the covariance residual forcing

`RA(t) P(t) + P(t) RA(t)† + RQ(t)`

and proves the same Grönwall and explicit exponential bounds with the fine multiscale budget computed directly from these residual covariance corners.

## Interpretation

The theorem separates:

1. propagation of already accumulated coarse covariance error, controlled by `2 ‖A0‖`; and
2. fresh covariance leakage, measured entirely by the sum of fine descendant residual-corner norms.

Thus a multiscale residual certificate controls accumulated coarse stochastic covariance error on a finite time interval.

## Verification

Checked with the preserved Komorebi portable Lean runtime:

- Lean 4.34.0-rc2
- pinned mathlib cache
- warnings treated as errors
- final compiler exit code: 0
- no `sorry`
- no `admit`
- no custom `axiom` declarations

Representative `#print axioms` checks report only the standard Lean/Mathlib foundations `propext`, `Classical.choice`, and `Quot.sound`.

## Boundary

The result assumes the covariance-error differential equation and the required right-derivative/continuity hypotheses. It does not itself derive that equation from an Itô integral. The residual forcing may be time dependent, but the displayed Grönwall result uses a uniform scalar upper bound `ε` on the fine descendant budget over the interval. A sharper future extension would retain the full time-varying budget inside a variation-of-constants integral.
