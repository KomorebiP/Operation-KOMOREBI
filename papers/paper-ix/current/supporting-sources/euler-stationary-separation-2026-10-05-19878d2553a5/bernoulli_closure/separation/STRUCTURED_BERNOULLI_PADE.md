# Structured Bernoulli Padé approximants and the critical-value budget

Scope: for every admitted ordinary

    r=(17659+2^18 T)2^640-161,

the target remains actual Euler critical nonvanishing. No multiplier digits
are extended here. This attempt constructs rational approximants from the
actual Bernoulli coefficients and tests their convergence and arithmetic cost.

Outcome: a uniform convergence obstruction for the first shifted approximant,
a convergent second shifted approximant with an exact failure to approximate
the deep chart, and a critical-scalar error theorem for higher approximants.
Actual critical nonvanishing is not proved.

## 1. Rational continuants retain actual Bernoulli coefficients

Write w=z^2 and

    g(z)=z coth z=sum_(m>=0) a_m w^m,
    a_0=1, a_m=2^(2m) B_(2m)/(2m)!=-beta_m/(2m-1).

All a_m lie in Z_2. Define integer polynomials

    A_0=D_0=1, A_1=3+w, D_1=3,
    A_N=(2N+1)A_(N-1)+w A_(N-2),
    D_N=(2N+1)D_(N-1)+w D_(N-2),  N>=2.

Then g_N=A_N/D_N is the finite continued fraction

    1+w/(3+w/(5+...+w/(2N+1))).

Its exact formal error is

    g-g_N = [(-1)^N/((2N+1)!!^2(2N+3))] w^(N+1)
                  +w^(N+2) Z_2[[w]].                     (1)

Thus this rational construction agrees with every actual Bernoulli
coefficient through m=N. Its first omitted coefficient is a dyadic unit.
The beta-kernel approximant

    f_N(w)=g_N(w)-2w g_N'(w)

agrees with f=(z/sinh z)^2 through m=N, and its first omitted error is
the coefficient in (1) multiplied by -(2N+1), still a dyadic unit.

Here is an algebraic proof of the coefficient count and leading error. For
n=N+1 put

    P_n(X)=sum_(k=0)^n [(2n-k)! n!/((2n)! k!(n-k)!)] X^k.

The factorial formulas

    [w^k] A_N = 2^(2k-n)(2n-2k)!/((2k)!(n-2k)!),
    [w^k] D_N = 2^(2k+1-n)(2n-2k-1)!/((2k+1)!(n-2k-1)!)

follow by substitution in the continuant recurrence. They give

    g_N=z[P_n(2z)+P_n(-2z)]/[P_n(2z)-P_n(-2z)].

Integration by parts, or coefficient comparison, gives the exact identity

    e^X P_n(-X)-P_n(X)
      =(-1)^n X^(2n+1)/(2n)! *
                   integral_0^1 e^(tX) t^n(1-t)^n dt.

In particular

    e^X P_n(-X)-P_n(X)
       = [(-1)^n(n!)^2/((2n)!(2n+1)!)] X^(2n+1)
                                              +O(X^(2n+2)).

This formal-power-series identity proves the complete coefficient agreement;
the leading coefficient uses the elementary integral
integral_0^1 t^n(1-t)^n dt=(n!)^2/(2n+1)!.
Substitution and simplification give (1). Since D_N(0)=(2N+1)!! is odd,
g_N has integral dyadic series coefficients. Together with a_m integral,
this proves the displayed integral remainder, not just formal agreement.

The adjacent continuants satisfy

    A_N D_(N-1)-A_(N-1)D_N=(-1)^(N-1) w^N.               (2)

In particular A_N and D_N are coprime over Q[w]. The poles of g_N=A_N/D_N
are simple. To see this without transferring any simplicity claim to the Euler
residual, write D_N as the determinant of a tridiagonal matrix with diagonal
3,5,...,2N+1 and adjacent entries sqrt(-w). After diagonal scaling, the
associated real symmetric matrix has zero diagonal and nonzero adjacent
entries. Its eigenvalues are simple, real, and paired as ±lambda; the zero
eigenvalue, if present, contributes a constant factor. Hence D_N is a nonzero
constant times a product of distinct factors1+w lambda^2. This concerns g_N only: f_N=g_N-2w g_N'
generically has double poles at these nonzero denominator roots.

## 2. An intrinsic height-versus-error obstruction

Fix an ordinary a>=1 and evaluate at z=2^a, w=2^(2a). Both A_N(w),D_N(w)
are positive odd integers. By (2), any common divisor divides w^N, so it
must be1. Therefore the rational value g_N(2^a) is already in lowest terms,
and its exact height satisfies

    H(g_N(2^a))=A_N(w)>=D_N(w)>=(2N+1)!!.                 (3)

