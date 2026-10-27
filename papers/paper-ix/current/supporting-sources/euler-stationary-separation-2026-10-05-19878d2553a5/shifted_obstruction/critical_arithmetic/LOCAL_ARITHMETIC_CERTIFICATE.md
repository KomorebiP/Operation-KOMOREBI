# Local arithmetic certificate for simultaneous Euler cancellation

Status: the actual-index nonvanishing theorem is still open. This continuation
constructs a finite coefficientwise certificate that tests the value and
stationarity together without assuming an algebraic critical point. It then
audits whether rational polynomial approximation supplies the required uniform
arithmetic bound. That last implication is not proved.

## 1. Scope

Fix an admitted ordinary index

    r=(17659+2^18 T)2^640-161,  T>=0,

with true terminal161. On x=10202+2^15 Z let f(Z)=K_r(Z) denote the actual
normalized Euler function. The inherited complete coefficient certificate gives

    f(Z)=a+2bZ+uZ^2+256 Z^3 R(Z),  u odd,
    h(Z)=f'(Z)/2 = Z + constant (mod2),

coefficientwise, with all series integral and restricted. Its critical point c
is unique. Let Phi=f(c). The target is Phi!=0 for every admitted ordinary r.

All claims below concern this actual fixed-r function. They do not interpolate
the ordinary multiplier T to arbitrary precision.

## 2. The local Jacobian quotient is the correct one-dimensional object

Because h(c)=0 and h reduces to a monic linear polynomial, division by Z-c gives

    h(Z)=(Z-c)V(Z),  V=1 (mod2).

Thus V is an analytic unit. Stationarity gives

    f(Z)=Phi+(Z-c)^2 S(Z),  S integral and a unit.

Consequently there is the exact identity

    f(Z)-A(Z)h(Z)=Phi,
    A(Z)=(Z-c)S(Z)/V(Z) in Z_2<Z>.                         (1)

In particular

    Z_2<Z>/(h) = Z_2,
    class(f)=Phi,
    (f,h)=(Phi,h).                                        (2)

These are isomorphisms and equalities of ideals, not informal evaluations. The
isomorphism in (2) is evaluation at c. It simultaneously accounts for all value
and derivative cancellation. Its rank is one independently of the degree used
in a polynomial approximation.

## 3. A finite Bezout certificate without algebraicity

Let P>=1. Suppose complete polynomials p and q satisfy

    p=f (mod 2^P),  q=h (mod 2^P)

coefficientwise. There are explicitly computable A_P in Z[Z] and an integer
R_P in [0,2^P) with

    p-A_P q=R_P (mod2^P)                                  (3)

coefficientwise. The constant is unique and equals Phi modulo2^P.

Here is a direct construction. Assume p-A_k q-R_k is divisible coefficientwise
by2^k. Reduce its quotient by2^k in F_2[Z], and divide that finite polynomial by
q mod2=Z+c mod2. Write the result as Q_k(q mod2)+r_k. Set

    A_(k+1)=A_k+2^k Q_k,  R_(k+1)=R_k+2^k r_k.

The invariant gains one bit. Starting at k=0 proves (3). Evaluating the exact
analytic identity at c proves R_P=Phi mod2^P. Alternatively, uniqueness follows
from the rank-one quotient (2).

If v2(R_P)=v<P, then (3) proves v2(Phi)=v and therefore nonvanishing. If R_P=0,
the only conclusion is Phi in2^P Z_2. No finite zero residue proves Phi=0.
An approximation to f through P+1 complete coefficient bits supplies both p
and q because division of its derivative by2 loses at most one bit.

This is an explicit local Bezout certificate. It does not use the full-degree
resultant of p and q, nor a number field containing c.

There is a smaller value-only verification of the constant. It is enough to
know f through P complete coefficient bits and h through M=ceil(P/2) bits.
Lift the unique root d of h mod2^M. The isometry of h gives v2(d-c)>=M, and

    f(d)-Phi=(d-c)^2 S(d) in2^(2M) Z_2.

Thus p(d)=Phi mod2^P. This independently verifies R_P while requiring only
half as many center bits as value bits.

## 4. Explicit rational polynomial approximations exist for the actual index

This step genuinely avoids assuming algebraicity of the exact critical point.
It also avoids evaluating 9 to an exponentially large integer representative.

Write

    gamma_q=2^154 * 8^q beta_(r+q)/beta_r,
    f(Z)=2^-178 sum_(q>=0) gamma_q P_q(x) A(x-q),
    x=10202+2^15 Z.

All gamma_q are integral because mu=-154 is the true global carry minimum.
The actual rational beta coefficients give

    v2(gamma_q)=154+3q+s2(r+q)-s2(r).

Since P_q and A are integral restricted, the normalized q-th summand has
Gauss valuation at least

    3q-s2(r)-23.                                          (4)

For P>=1 take

    Q=ceil((P+s2(r)+24)/3).

