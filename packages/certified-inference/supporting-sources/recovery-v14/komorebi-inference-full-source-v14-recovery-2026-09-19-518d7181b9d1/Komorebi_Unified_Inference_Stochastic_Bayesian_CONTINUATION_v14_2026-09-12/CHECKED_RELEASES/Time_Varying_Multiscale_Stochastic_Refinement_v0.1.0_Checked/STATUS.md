# Status — Time-Varying Multiscale Stochastic Refinement v0.1.0

**Lean:** 4.34.0-rc2  
**mathlib:** aeb72f1e9981b6d35b426b16dca7759be3e7ba06  
**Full warning-as-error check:** PASS (RC=0)  
**Axiom audit:** PASS (RC=0)

## Source inventory

- 43 theorem declarations
- 11 definitions
- 2 structures
- 0 `sorry`
- 0 `admit`
- 0 custom `axiom` declarations

## New sharp block

The release upgrades the earlier uniform-forcing Grönwall estimate to an exact two-sided Duhamel / variation-of-constants theorem with time-dependent forcing.

For a Banach-space operator equation

`D' = A ∘ D + D ∘ B + R`,

Lean proves pointwise

`D(t)x - exp((t-t0)A) (D(t0) (exp((t-t0)B)x))`

is exactly the interval integral of the transported forcing.

It then proves the operator-norm estimate

`‖D(t)‖ ≤ ‖exp((t-t0)A)‖ ‖D(t0)‖ ‖exp((t-t0)B)‖
 + ∫ s in t0..t, ‖exp((t-s)A)‖ ε(s) ‖exp((t-s)B)‖`

whenever `‖R(s)‖ ≤ ε(s)`.

For stochastic covariance refinement, `ε(s)` is instantiated by the actual fine-descendant residual budget

`Σ_{ρ(c)=a,ρ(d)=b} ‖F_c R(s) F_d‖`,

and then by the Lyapunov residual forcing

`R_A(s) P(s) + P(s) R_A(s)^* + R_Q(s)`.

Continuity of the coarse residual corner and the descendant norm budget is derived automatically from continuity of the underlying residual paths.
