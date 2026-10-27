# Shifted Bernoulli remainder and the regularized finite prefix

Base: `Euler-arithmetic-nonvanishing-20261005`.
Base archive SHA256:
`15e1f9114380e180adcf4f7306d894100d6fd499929ee7a841d8629bd27e7464`.
The prior archive is immutable. This continuation works on the actual
source-eliminated shifted series, its exponent derivative, and the finite
prefix after unit-3 regularization.

## 1. Exact shifted-series dictionary

Use a_n=4^n B_(2n)/(2n)!, nu=2s+1, and

    u_r(s)=sum_(n>=r) 8^n a_n 9^-n P_(n-1)(s).

For s(2s+1)!=0, direct falling-factorial cancellation gives

    u_r(s-1/2)
      = [2/((2s)(2s+1))]
          sum_(n>=r) (16/9)^n B_(2n) binom(2s+1,2n).        (1)

The identity extends by removable continuation where appropriate. The
terminal-161 chart has odd s, so its displayed denominator is nonzero.
The factor is 2/((2s)(2s+1)), not its reciprocal and not a missing factor2.

For b=4 or 4/3 define

    J_b(s)=I((1+ba)^(2s+1)),
    P_(r,b)(s)=1-(2s+1)b/2
                  +sum_(1<=n<r) b^(2n) B_(2n) binom(2s+1,2n),
    R_(r,b)(s)=J_b(s)-P_(r,b)(s).

I is the Volkenborn functional. The coefficient valuations of the binomial
expansion tend to infinity uniformly in s; the functions and their exponent
derivatives converge in the restricted analytic algebra. Thus (1) is

    u_r(s-1/2)=R_(r,4/3)(s)/(s(2s+1)).                     (2)

## 2. Reflection includes an exact finite cutoff defect

Volkenborn reflection I[f(-1-a)]=I[f(a)] gives, for odd exponent nu=2s+1,

    J_(4/3)(s)=-(3*9^s)^-1 J_4(s).                       (3)

Here (3+4a)^(2s+1) means (3+4a)((3+4a)^2)^s. Reflection sends it to
-(1+4a)^(2s+1), so the sign in (3) is forced. It is compatible with the
analytic half-shift branch exp(log(9)/2)=-3.

Set lambda=3*9^s and ell=log9. Keeping every term below the cutoff,

    R_(r,4/3)
      =-lambda^-1 R_(r,4)-P_(r,4/3)-lambda^-1 P_(r,4),     (4)

and differentiation with respect to s gives

    R_(r,4/3)'
      =-lambda^-1(R_(r,4)'-ell R_(r,4))
       -P_(r,4/3)'-lambda^-1(P_(r,4)'-ell P_(r,4)).         (5)

There is no lost cutoff constant or logarithmic derivative in (4)-(5).
The finite defect lambda P_(r,4/3)+P_(r,4) vanishes at s=0,...,r-1,
where both even Bernoulli tails terminate. Those forced zeros do not imply
that its value or derivative is zero at a general dyadic argument.

The same computation for J_d(s)=I((d+4a)^(2s+1)), odd ordinary d, yields

    J_(d+4)-J_d=4(2s+1)d^(2s),
    J_(4-d)=-J_d,                                        (6)

with differentiated translation term

    8d^(2s)+4(2s+1)log(d^2)d^(2s).

For integer odd d, translation and reflection express J_d in terms of
J_1 and finite odd powers. They do not give a second independent equation
determining J_1. The unit-3 regularization below is a stronger boundedness
input, and its transfer to the actual prefix was therefore tested separately.

## 3. What regularization does to the actual finite prefix

Let

    m(s)=1+3*9^s,
    S_r(s)=sum_(0<=n<r)8^n beta_n P_n(s) A(s-n),
    F_r(s)=Ecal(s)-S_r(s).

On Z_2, m has exact valuation2 and no zeros, so multiplying F_r by m
preserves zero multiplicity. The regularized full Euler moment sequence
has the rational Amice transform

    sech t+3sech(3t)
       =2y(y^2+1)/(y^4-y^2+1),   y=exp t.                (7)

After y=1+T, the denominator has odd constant coefficient. Its reciprocal
has integral coefficients, while the numerator is divisible by2. This
is a bounded measure with norm at most1/2, supported on odd units. In
particular its half-index forward differences have valuation at least
3k+1. The parent continuation studies sharper exact moment valuations.

