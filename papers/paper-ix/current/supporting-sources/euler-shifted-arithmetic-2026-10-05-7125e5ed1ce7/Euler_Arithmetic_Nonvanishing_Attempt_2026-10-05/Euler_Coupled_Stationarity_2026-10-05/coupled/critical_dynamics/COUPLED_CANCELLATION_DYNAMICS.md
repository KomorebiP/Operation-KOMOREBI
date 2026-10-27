# Coupled cancellation and stationary-point dynamics

## Scope and notation

Fix an actual integer index

    r=(17659+2^18 T) 2^640-161,  T>=0,

whose true terminal label is161. The inherited 629-bit complete coefficient
certificate supplies the common deep quadratic chart at

    x=10202+2^15 Z.

Let gammahat_q be its depleted normalized packet scalars, with mu=-154.
Keep epsilon independent of this fixed r and put epsilon=2^24 eta. Define

    K(Z,eta)=2^-178 (1-2^24 eta)
       sum_q gammahat_q P_q(x) A(x-q)/(1-2^24 eta 4^q).

This is a restricted analytic function of Z and eta in Z_2. Let c(eta) be
its unique critical point and let Phi(eta)=K(c(eta),eta). Subscripts below
denote partial derivatives, always in the normalized coordinates Z,eta.

The true-terminal hypothesis is essential. No global analytic interpolation
in the integer multiplier T is assumed or constructed.

## Main coupled conclusions

For every eta,theta in Z_2,

    v2(c(eta)-c(theta))=18+v2(eta-theta),                         (1)
    v2(Phi(eta)-Phi(theta))=v2(eta-theta).                        (2)

The derivatives have the exact normalized leading units

    c'(eta)/2^18 = -1 mod8,
    c''(eta)/2^40 = 3 mod8,
    Phi'(eta) =17 mod32,
    Phi''(eta)/2^27 =1 mod8.                                   (3)

The stronger all-disc Taylor laws are

    c(theta+h)=c(theta)+h c'(theta)+2^39 h^2 C_theta(h),
    Phi(theta+h)=Phi(theta)+h Phi'(theta)+2^26 h^2 V_theta(h),    (4)

where C_theta,V_theta are integral restricted analytic units satisfying

    C_theta(h)=3 mod8,  V_theta(h)=1 mod8.

Thus the critical value's first nonlinear response is ten bits larger in
2-adic norm than the stationary-point contribution to its quadratic response.
The actual source cancellation also slows stationary motion by four more
bits than the previous bound14 detected.

At every eta, exact stationarity gives

    K(c(eta)+z,eta)=Phi(eta)+z^2 U_eta(z),                       (5)

with U_eta an integral analytic unit. Its constant coefficient is
K_ZZ(c(eta),eta)/2, and U_eta=81 mod256 coefficientwise.

Let eta_* be the unique zero of Phi and set c_*=c(eta_*). If eta!=eta_*,
put N=v2(Phi(eta)). Then

    v2(c(eta)-c_*)=N+18.                                      (6)

Every root Z of K(.,eta) must satisfy

    v2(Z-c(eta))=N/2.                                        (7)

In particular an odd N excludes roots. In the original x coordinate,
the stationary-center displacement has valuation N+33 while root distance
from the moving center has valuation15+N/2. Equations (6)-(7) link cancellation
depth, stationary motion, and root separation without equating any of them.

## 1. The inherited actual coefficients used

The authoritative finite input is

`recovered/Komorebi_Euler_Parameter_Nonintersection_2026-10-04/Euler_Nonintersection_Certificate/fast_certificate_629.json`.

Its complete deep affine coefficient records give, modulo256,

    H0=215+72 Z+107 Z^2,
    H1=189,

with every higher coefficient zero. Since B=17659+2^18 T=251 mod256,
the actual and depleted deep chart coefficients satisfy

    K(Z,0)=213+167 T+88 Z+81 Z^2 mod256.                       (8)

The actual/depleted difference is invisible at these bits because the
undepletion exponent2r-1 exceeds the required global precision. The same
complete certificate gives exact valuation8 for its cubic coefficient:
H0's cubic has valuation8 and H1's cubic has valuation42. Therefore

    K_ZZ/2=81 mod256,  v2(K_ZZZ)>=9                           (9)

throughout the chart at eta=0. At its critical point the latter valuation is
exactly9: c=20 mod128 is even, so each term beyond the cubic gains at least
one extra power of two upon evaluation. These bounds persist for every eta
by the estimates below. In particular c(eta)=20 mod128.

## 2. The source cancellation determining velocity

Write

    W(x)=2^-154 sum_q 4^q gammahat_q P_q(x) A(x-q),
    u=gammahat_1/2^153.

For q<161 the scalar valuation is

    v2(gammahat_q)=154+3q+2-s2(160-q).

