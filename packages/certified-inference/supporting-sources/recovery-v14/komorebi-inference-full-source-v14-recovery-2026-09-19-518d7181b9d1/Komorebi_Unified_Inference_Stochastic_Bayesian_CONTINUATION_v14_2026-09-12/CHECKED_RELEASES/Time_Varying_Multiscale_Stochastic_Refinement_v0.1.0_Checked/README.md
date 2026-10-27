# Time-Varying Multiscale Stochastic Refinement — Lean Checked

This is the sharp finite-horizon successor to `Finite_Time_Multiscale_Stochastic_Refinement_v0.1.0_Checked`.

## Principal theorem

Let `D : ℝ → (T →L[ℝ] T)` solve

\[
D'(t)=A D(t)+D(t)B+R(t).
\]

The checked pointwise Duhamel formula is

\[
D(t)x-e^{(t-t_0)A}D(t_0)e^{(t-t_0)B}x
=
\int_{t_0}^{t}e^{(t-s)A}R(s)e^{(t-s)B}x\,ds.
\]

Consequently, if `‖R(s)‖ ≤ ε(s)`, Lean proves

\[
\|D(t)\|
\le
\|e^{(t-t_0)A}\|\,\|D(t_0)\|\,\|e^{(t-t_0)B}\|
+
\int_{t_0}^{t}
\|e^{(t-s)A}\|\,\varepsilon(s)\,\|e^{(t-s)B}\|\,ds.
\]

## Multiscale stochastic specialization

For an orthogonal fine refinement of coarse projectors, the forcing envelope is not replaced by a worst-case constant. It is the actual time-dependent descendant leakage budget

\[
\varepsilon_{ab}(s)
=
\sum_{\rho(c)=a,\rho(d)=b}
\|F_c R(s)F_d\|.
\]

With covariance residual forcing

\[
R(s)=R_A(s)P(s)+P(s)R_A(s)^*+R_Q(s),
\]

this gives a semigroup-weighted history certificate for accumulated coarse covariance leakage.

## Why this is sharper than the previous checkpoint

The earlier theorem used a single constant `ε` on the full time horizon and Grönwall. This theorem retains the entire temporal profile of fine residual generation and the actual left/right semigroup amplification factors. It is therefore both more informative and no weaker.

## Formalization note

A first direct operator-valued product-derivative proof encountered a Lean typeclass-instance diamond in the continuous-linear-endomorphism space. The final proof is pointwise in the Banach space and then lifted to operator norm. No mathematical hypothesis was weakened by this implementation change.

## Audit

Representative central theorems depend only on the ordinary Lean/mathlib foundations:

- `propext`
- `Classical.choice`
- `Quot.sound`

No `sorry`, `admit`, or custom axiom is present.
