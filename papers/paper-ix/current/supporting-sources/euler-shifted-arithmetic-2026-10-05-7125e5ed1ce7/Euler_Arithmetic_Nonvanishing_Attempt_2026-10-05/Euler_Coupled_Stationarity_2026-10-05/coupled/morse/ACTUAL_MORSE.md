# Exact square coordinate for the actual Euler chart

Base checkpoint: `Euler-regular-address-critical-phases-20261005`.
This is a pointwise theorem for every actual integer index meeting the stated
terminal hypothesis. It does not interpolate those indices at all precision.

Let `B=17659+2^18 T` be a positive odd integer with actual terminal 161 at
`r=B*2^640-161`, and set

    K_r(Z)=2^-178 G_r(10202+2^15 Z).

The inherited finite template, with 629 global coefficient bits, gives

    B K_r = H0+T H1 (mod 2^451)

coefficientwise on this chart. Its complete coefficient records are stored in
`fast_certificate_629.json` in the inherited nonintersection certificate.
All statements below about this finite template use its proved parity-tail
cutoff and true-terminal hypothesis. They do not arise from sampling T.

## A complete low-order certificate

The complete polynomial reductions are

    H0 = 215+72Z+107Z^2 (mod256),
    H1 = 189 (mod256).

All higher coefficients vanish modulo256. Omitted local degrees have valuation
at least451 after removing the content178, so they cannot change this assertion.
Since `B=251 mod256` and its inverse is51 modulo256, the actual function obeys

    K_r(Z)=213+167T+88Z+81Z^2 (mod256).                       (1)

The coefficientwise congruence is crucial. It proves integrality, an even
linear coefficient, a unit quadratic coefficient, and divisibility by256 of
every coefficient of degree at least three.

## Stationary point and exact critical value

The half derivative `Q_r=K_r'/2` is an integral restricted isometry of Z2:
its linear coefficient is odd and every nonlinear coefficient is even.
Thus it has a unique zero `c_r`. From (1),

    Q_r(Z)=44+81Z (mod128),
    c_r=20 (mod128).                                        (2)

Define `Phi_r=K_r(c_r)`. The stationary Taylor expansion shows that replacing
`c_r` by20 changes its value by a multiple of `2^14`. Therefore (1) gives

    Phi_r=69+167T (mod256).                                 (3)

These are the leading coefficients of the coupled system. Equation (3) is a
finite necessary cancellation condition, not an all-precision formula for Phi.

## Exact global Morse coordinate on this dyadic chart

Translation by the exact critical point gives

    K_r(c_r+z)=Phi_r+z^2 S_r(z),
    S_r in Z2<z>,  S_r=81 (mod256),                         (4)

coefficientwise. Indeed the linear coefficient vanishes exactly. The original
quadratic coefficient is81 modulo256, and all higher original coefficients
are divisible by256. Their translated contributions retain that divisibility.

Write `S_r=81(1+256 R_r)`, with `R_r` integral restricted. The binomial series

    s_r(z)=9 sum_(m>=0) binom(1/2,m) (256 R_r(z))^m

converges in the restricted-series algebra. For m>=1, the m-th summand has
coefficient valuation at least `6m+s2(m)`, tending to infinity. Consequently

    s_r^2=S_r,  s_r=9 (mod128).

The coordinate

    w_r(Z)=(Z-c_r)s_r(Z-c_r)

is a bijective analytic isometry of Z2. Its divided difference is odd, and
its inverse is obtained by contraction from its linear term9. It obeys the
exact identity

    boxed: K_r(Z)=Phi_r+w_r(Z)^2.                            (5)

This is not an equality only at zeros or modulo a finite power. The finite
certificate proves a coefficient class, and the convergent square-root
construction proves the exact identity for each actual function in that class.

Consequences:

* The unique stationary point is `w_r=0`.
* A double root occurs exactly when `Phi_r=0`.
* If `Phi_r!=0`, a dyadic root exists precisely when `-Phi_r` is a nonzero
  dyadic square. There are then exactly two simple roots on this chart.
* Equivalently, `v2(Phi_r)` must be even and the unit part of `-Phi_r` must
  be1 modulo8. At either root,

      v2(Z-c_r)=v2(Phi_r)/2,
      v2(K_r'(Z))=1+v2(Phi_r)/2.

The elementary square criterion follows by writing a nonzero dyadic number
as `2^n u`. A square has even n and odd unit u=1 modulo8. Conversely an odd
unit1 modulo8 has a convergent square root by the same binomial construction.
There are two square roots in Q2, and the coordinate is bijective.

## Why stationary-point motion changes observed cancellation

For any test point d in this chart, (5) gives the exact error identity

    K_r(d)-Phi_r=w_r(d)^2,
    v2(K_r(d)-Phi_r)=2v2(d-c_r).                            (6)

If d is the stationary point of a different Euler index, this measures
precisely the error caused by freezing that old point. If the true critical
value has valuation greater than the right side, the frozen value has
exactly the smaller valuation. If they have equal valuation, another
cancellation is possible and must itself be checked. No equality case is
silently discarded.

The packet audit supplies actual examples: center movements of valuations7
and37 create frozen-point errors of valuations14 and74, respectively, while
the moved critical values have valuations30 and80. Thus the cancellation
cannot be interpreted independently of the critical point's motion.

## Extension to the independent undepletion parameter

For a fixed ordinary r as above, use the already-defined independent family
`epsilon=2^24 eta`, with depleted base Khat. Its exact expansion is

    K_eta=(1-2^24 eta)Khat+eta W(10202+2^15 Z)+2^25 eta^2 R1.

Localization makes every nonconstant coefficient of W divisible by `2^15`.
Thus all nonconstant coefficients in (1) are unchanged modulo256, uniformly
for eta in Z2. The actual/depleted difference is also zero at this precision.
Every K_eta therefore admits the exact square coordinate (5), with its own
critical point c(eta) and critical value Phi(eta). These coordinates are
jointly restricted analytic: contraction constructs c in Z2<eta>, then the
same uniformly convergent square-root construction applies over that algebra.

Since the prior theorem proves Phi is a bijective isometry, the parameter
coordinate `v=-Phi(eta)` converts this fixed-r family exactly to

    K_eta(Z)=w^2-v.                                         (7)

This describes the stationary point and cancellation together. The family
contains exactly one double-root parameter v=0, with two simple roots when
v is a nonzero square. The actual Euler parameter remains the specific
`eta=2^(2r-25)`; (7) does not prove that its v is nonzero.

## Scope and remaining implication

This theorem solves the local geometry and gives an exact accounting of
stationary-point motion. It does not assert all-precision continuity in T
of the undepleted integer-index family. The remaining arithmetic question is
the nonvanishing of the actual critical value, now in the exact coordinate
(5). Higher terminal labels require their own certified chart reductions.
