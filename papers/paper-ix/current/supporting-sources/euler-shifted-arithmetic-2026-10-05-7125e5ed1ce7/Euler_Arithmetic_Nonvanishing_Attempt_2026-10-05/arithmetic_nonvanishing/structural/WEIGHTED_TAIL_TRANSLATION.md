# Weighted Bernoulli convolution and the exact half-shift defect

Base checkpoint: `Euler-coupled-stationarity-20261005`.
This note pursues the weighted convolution supplied in parallel by the
unit-identity route. It preserves the actual cutoff and every cross-boundary
term. No Euler critical-value nonvanishing is concluded.

## 1. The exact cutoff identity

Put

    g(z)=z coth z=sum a_n z^(2n),
    a_0=1, a_n=-beta_n/(2n-1) for n>=1,
    f(z)=(z/sinh z)^2.

The elementary identity coth z coth(2z)=1+(2 sinh^2 z)^-1 gives

    g(z)g(2z)=f(z)+2z^2.                                  (1)

Let g_<r be the polynomial with n<r, h_r=g-g_<r, and let

    C_r(z)=[g_<r(z)g_<r(2z)]_(degrees>=2r).

For r>=2 the exceptional 2z^2 is below the cutoff, and exactly

    f_>=r(z)=h_r(z)g(2z)+g_<r(z)h_r(2z)+C_r(z).             (2)

Here C_r is the finite polynomial

    sum_(n=r)^(2r-2) [sum_(i+j=n, i,j<r) 4^j a_i a_j] z^(2n).

It cannot be discarded. Its top coefficient is
4^(r-1) a_(r-1)^2, which is nonzero. At its first coefficient,
comparison in (1) gives the stronger exact formula

    [z^(2r)] C_r = ((2r+4^r)/(2r-1)) beta_r.               (3)

For r>=2, v2(2r+4^r)=1+v2(r): the other summand has strictly
higher valuation. Thus this first coefficient has valuation s2(r)+v2(r).
In particular the cross-boundary defect carries genuine actual-index
arithmetic, rather than being a formal zero. A nonzero coefficient does not
by itself make its transformed value nonzero at a dyadic stationary point.

## 2. Exact source transform

Write S(t)=sinh(2t)sinh(t)/(2t^2), the source exponential generating function.
For any even kernel k(z)=sum k_n z^(2n), define its analytic source transform
when convergent by

    T_s(k)=sum_(n>=0) 8^n k_n P_n(s) A(s-n).

At s=N>=0 it is (2N)! times [t^(2N)] S(t)k(2t).
For the kernels in (2), coefficient bounds and the convergent individual
Bernoulli series justify the transforms. Equivalently their identities
follow from the finite coefficient identities at every ordinary N and the
restricted analytic continuation in s.

The full transforms simplify exactly:

    T_s(f)=Ecal(s),
    T_s(g)=C(s)=(3*9^s-1)/(2(2s+1)),                     (4)

because

    S(t)g(2t)=[sinh(3t)-sinh(t)]/(2t).

Moreover

    S(t)g(2t)g(4t)=sech t+2cosh(3t)-2cosh t.              (5)

Applying T to (2) therefore gives the actual Euler tail Ecal-S_r,
but as the sum of two translated g tails and the explicit finite transform
T_s(C_r). It is not an identity setting one of those three terms to zero.

## 3. The exact half-shift operator and branch

Define the operator

    N b(s)=s[b(s)-b(s-1/2)].

Since P_q(s)=2^-q(2s)^underlined(2q), it satisfies

    N P_q=q P_q.                                         (6)

The shift uses the analytic branch

    9^(s-1/2)=-(1/3)9^s.                                (7)

Indeed exp(log(9)/2)=-3, the square root of9 in 1+4Z_2.
Using +3 instead changes the commutator and is incorrect for this analytic
continuation. Before shifting, cancel P_n(s)A(s-n) to its source-eliminated
expression. Individual A factors may have poles on the half-integral
coset, while the cancelled packet has a regular continuation.

For r>=1 put

    u_r(s)=sum_(n>=r) 8^n a_n 9^-n P_(n-1)(s),
    v_r(s)=sum_(n>=r) 8^n a_n P_(n-1)(s),
    lambda(s)=9^(s+1),
    M_r(s)=T_s(h_r)=[lambda(s)u_r(s)-v_r(s)]/8.

These source-eliminated series converge on s in (1/2)Z_2: after substituting
s=y/2, the n-th polynomial has coefficient valuation at least
2n+s2(n), tending to infinity. Thus all half-shift operations below are
legitimate. The explicit finite resummation is

    M_r(s)=C(s)-sum_(0<=n<r) 8^n a_n P_n(s)A(s-n).        (8)

Apparent poles in this finite expression are interpreted by the regular
source-eliminated continuation.

Because beta_n=-(2n-1)a_n, (6) gives the actual f tail

    F_r(s):=Ecal(s)-S_r(s)
       =-[lambda(2N+1)u_r-(2N+1)v_r]/8.

The noncommutation with lambda is exactly

    N(lambda u)-lambda N(u)=(4/3)s lambda u(s-1/2).

Consequently the desired finite half-shift relation is

    F_r(s)=-(2N+1)M_r(s)
              +(s lambda(s)/3) u_r(s-1/2).                (9)

All terms are exact actual Bernoulli/source quantities. Equation (9) makes
precise the extra term surviving when one tries to derive the Euler tail
from the explicit g-tail transform. It is not permissible to identify N
with ordinary differentiation in s.

## 4. What a double root forces, and what remains missing

On the terminal-161 deep chart, s=r+x is odd, hence s lambda(s)/3 is a unit.
If G_r(x)=G_r'(x)=0 then F_r(s)=F_r'(s)=0 by the exact factorization
F_r=8^r beta_r 2^mu_r P_r G_r, including at forced skeleton points.
Equation (9) then forces

    u_r(s-1/2)=3(2N+1)M_r(s)/(s lambda(s)),                (10)

and its ordinary first-derivative equation at that point.

The right side in (10) is a finite rational-exponential expression from
(8). The left side is still an infinite source-eliminated Bernoulli series.
The known finite g-tail identity supplies lambda u_r-v_r, not u_r and v_r
separately. The commutator is exactly where this second unknown survives.
Substituting the full resummations into (9) returns the original Ecal tail;
it does not create an independent nonzero forcing term.

The weighted cutoff equation (2) adds products/convolutions of g tails,
rather than closing a finite linear system in M_r alone. We did not prove
a unit estimate for the difference in (10), nor prove that the cross-boundary
term in (2) dominates the two infinite translated tails at a critical point.
Those are the exact missing implications of this attempt. The factor 4^r
and the finite defect are retained, so a future argument can use them.

The finite checker verifies (1)-(3) through coefficient n=32 and the exact
half-shift identity (9) at integer s=N, 2<=r<=N<=24. The uniform identities
have the independent algebraic proofs above. No Lean run was performed.