The corresponding regularized finite prefix is exactly

    m(s)S_r(s),

whose ordinary-moment exponential generating function is

    Aegf(t) f_<r(2t)+3 Aegf(3t) f_<r(6t),                (8)

where Aegf(t)=(cosh(3t)-cosh t)/(4t^2) and
f_<r(z)=sum_(n<r) beta_n z^(2n).
The factor3 in (8) must retain the factor1/9 inside Aegf(3t).

For the n=0 source term there is another exact identity. Define the
regular function J(q)=(exp(ell q)-1)/(ell q), with J(0)=1. Then

    m(s)A(s)=-ell^2/16 J(s+1) J(s+1/2).                  (9)

This follows from m(s)=1-exp(ell(s+1/2)); the minus sign uses
exp(ell/2)=-3. Equation (9) removes the apparent pole at s=-1/2.

Writing J(q)=int_0^1 exp(ell q u) du as coefficient integration shows
the arithmetic that remains: mA is a product of two integration functionals,
whose monomial values are 1/(k+1). They are not bounded measures on the
2-adic continuous-function norm. Analyticity of mA in the exponent s does
not supply the bounded odd-unit moment estimate possessed by (7).

## 4. The transfer fails for every r, with an exact pole witness

The regularized prefix in (8) is not the moment sequence of a bounded
measure on Z_2, for any finite r>=1. Here is a concrete obstruction that
retains all finite cutoff terms.
If only its even moments are prescribed, first symmetrize a hypothetical
measure under x -> -x. This preserves the even moments and sets the odd
moments to zero, giving precisely the even Amice germ used below.

As an Amice germ put y=1+T and t=log y. Its n=0 contribution is

    [cosh(3t)-cosh t+(cosh(9t)-cosh(3t))/3]/(4t^2),      (10)

where the hyperbolic functions are continued as (y^k+y^-k)/2.
Take a primitive eighth root zeta. It has |zeta-1|_2<1 and log zeta=0.
If c=(zeta+zeta^-1)/2, then c!=0,

    cosh(9t)|_(y=zeta)=c,
    cosh(3t)|_(y=zeta)=-c,
    cosh t|_(y=zeta)=c.

The numerator of (10) is therefore -4c/3, so (10) has nonzero principal
part -c/(3(log y)^2) at y=zeta. Every term n>=1 in (8) has a factor
(log y)^(2n), cancelling the source denominator (log y)^2. These finitely
many terms are regular at zeta and cannot cancel the double pole.

Thus no finite r removes this pole. The regularized full Euler transform
(7) is regular there, so the actual regularized residual mF_r also retains
a nonzero double pole, with the opposite principal part.

This is a statement about the moment distribution, not a pole of F_r as a
function of the exponent s. It prevents transferring a bounded-measure
estimate from (7) to mS_r or mF_r by an unjustified norm inequality.

## 5. Executed strict-bound discriminator

We tested the concrete proposed estimate

    v2 Delta^k[mF_r](0) >= 3k+1,                           (11)

which would follow if the actual regularized residual had the same bounded
odd-unit measure norm as (7). Exact rational Euler/Bernoulli reconstruction
falsifies (11), preserving the true r cutoff:

| r | k | actual valuation | proposed lower bound |
|---:|---:|---:|---:|
| 1 | 6 | 18 | 19 |
| 2 | 6 | 18 | 19 |
| 3 | 10 | 30 | 31 |
| 5 | 14 | 42 | 43 |
| 9 | 22 | 66 | 67 |
| 17 | 38 | 114 | 115 |

These are counterexamples to this transfer estimate, not to simplicity.
The pole argument proves the stronger lack of any bounded-measure
representation of these ordinary moments. It does not prove that no more
delicate estimate on the value and derivative at a critical point can exist.

## 6. No finite odd dilation multiplier repairs the prefix

This obstruction extends beyond m(s)=1+3*9^s. Let

    h(s)=sum_(d in D) c_d d^(2s),

where D is a finite set of distinct positive odd integers, the coefficients
are in Q_2, and not all c_d are zero. Negative d may first be merged with
positive d because d^(2s) uses (d^2)^s. Then h(s)S_r(s) is not the even
moment sequence of a bounded measure, for any finite r>=1.