For q=0 this is154, and for q=1 it is153. In W, the q=2 term has scalar
valuation7; every q>=3 lower term has valuation at least10. For q>=161,
integral normalization gives scalar valuation at least168. Hence

    W=A+2u P1 A(.-1)+2^7 R
     =A+u(9^x-1)/4+2^7 R,   R in Z_2<x>.                    (10)

This is an actual Bernoulli-unit identity, not a free choice of decoration.
Let D(m)=(1-2^(2m-1))*2B_(2m). The exact beta ratio gives

    u=D(r+1)/[D(r)(2r-1)((r+1)/32)].

The midpoint expansion modulo64 requires only Bernoulli indices0,1,2,4,6:

    D(m)=1-2m+(2/3) binom(2m,2)
                 -(8/15) binom(2m,4)+(32/21) binom(2m,6) mod64.

Since r=-161 modulo all the required powers of two, this gives
D(r)=13, D(r+1)=1, and the denominator factor(2r-1)((r+1)/32)=15 modulo64.
Consequently

    u=43 mod64.                                               (11)

The source has the coefficientwise expansion

    A=1+34x+92x^2+8x^3+112x^4+32x^5+64x^6 mod128.

One obtains it directly from

    (1+2x)A(x)=sum_(q>=0) 8^q x-underlined-q/(q+1)!;

terms q>=4 vanish modulo128. On x=10202+2^15 Z, coefficientwise,

    A'=50 mod128,
    u (log9/4) 9^x=94 mod128.

Differentiating (10) therefore gives the exact cancellation

    W'_x=16 mod128,
    W'_Z=2^19 (1+8R_1).                                     (12)

The two separate source/q1 derivative terms have valuation1. Their sum has
valuation4. This cancellation is precisely responsible for the motion gain18.
The same low source coefficients give

    W=17 mod32,                                               (13)

on the deep chart. Localization of an integral global series also gives
v2(W_ZZ)>=30, which will suffice below.

## 3. The complete eta expansion and its leading terms

Write K=J0+eta J1+sum_(m>=2) eta^m Jm. Exactly,

    J0=K(.,0),
    J1=W-2^24 J0,
    Jm=2^(24m-178) sum_q gammahat_q(4^q-1)4^(q(m-1)) Pq A(.-q).

For every m>=2, the q=1 contribution is

    3u 2^(26m-27) P1 A(x-1)
      =3u 2^(26m-30)(9^x-1).                                (14)

On the chart v2(x)=1, so this term has exact valuation26(m-1).
The q=2 remainder has valuation at least28m-24; every subsequent packet
has greater valuation. To make the tail explicit, for 3<=q<161 we have
gammahat_q valuation at least149+3q, because s2(160-q)<=7. The undifferentiated
localized Pq has content at least1. Thus these terms have valuation at least
24m-28+(2m+1)q, greater than the q=1 valuation. After d=1 or2 Z derivatives,
the bound is24m-29+(2m+1)q+15d. For q>=161, integral gammahat_q gives the
bound24m-178+2q(m-1)+15d, before any additional packet content. All are
strictly above the q=1 bounds for m>=2. For q=2 the derivative bounds are
28m-10 and28m+5 for d=1,2, also strictly higher. Therefore

    v2(Jm)=26(m-1),
    v2(Jm')=26m-12,
    v2(Jm'')=26m+6.                                          (15)

These are coefficientwise lower bounds, attained by their constant terms.
For the leading m=2 terms, (11), log9/8=5 mod8, and
(9^x-1)/16=1 mod8 give

    J2/2^26=1 mod8,
    J2'/2^40=5 mod8.                                        (16)

All estimates are uniform in eta because eta is integral. Equations
(8)-(16) yield, throughout the entire two-variable chart,

| Derivative | Exact valuation or congruence |
| --- | --- |
| K_ZZ | 1; K_ZZ/2=81 mod256 |
| K_Zeta | 19; K_Zeta/2^19=1 mod8 |
| K_etaeta | 27; K_etaeta/2^27=1 mod8 |
| K_Zetaeta | 41; K_Zetaeta/2^41=5 mod8 |
| K_ZZeta | 25 |
| K_ZZZ | at least9; exactly9 at the critical point |
| K_eta | 17 mod32 |

For K_ZZeta, the term -2^24 J0'' of valuation25 dominates W'' and the
higher eta powers. The bounds in (15) justify differentiation and all tail
estimates, without extending a finite multiplier template to new precision.

## 4. Analytic critical motion and the Schur complement

The half derivative K_Z/2 is an affine unit in Z plus an even analytic
perturbation. Its unique zero c(eta) is restricted analytic in eta: solve
by a contraction in the complete Tate algebra Z_2<eta>. Its Z derivative
is always a unit, so implicit differentiation is valid and gives

    c'=-K_Zeta/K_ZZ,
    c''=-(K_Zetaeta+2K_ZZeta c'+K_ZZZ(c')^2)/K_ZZ.              (17)