On the other hand (1) proves the exact error valuation

    v2(g(2^a)-g_N(2^a))=2a(N+1).                         (4)

The same exact error valuation holds for f-f_N. The lower bound in (3)
grows as N log2 N, whereas (4) is linear in N. Thus at every fixed a the
intrinsic rational height eventually exceeds the available error precision.
This is not merely a loose estimate obtained from evaluating a high-degree
polynomial. Already at a=1, the height exceeds2^(2N+2) for every N>=3:
check N=3,4 directly; for N=5, D_N>=11!!>2^12; induction uses the odd
factor2N+3>4.

Subtracting any fixed rational number does not remove this asymptotic
denominator cost. If alpha=p/q is fixed, the reduced denominator of
g_N(2^a)-alpha is at least D_N(w)/|q|, because gcd(A_N,D_N)=1.

Consequently this explicit Padé construction cannot by itself supply a
Liouville separation argument based on rational height below certified
precision. It remains a useful exact coefficient approximation. This result
does not exclude every Padé construction or an additional arithmetic identity.

## 3. What the global approximant gives for the actual stationary scalar

Suppose N>=r and use the actual beta coefficient beta_r for normalization.
Let beta_m^(N) be the coefficients of f_N. Define the rational-kernel source
model on the terminal161 chart by

    K_(r,N)(Z)=2^-24 sum_(q>=0) 8^q [beta_(r+q)^(N)/beta_r]
                       P_q(x) A(x-q),
    x=10202+2^15 Z.

Its packet series converges: the coefficients beta_m^(N) are integral,
and the factor8^q makes the normalized tail restricted. Actual and model
coefficients agree through q=N-r. Since v2(beta_r)=s2(r)-1,

    K_(r,N)-K_r in2^L Z_2<Z>,
    L=3(N+1-r)-s2(r)-23.                                 (5)

For L>=9 the model remains in the same quadratic chart. Its half derivative
has a unique critical point c_N, and

    v2(c_N-c)>=L-1,
    v2(K_(r,N)(c_N)-K_r(c))>=L.                           (6)

Indeed division of the differentiated error by2 loses at most one bit, while
both half derivatives are isometries. Stationarity makes the value correction
from moving the center have valuation at least2L-2, which is no smaller than L.
Thus the local rank-one certificate of the model transfers exactly through L
bits. No critical point is assumed rational or algebraic over Q.

Two missing arithmetic inputs remain. First, the source transform of a rational
kernel is still an infinite analytic packet series; rationality in w does not
make it a rational function of Z. Second, neither the simple kernel poles nor
the nonzero continuant determinant gives a lower bound for its critical scalar.
The global approximant also has degree proportional to r+L, rather than just L.
The next construction removes that degree cost but exposes another issue.

## 4. Shifted Padé: the first approximation does not even converge on the chart

Consider the actual shifted Bernoulli series

    h_r(w)=sum_(q>=0) a_(r+q) w^q.

For every index in the prescribed progression,

    v2(a_(r+1)/a_r)=-4.                                  (7)

This follows either from s2(r+1)-s2(r)=-4 or from the exact factorial ratio
and v2(r+1)=5. The [0/1] shifted Padé approximant is

    h_r^[1](w)=a_r/(1-rho w), rho=a_(r+1)/a_r.

Apply the beta conversion coefficientwise: the normalized q-th coefficient
is rho^q(2r+2q-1)/(2r-1). The last quotient is an odd unit. Its purported
source-transform packet on the normalized K chart has valuation

    -24+3q-4q+v2(P_q(x)).

Choose the point x=-22566=10202-2^15, which belongs to the actual chart.
For q=2^k with k>=15, the binomial coefficient
binom(22565+2^k,2^k) is odd. Therefore

    v2(P_q(-22566))=v2(q!)=q-1,

the other factors2x-2i-1 being odd. Since A is always a unit, the packet
terms have valuation exactly -25 for all these q. They do not tend to zero.

Thus this rational approximant built from actual Bernoulli coefficients
does not define a source-transformed function even at one point of our chart.
The obstruction is its dyadic denominator slope, not an unknown height bound.

## 5. The next shifted approximant converges, but misses the deep cancellation

Write a_j here for a_(r+j), and put

    Delta=a_1^2-a_0 a_2,
    q1=(a_0 a_3-a_1 a_2)/Delta,
    q2=(a_2^2-a_1 a_3)/Delta.

The exact actual valuations relative to v2(a_0)=v are

    v2(a_0)=v, v2(a_1)=v-4, v2(a_2)=v-3, v2(a_3)=v-3.