Indeed its n=0 source term has numerator

    P(y)=sum_d c_d/d^2 [ (y^(3d)+y^(-3d))/2
                        -(y^d+y^(-d))/2 ]

over 4(log y)^2. Every n>=1 cutoff contribution is regular at nontrivial
2-power roots of unity. If this were a bounded measure, multiplication by
(log y)^2 and evaluation at each such root would force P to vanish at
infinitely many distinct roots. A finite Laurent polynomial with infinitely
many roots is zero. But if d_max is the largest d with c_d!=0, the coefficient
of y^(3d_max) is uniquely c_(d_max)/(2d_max^2), which is nonzero.
This proves the contradiction.

The same argument applies to h(s)F_r(s). To avoid poles of the full Euler
dilates, use primitive roots of order at least8: each sech(dt), odd d,
has denominator y^(2d)+1 and can have a 2-primary torsion pole only at
order4. Thus the full finite Euler dilation sum is regular at all the
higher torsion points used above.

This theorem is restricted to finite scalar dilation multipliers. It is
not a theorem about arbitrary analytic or differential filters.

## 7. A multiplicity-preserving polynomial escape, tested explicitly

The polynomial D(s)=(s+1)(2s+1) does remove the source's torsion denominator:
the prior exact identity is 8D S_r=9^(s+1)Q_r-R_r, with finite rational
polynomials Q_r,R_r. On the terminal-161 chart s is odd and s+1 has fixed
valuation1, so D is nonzero and multiplication by it preserves multiplicity.
It lies outside the finite-dilation theorem.

However, it destroys the bounded-measure property of the full regularized
Euler function b(s)=m(s)Ecal(s). This failure can be quantified exactly.
Let R(y) be the rational transform in (7), L=y*d/dy, and t=log y. Since
2s corresponds to t*d/dt on ordinary-moment exponential generating
functions, the transform of D(s)b(s) is

    R(y)+2t L R(y)+(t^2/2)L^2 R(y).                        (12)

The extra t LR term from squaring t*d/dt is included here. At y=1,

    LR(1)=0,   L^2R(1)=-28.

All coefficients of R(1+T), LR(1+T), and L^2R(1+T) are divisible by2.
Thus B(T)=L^2R(1+T)/2 is integral, with B(0)=-14 of valuation1.
Also A(T)=2LR(1+T) is divisible by4 and A(0)=0.

For n>=2,

    [T^n](log(1+T))^2=(-1)^n 2H_(n-1)/n,

and v2(H_(n-1))=-floor(log2(n-1)), because the largest power-of-two
denominator is unique. For n=2^k this coefficient has valuation2-2k.
For 2<=n<2^k it has valuation at least4-2k: if v2(n)=k-1 then
n=2^(k-1), and otherwise v2(n)<=k-2.

Consequently, at T^(2^k), k>=2, the B(0)t^2 contribution to (12) has
valuation3-2k. All shifted t^2 contributions have valuation at least4-2k.
The tA contribution has valuation at least3-k and R has valuation at least1.
The leading term is therefore unique, proving

    v2([T^(2^k)] Amice[D b])=3-2k, k>=2.                 (13)

These valuations tend to minus infinity. Thus the concrete polynomial
filter cancels the prefix's interior poles but loses boundedness on the
Euler side. It does not furnish the desired strict value/derivative
separation. No claim excluding every differential or infinite filter is made.

## 8. Current arithmetic implication

Equations (2), (4), and (5) identify the shifted term and its derivative
as a reflected Bernoulli remainder with the finite defect retained. The
unit-3 regularization supplies a true bounded full Euler measure, but the
actual residual prefix remains an unbounded distribution. The attempted
strict coefficient estimate (11) fails at the displayed exact examples.

No strict separation between the shifted remainder and its finite target
at the actual stationary point was proved. A successful continuation must
use the retained prefix explicitly, for example by an estimate for its
order-two integration functional at that point. It cannot replace this
prefix by the bounded Euler measure or discard its pole contribution.

The proof in this note is algebraic/analytic. `check_moment_transfer.py`
corroborates reflection and the shifted-series dictionary by exact rational
identities, verifies the torsion numerator, and reproduces the failed
strict estimate. No Lean run was performed.