The omitted q>Q tail is then zero modulo2^(P+1) coefficientwise. A conservative
rational polynomial source approximation is supplied by the exact formula

    A(y) = (sum_(n>=0) 8^n y-underlined-n/(n+1)!)/(1+2y).

The n-th numerator polynomial has Gauss valuation at least2n. Truncate this
sum at M=ceil((P+179)/2), and truncate the geometric inverse of1+2y at
L=P+178. Call the resulting rational polynomial A_(M,L)(y). Its error has
Gauss valuation at least P+179. Therefore

    p_P(Z)=2^-178 sum_(q=0)^Q gamma_q P_q(x) A_(M,L)(x-q)  (5)

is a rational polynomial and satisfies

    p_P-f in2^(P+1) Z_2<Z>.

In particular p_P has 2-integral coefficients, even though its displayed
summands need not individually have that integrality after division by2^178.
The finite Bezout construction applies to p_P and p_P'/2. Formula (5) supplies
an exact finite arithmetic input for each ordinary r and chosen P. No unknown
critical point appears in its construction.

This is a finite certificate construction, not a uniform terminating bound.
The exact target becomes proving that its R_P is nonzero for some P for every
admitted r. A claim such as R_(2r-24)!=0 would be sufficient but is not proved.
The inherited undepletion identities do not imply that claim.

## 5. Why localization does not automatically retain rationality

The tempting stronger implication is false even for a cubic with rational
integer coefficients: localizing to the unique integral critical point does
not necessarily leave a rational scalar or rational rank-one direct summand.

Take

    f_0(Z)=1+2Z+Z^2+256Z^3,
    h_0(Z)=f_0'(Z)/2=1+Z+384Z^2.

The polynomial h_0 is irreducible over Q because its discriminant is -1535.
Over Q_2 it has exactly one integral root c by h_0=1+Z mod2; the other root
has valuation -7. Hence the rational algebra Q[Z]/(h_0) is a field, with no
nontrivial idempotent, whereas its Q_2 scalar extension splits into two fields.
The projector isolating the integral critical point exists over Q_2, not Q.

Reduction using 384c^2=-c-1 gives exactly

    f_0(c)=(1151+1535c)/1152.                              (6)

It is irrational over Q. Its valuation is nevertheless easy to prove. The
critical equation gives v2(c+1)=7, so

    f_0(c)=(c+1)^2+256c^3

has valuation8. This is a counterexample to the proposed rationality transfer,
not an Euler counterexample. It does not rule out special arithmetic identities
for the actual Euler coefficients.

## 6. The attempted rational-height separation and its exact failure

Let d_P be the least integer critical-center lift modulo2^ceil(P/2), and put

    t_P=p_P(d_P) in Q.

By Sections3-4 this is a rational approximation to Phi through P bits. Thus a
valid sufficient arithmetic test is

    t_P!=0 and log2 H(t_P)<P,                              (7)

where H(a/b)=max(|a|,|b|) in lowest terms. This test needs no algebraicity of c.

Write p_P=C^-1 sum_(j=0)^D a_j Z^j with integer coefficients and A=max|a_j|.
The direct available bound is

    log2 H(t_P) <= max(log2|C|,
        log2 A+log2(D+1)+D*ceil(P/2)).                     (8)

The degree in the explicit construction satisfies D<=2Q+M+L, which is linear
in P for fixed r. The bound in (8) therefore includes a quadratic term in P,
before the heights of the actual Bernoulli ratios are included. It cannot
establish (7). This is a failure of this bound, not a theorem that every
low-height rational approximation is impossible.

Compared with direct exact evaluation at a large ordinary argument, (5)
removes the exponential-in-P exponentiation cost from the approximation
argument. It still does not give the strict arithmetic height/error margin.
Replacing (8) by the height of the modular representative R_P would be
circular: proving that representative is nonzero is exactly the desired
finite nonvanishing test.

## 7. Exact finite checks and outcome

The checker uses the existing complete94-bit local coefficient records for
T=0 and T=718787533. It constructs (3) through93 bits and verifies the identity
coefficient by coefficient. The constant remainders have valuations0 and30,
matching the independently lifted stationary values. Their transfer from the
depleted eta=0 records to the actual Euler members is valid at these bits
because the actual undepletion correction begins at2r-25>93.

The checker also evaluates the inherited independent-eta singular residues.
Both return R_93=0, as they must. These are controls in the enlarged analytic
family, not actual singular Euler indices. The rational cubic example is
checked independently and has critical-value valuation8.

No additional multiplier digits were computed. No exact Euler critical value
has been shown zero. The finite coefficient records are reused, not rebuilt.
No Lean compilation was attempted.

The strongest useful conclusion is the explicit, rank-one local arithmetic
certificate and its actual-index rational construction. The missing implication
is still an arithmetic reason that the certificate is nonzero at a controlled
precision for every admitted r. Neither rational polynomial approximation nor
fixed local degree supplies that reason by itself.