Consequently Delta has valuation2v-8, both numerator valuations are2v-7,
and

    v2(q1)=v2(q2)=1.                                     (8)

The [1/2] approximant

    h_r^[2](w)=[a_0+(a_1+q1 a_0)w]/[1+q1 w+q2 w^2]       (9)

matches the actual coefficients q=0,1,2,3. If t_q denotes its q-th coefficient,
then t_0=a_0,t_1=a_1 and t_q=-q1 t_(q-1)-q2 t_(q-2). Thus

    v2(t_q/a_0)>=-4+floor(q/2), q>=1.                    (10)

The resulting source transform does converge as a restricted analytic series.
This supplies a genuine finite rational model whose denominator has safe
dyadic slopes; convergence cannot simply be assumed for arbitrary shifted
approximants, as Section4 demonstrated.

But this model does not yet approximate the actual deep critical value.
Set c_q=16t_q/a_0 and define its integral global transform

    M(x)=sum_(q>=0) 8^q c_q [(2r+2q-1)/(2r-1)]
                                    P_q(x)A(x-q).

The model's normalized chart is K^[2](Z)=2^-28 M(10202+2^15 Z).
The actual low Bernoulli residues give, modulo2^11,

    (c_0,c_1,c_2,c_3)=(16,1,1386,1190),
    q1=22 mod32, q2=30 mod32.

At x=10202 the contributions q=0,1,2 modulo2^11 are respectively

    592, 688, 1792,

whose sum is1024 modulo2048. The q=3 contribution has valuation14, and
(10) makes every q>=4 contribution divisible by2^14 coefficientwise.
Since M is integral restricted, replacing x by x+2^15 Z leaves these eleven
bits unchanged. Hence uniformly on the deep chart,

    v2(M)=10,  v2(K^[2])=-18.                            (11)

These residues are actual-coefficient consequences for the whole progression.
They can be evaluated using

    D(m)=(1-2^(2m-1))*2B_(2m)
        =sum_(j>=0) 2^j B_j binom(2m,j).

For the required32-bit certificate, terms j>=34 vanish, and r=-161 modulo
2^640 may replace r in the four finite unit evaluations and factorial ratios.
The exact undepletion factors differ from1 far beyond this precision. The
checker verifies the four ratios both at r=-161 in this finite formula and
at the actual base integer17659*2^640-161. The binary congruence gives the
same result for every admitted multiplier, not an extrapolation from a scan.
Explicitly, changing the upper argument of binom(2r,j), j<=33, by a multiple
of2^641 changes it by a multiple of2^(641-floor(log2 j)), at least2^636.
The finite factorial products in the four scaled ratios have valuation at
most9; after removing their known powers of2, their odd parts are unchanged
through at least635 bits. These margins greatly exceed the32 bits used here.

The true K_r is integral on the chart by the inherited complete certificate.
Therefore (11) proves the exact model error

    v2(K^[2](Z)-K_r(Z))=-18  for every Z in Z_2.           (12)

The convergent second approximant is root-free, but its omitted actual
Bernoulli tail changes the deep value by a larger amount than the normalized
unit scale. Its root-free conclusion cannot transfer. This is an actual
arithmetic failure of this particular finite approximant, not merely an
insufficient abstract error estimate.

## 6. Remaining precise task

The carry-adapted continuation has now been executed in
[CARRY_ADAPTED_SEPARATION.md](carry_adapted/CARRY_ADAPTED_SEPARATION.md).
It keeps the actual lower161 packets and starts its rational approximation
at m=r+161. There the actual Hankel matrices have an exact valuation law,
giving integral Padé denominators throughout the carry range, and ranks1
through10 have exact uniform source and critical-value error formulas.
Those statements concern this changed tail parameterization. They do not
assert nonvanishing of the actual stationary scalar for every admitted T.

The shifted [1/2] construction gives a usable recurrence and convergence
criterion. To reach the q161 cancellation, a shifted approximant must capture
the relevant high-index coefficients while keeping its denominator slopes
compatible with the source transform. For example a [80/81] approximant would
match q=0,...,161 if its defining Hankel system is nonsingular. Neither that
Hankel valuation budget nor a nonzero local critical scalar is established here.

The exact Bernoulli continued-fraction identities improve the arithmetic
construction, but they do not currently bind the actual stationary scalar
away from zero. Sections2,4,5 identify three distinct failed implications:
intrinsic Padé height does not beat error, coefficient matching need not preserve
source convergence, and source convergence need not preserve deep cancellation.

All universal claims above have algebraic or valuation proofs. The executable
checks verify indexing, the finite Padé identities, exact rational heights,
and the small low-unit certificate supporting (11). No new T digits and no
Lean compilation are involved.
