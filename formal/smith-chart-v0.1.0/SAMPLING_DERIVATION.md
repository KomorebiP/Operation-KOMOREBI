# Sensitivity sampling: derivation and scope

This is a mathematical self-review of the sampling construction stated in
the bound Smith chart source. It is not a Lean proof of the integrals or of
the browser's floating-point implementation.

Let `0 ≤ ρ < 1`, put `q = ρ²`, and write `t = ρ exp(iθ)`. Define

```
w(t) = 1/|1-t|² + 1/|1+t|²,
P_q(φ) = (1-q²)/(1-2q cos φ+q²).
```

The denominators are positive. Combining the two fractions gives

```
w(ρ exp(iθ)) = 2(1+ρ²)/(1-2ρ² cos(2θ)+ρ⁴)
              = 2 P_q(2θ)/(1-ρ²).
```

The rational-algebra and trigonometric steps have Lean counterparts in
`SmithSampling.symmetric_weight_algebra` and `SmithSampling.angular_weight`;
the integral and inverse-lift steps below have not been formalized here.

## Cumulative distribution and inverse

For real `|q| < 1`, consider the circle map
`B_q(z) = (z-q)/(1-qz)`. On `|z|=1`, the denominator is nonzero,
`|B_q(z)|=1`, and its inverse is `B_{-q}`. Let `L_q` be the continuous
real-valued lift satisfying `B_q(exp(iφ)) = exp(iL_q(φ))` and `L_q(0)=0`.
Differentiating the logarithm gives

```
L_q'(φ) = (1-q²)/(1-2q cos φ+q²) = P_q(φ) > 0.
```

For example, on `-π < φ < π`, the lift is
`2 arctan(((1+q)/(1-q)) tan(φ/2))`. Continuing it across the endpoints
shows `L_q(φ+2π)=L_q(φ)+2π`. Thus its inverse lift is `L_{-q}`:
the two circle maps are inverses, and the lifts compose to the identity
because both are continuous and fix zero.

For `0 ≤ θ ≤ 2π`, set `F_ρ(θ)=L_q(2θ)/(4π)`. It follows that

```
F_ρ'(θ) = (1-ρ⁴) / [2π(1-2ρ² cos(2θ)+ρ⁴)],
F_ρ(0) = 0,                 F_ρ(2π) = 1,
F_ρ⁻¹(u) = L_{-q}(4πu)/2   for 0 ≤ u ≤ 1.
```

Hence the displayed density is normalized and strictly positive, and each
specified CDF mass has a unique angle in `[0,2π]`. The browser's
`smithCdf` and `smithQuantile` implement these lifted maps with explicit
floating-point branch handling. A bounded numerical comparison to independent
high-precision quadrature is recorded separately; it is not a proof that all
floating-point branch cases are correct.

## What the equal-mass statement proves

Along the phase orbit,

```
|dz/dθ| + |dy/dθ| = 2ρ w(ρ exp(iθ)).
```

For `ρ>0`, partitioning the circle at equal increments of `F_ρ` therefore
gives equal integrals of the combined coordinate speed. For any `N` intervals
with combined-speed masses `A₁,…,A_N`, their sum is fixed, so
`max A_j ≥ (Σ A_j)/N`; an equal-mass partition attains that bound. This
elementary minimax step is formalized in `SmithSampling.equal_mass_minimax`.
When `ρ=0`, both coordinate speeds vanish and every partition attains the
zero bound; the normalized sensitivity density itself is uniform.

For linear interpolation on an interval `[a,b]`, the triangle inequality
bound for each coordinate's interpolation error is at most the integral of
its speed over that interval. Adding the two bounds gives `A_j`. Equal mass
therefore minimizes the largest of these **upper bounds**. It does not by
itself minimize the actual maximum error, optimize an arbitrary response,
establish noise robustness, or outperform another RF fitting method.