All quantities on the right are evaluated at Z=c(eta). The three numerator
terms for c'' have valuations41,44,45 respectively at the critical point. Thus the first one
strictly dominates. The table proves the first two congruences in (3).

Stationarity removes the chain-rule term from the first value derivative:

    Phi'=K_eta.

Differentiating once more gives the exact Schur-complement identity

    Phi''=K_etaeta-K_Zeta^2/K_ZZ.                              (18)

The direct parameter curvature has valuation27. The correction caused by
stationary-point motion has valuation37. They cannot cancel. This proves
the last two congruences in (3), including their leading units.

For two parameters eta,theta, the divided difference of K_Z/2 in the
parameter direction has exact valuation18, uniformly in Z. Its Z direction
is an isometry. Comparing its two zero equations proves (1). The original
critical-value isometry proves (2), or follows from the strict value-motion
comparison used below.

## 5. Exact chord laws, including the nonlinear motion correction

Fix theta and set h=eta-theta and d=c(theta+h)-c(theta). Equation (1) gives
v2(d)=18+v2(h). Coefficientwise, d belongs to 2^18 h Z_2<h>: the critical
equation's change at fixed Z is divisible by 2^18 h, and its contracting
inverse in Z preserves that ideal. In the stationary equation, expand K_Z/2
about c(theta).
The second and higher Z terms have coefficient valuation at least7 by (8).
The parameter expansion has its quadratic coefficient of exact valuation39,
with normalized leading unit5 by (16). After subtracting its two linear
terms, the three possible leading sizes are

    pure parameter quadratic: 39+2v2(h),
    parameter/point cross term: at least42+2v2(h),
    stationary nonlinear term: at least43+2v2(h).

Only the first survives in the leading unit. Dividing by the unit
K_ZZ/2=1 mod8 yields the first identity of (4), with C_theta= -5=3 mod8.

For the critical value, Taylor-expand K(.,theta) about its critical point
and subtract h Phi'(theta). The corresponding leading sizes are

    direct parameter quadratic: 26+2v2(h),
    stationary value motion: at least36+2v2(h),
    parameter/point cross term: at least37+2v2(h).

The direct quadratic coefficient has normalized unit1 by (16). It gives
the second identity of (4), with V_theta=1 mod8. Restricted analyticity
makes each exact difference divisible by h^2 in Z_2<h>; the coefficientwise
bounds above justify the displayed normalized analytic units, including h=0.

## 6. Stationary factorization and the coupled cancellation invariant

Translation to c(eta) removes the linear term exactly. The quadratic term
is a unit, and all higher Z coefficients of K are divisible by256. Translation
preserves that divisibility. This proves (5) and U_eta=81 mod256.

At eta_*, Phi=0 and the critical root has multiplicity exactly two. At any
other eta, (2) gives N=v2(eta-eta_*), and (1) gives (6). If K(Z,eta)=0,
the two terms in (5) cancel. Since U_eta is a unit, their valuations must
match, giving (7). This is the new coupled invariant: the same cancellation
depth fixes both center drift and the possible root distance.

The actual Euler sheet is eta=2^(2r-25). All these identities remain valid
there. They still do not prove that this eta differs from eta_*. The remaining
gap is the arithmetic intersection, not an uncontrolled stationary-point
motion or an omitted nonlinear cancellation term.

There is now a sharper exact necessary cancellation filter. Put E=2r-25
and a=Phi(0). If the actual Euler chart is singular, (4) at theta=0 gives

    0=a+2^E Phi'(0)+2^(2E+26) V_0(2^E).                       (19)

Therefore, successively,

    v2(a)=E,
    a/2^E=15 mod32,
    v2(a/2^E+Phi'(0))=E+26,
    [a/2^E+Phi'(0)]/2^(E+26)=7 mod8.                         (20)

The unit15 is -17 modulo32 and the last unit7 is -1 modulo8. Any failure
of one of these tests proves actual simplicity. Equation (19) includes the
stationary-point motion exactly through V_0; it does not freeze the critical
point. The present work does not prove that an actual Bernoulli family must
fail one of these filters, so (20) is a strengthened necessary condition,
not universal nonintersection.

Regardless of whether a singularity occurs, the actual-versus-depleted
critical-point motion is now exact:

    v2(c(2^E)-c(0))=2r-7,
    [c(2^E)-c(0)]/2^(2r-7)=7 mod8.

In the physical x coordinate its valuation is2r+8. The corresponding
critical-value correction has valuation2r-25 and normalized leading unit17
modulo32. After subtracting the full first-order correction, the remaining
critical-value error has exact valuation4r-24 and normalized unit1 modulo8.
These identities sharpen the earlier coarse motion bound and explain why
stationary-point movement cannot cancel the first undepletion correction.
