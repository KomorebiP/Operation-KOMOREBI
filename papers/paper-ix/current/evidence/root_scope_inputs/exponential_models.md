# Finite exponential models with exact source and controlled actual reinsertion

Status: proved finite-exponential dictionary for finite Jacobi models, finite
actual approximants at every precision, and a precise obstruction to retaining
an exact finite moment recurrence. None of these results proves stationary
nonvanishing. No transcendence conjecture or external common-zero theorem is
used.

## 1. Definitions and normalization

Let r>=1 be an ordinary integer. For the target chart r is admitted with
terminal161, mu=-154, x=10202+2^15 Z. Write

    C_r=2^154 (2r)!/(2r-1),
    R_(r,q)=C_r 32^q (2r+2q-1)/(2r+2q)!,
    P_q(x)=2^(-q)(2x)_fall(2q),
    A(x)=(9^(x+1)-1)/(8(x+1)(2x+1)).

Thus the global normalized depleted Jacobi model is

    G^[m](x)=sum_(q>=0) R_(r,q) d_q^[m] P_q(x) A(x-q),
    d_q^[m]=(J_m^q)_(0,0),  J_m=I (mod4),

and its deep-chart normalization is K^[m]=2^-178 G^[m]. The rational matrix
J_m is the inherited leading shifted Jacobi truncation. Its moments are
integral units and the actual depleted moments d_q=D(r+q)/D(r) satisfy

    v2(d_q-d_q^[m])>=h_m=4m+4v2(m!)  for every q>=0.        (1)

These are the proved statements of
`bernoulli_closure/nonintersection/jacobi_height/SAFE_JACOBI_AND_HEIGHT_BOUNDARY.md`.
They include the entire future packet sequence, not just a finite prefix.

Put nu=2r-1 and delta=2^nu. The exact actual Bernoulli correction is

    e_q=(1-delta)/(1-delta 4^q),  e_0=1.                    (2)

The actual packet moments are d_q e_q. The critical-value undepletion scale
elsewhere in the project is E=2r-25=nu-24; it is not nu.

## 2. Full-source summation of a geometric moment mode

For a nonzero algebraic lambda with v2(lambda)>=0, choose an algebraic
square root and put

    t=4 sqrt(lambda),  s=2x+2r,
    D_r(x)=(s)_fall(2r)(s+1)(s+2)=prod_(j=1)^(2r+2)(2x+j),
    E_s(t)=((1+t)^s+(1-t)^s)/2,
    B_r(s,t)=sum_(j=0)^(r-1) binom(s,2j)t^(2j+2)/(2j+2),
    H_r(s,t)=(s+1)[E_(s+2)(t)-1]
               -(s+2)[E_(s+1)(t)-1]-(s+1)(s+2)B_r(s,t).

The original Jacobi eigenvalues are units; the allowed larger domain also
covers4^k lambda for k>=0. Its proof uses v2(t)>=2 and |lambda^q|_2<=1,
so positive valuation only improves convergence.

Both 1+t and1-t lie in1+4 O of a finite dyadic extension; their powers are
unambiguously defined by the convergent binomial/logarithm expansion.
Changing the chosen square root exchanges the plus and minus terms, leaving
all expressions unchanged.

Define the convergent auxiliary series

    F_r(x;z)=sum_(h>=0) z^h (2x)_fall(2h)
                           /[(2r+2h+2)(2r+2h)!].

For t of valuation at least2, the exact identity is

    D_r(x) F_r(x;t^2)=t^(-2r-2) H_r(s,t).                 (3)

Proof: multiplication by(s)_fall(2r) changes the falling factorial to
(s)_fall(2r+2h). The even binomial tail is consequently

    sum_(h>=0) binom(s,2r+2h)t^(2r+2h)
       =E_s(t)-sum_(j<r)binom(s,2j)t^(2j).

Integrate u times this equality from0 to t term by term, using

    integral_0^t u E_s(u)du
      =[E_(s+2)(t)-1]/(s+2)-[E_(s+1)(t)-1]/(s+1).

Multiplying by(s+1)(s+2) proves(3). This is an identity after clearing
D_r; it therefore remains valid at its zeros. The displayed quotient version
away from these zeros has removable singularities. The binomial series and
its integrated form converge coefficientwise on x in Z_2 because v2(t)>=2
beats the factorial denominator loss. Derivatives in x remain convergent.

Now define one complete source mode

    G_lambda(x)=sum_(q>=0) R_(r,q) lambda^q P_q(x)A(x-q).

The q=0 summand is2^154 A(x). For q>=1 use the exact source cancellation

    P_q(x)A(x-q)=P_(q-1)(x)(9^(x-q+1)-1)/8,

and

    (2r+2q-1)/(2r+2q)!=1/[(2r+2q)(2r+2q-2)!].

After setting h=q-1, this gives the full-source formula

    G_lambda(x)=2^154 A(x)
       +4 C_r lambda[9^x F_r(x;t^2/9)-F_r(x;t^2)].         (4)

In particular the source has not been replaced by a constant or by its
leading jet. Combining(3) and(4) gives a finite formula for D_r G_lambda:

    2^154 [D_r/(8(x+1)(2x+1))](9^(x+1)-1)
    +4 C_r lambda{9^x(t/3)^(-2r-2)H_r(s,t/3)
                         -t^(-2r-2)H_r(s,t)}.             (5)

The bracket multiplying9^(x+1)-1 is a polynomial: D_r contains both
2x+1 and2x+2=2(x+1).

## 3. Exact finite-exponential dictionary and its costs

Expanding(5) gives a finite exponential polynomial in x. Its bases are

    1, 9, (1+4sqrt(lambda))^2, (1-4sqrt(lambda))^2,
          (3+4sqrt(lambda))^2, (3-4sqrt(lambda))^2.          (6)

All these bases lie in1+8 O, so the chosen powers are restricted analytic
on x in Z_2. For example
9^x(1+t/3)^(2x)=(3+t)^(2x), with the latter understood as
[(3+t)^2]^x. The square avoids a branch choice for powers of3+t itself.
The algebraic constants(1+t/3)^(2r+1) cause no ambiguity.

Before collecting coincident bases, the polynomial coefficients of the
explicit1 and9 terms have degree at most2r. Those at the four other listed
terms have degree at most1. Indeed their exponential
part is a constant multiple of

    (1 +/- t)^(2x+2r+1)[+/- t(s+1)-1],

and the prefix B_r has degree at most2r-2 in s. Some bases can coincide;
these are upper bounds and do not assume distinctness or coprimality.

No diagonalization assumption is needed for J_m. Over a finite splitting
field, Jordan normal form expresses every moment entry as a finite sum of

    binom(q,j) lambda^(q-j),  0<=j<d_lambda,

where d_lambda is the largest relevant Jordan-block size, and the sum of
these sizes over distinct eigenvalues is at most m. This follows directly
from(lambda I+N)^q=sum_j binom(q,j)lambda^(q-j)N^j. All eigenvalues are
units because J_m=I mod4. Each moment mode is (1/j!) times the j-th lambda
derivative of lambda^q. Apply the same derivative to(5). Convergence permits
this: q-falling-factorial weights have nonnegative dyadic valuation, and
only finitely many derivatives are used.

The four exponential coefficient degrees increase to at mostj+1. The
original prefix coefficients at1 and9 retain degree at most2r. If another
base coincides with1 or9, the collected coefficient can have degree up to
max(2r,max_lambda d_lambda); its contribution is already counted below.
Consequently D_r G^[m] has
at most4m+2 bases and an upper bound

    4r+2+8m                                                (7)

on its constant-coefficient differential-equation order, counting each
polynomial prefactor of degree d as d+1. The bound also holds when bases
coalesce, since coalescence can only reduce this upper bound. A splitting
field for the rational characteristic polynomial and the square roots has
degree at most2^m m! over Q. This is a coarse algebraic-degree bound, not a
bound on a dyadic critical point. Coefficient heights include the prescribed
Jacobi entries, the length-r prefix, factorial denominators, and algebraic
powers of exponent2r+1. No small-height estimate is inferred from(7).

The exact source transform of a finite moment model is thus more structured
than an arbitrary infinite analytic series. The denominator and derivative
qualifications below are essential before applying a common-zero theorem.

## 4. Denominator clearing changes the contact problem at its zeros

D_r has zeros x=-j/2, 1<=j<=2r+2. Its dyadic integral zeros are exactly

    x=-1,-2,...,-(r+1).

Many lie in the target chart: those with -x congruent22566 modulo32768.
Thus D_r is not an analytic unit on the whole chart. Where D_r(x)!=0,

    G(x)=G'(x)=0  iff  (D_r G)(x)=(D_r G)'(x)=0.

At a zero x_0 of D_r, however, (D_r G)(x_0)=0 automatically and
(D_r G)'(x_0)=D_r'(x_0)G(x_0). The cleared function can therefore have a
double zero there merely because G(x_0)=0, without G'(x_0)=0. None of the
finite exponential formulas permits discarding these exceptional points or
assuming global irreducibility/coprimality. Differentiation of the exponentials
also introduces logarithms of the algebraic bases; it does not make an
unknown critical point algebraic or an integer exponent for a logarithmic-form
bound.

## 5. Exact reinsertion does not preserve a finite moment recurrence

Let

    R_m(z)=sum_(q>=0)d_q^[m] z^q=((I-z J_m)^(-1))_(0,0).

It is a nonzero strictly proper rational function: J_m is invertible, so its
resolvent tends to zero at infinity, while R_m(0)=1. Its reduced rational
form therefore has a nonempty finite pole set, all of valuation0. Cancellation
may remove some eigenvalue poles but cannot remove them all.

For the exactly reinserted model let

    M(z)=sum_(q>=0)d_q^[m] e_q z^q.

Equation(2) gives the exact formal identity

    M(z)-delta M(4z)=(1-delta)R_m(z).                      (8)

This proves that M is not rational, without a meromorphic-continuation
hypothesis. If M were polynomial, the right side of(8) could not have a pole.
Otherwise let a and b be the least and greatest valuations among its finite
poles over an algebraic closure. The poles of M(4z) have extreme valuations
a-2 and b-2. A pole of valuation a-2 is below every pole of M; it must
therefore be a pole of R_m, forcing a-2=0, so a=2. But then b>=2, and a
pole of M of valuation b cannot be cancelled by M(4z), whose poles have
valuation at most b-2, or by R_m, whose poles have valuation0. Contradiction.

Thus exact Bernoulli reinsertion makes the moment sequence nonrational and
of infinite constant-recurrence rank for every finite m and ordinary r>=1.
This blocks preservation of the finite Jacobi recurrence. It does not prove
that the transformed function G has no other finite exponential description.

There is a second warning against a careless infinite exponential formula.
The convergent geometric expansion is a sum of complete source blocks:

    G_exact^[m]=(1-delta)sum_(k>=0)delta^k G_[4^k J_m].      (9)

It converges coefficientwise; the moments of4^k J_m have norm at most1,
and the packet convergence estimates give a common bound on each complete
block. For a scalar mode t_k=2^k t, however, the coefficient of an individual
cleared exponential term contains

    delta^k (4^k lambda) t_k^(-2r-2).

Its valuation changes by exactly -k, apart from a fixed offset. The remaining
constant term of its linear polynomial coefficient is a unit, and its
algebraic exponential prefactor is a unit. Hence these individually expanded
terms do not tend to zero as k increases. The binomial-tail cancellations
inside each block are indispensable. Formula(9) must not be rearranged into
a convergent sum of individual cleared exponentials without a new argument.

## 6. Normalized finite actual models at every precision

The obstruction in Section5 does not prevent finite approximations with all
actual corrections retained to a prescribed precision. For K>=1 define

    e_q^[K]=(1-delta)/(1-delta^K)
                 *sum_(k=0)^(K-1)delta^k 4^(kq).          (10)

Then e_0^[K]=1 exactly, and every e_q^[K] is an integral unit. An exact
geometric-sum calculation gives

    e_q-e_q^[K]
      =e_q delta^K(4^(Kq)-1)/(1-delta^K).                 (11)

This vanishes for q=0 and has valuation exactly K nu for every ordinary
q>=1. Therefore the finite moment model

    d_q^[m,K]=d_q^[m] e_q^[K]

has rank at most mK, represented by the blocks4^k J_m for0<=k<K with the
weights from(10). Combining(1) and(11), all q satisfy

    v2(d_q e_q-d_q^[m,K])>=min(h_m,K nu).                 (12)

Unlike the depleted Jacobi moments, these finite actual moments generally
lose exact prefix agreement for1<=q<2m; only q=0 is forced exact. The
all-q error bound(12), not exact prefix matching, is the guarantee.

Take K=ceil(h_m/nu). Reinserting the unchanged factorial factors and full
source, the resulting actual normalized function K_r^[m,K] satisfies

    K_r^[m,K]-K_r in2^L Z_2<Z>,  L=h_m-178.              (13)

This is the same all-tail error as the depleted Jacobi model, with no cap
at the undepletion scale E. Since each approximate moment is a unit, the
packet convergence proof and global carry normalization remain valid.

If L>=9, the inherited quadratic chart persists. Half-derivative error has
valuation at least L-1, unique critical points differ by an element of
valuation at least L-1, and stationary values differ by an element of
valuation at least L. Indeed the direct function error is2^L-integral and
the critical displacement contributes at least2L-2 bits. Thus these finite
models approximate the actual critical scalar at every depth. A strict
nonzero-value/error inequality is still required to infer nonvanishing.

For each finite m,K, Section3 applies block by block. The cleared actual
approximant has at most4mK+2 bases, with differential-order bound

    4r+2+8mK,   K=ceil(h_m/(2r-1)).                       (14)

The same splitting field suffices: eigenvalue square roots only acquire
rational factors2^k. Before collecting coincident bases, the explicit prefix coefficient degrees
are at most2r at1 and9, and the other terms have degrees at most the relevant
Jordan-block size. Collected coefficients obey the maximum of these bounds.
For fixed r and m increasing, mK=O(m^2/r+m); this is not a bounded-order
representation at arbitrary precision. The constants and bases also acquire
powers indexed by K. No assertion of low rational height is hidden in(14).

## 7. A construction-specific rational-height cost

Even the normalized correction factor itself carries an explicit cost. At
q=1, put

    D_K=sum_(k<K)2^(nu k),  N_K=sum_(k<K)2^((nu+2)k).

Then e_1^[K]=N_K/D_K. Since nu is odd,

    gcd(D_K,N_K) divides
    gcd(2^(nu K)-1,2^((nu+2)K)-1)=2^K-1.

For K>=2, the reduced numerator n_K and denominator d_K consequently obey

    n_K > 2^((nu+1)K-nu-2),
    d_K > 2^((nu-1)K-nu).                                (15)

The first bound uses N_K>2^((nu+2)(K-1)) and gcd(D_K,N_K)<2^K;
the second is identical with nu in place of nu+2. The approximation error
at q=1 has valuation K nu by(11), while this numerator-height lower bound
has eventual slope nu+1 in K. For K>nu+2 it already exceeds that error
precision. This is a precise cost for this particular normalized finite-mode
construction. Indeed the exact q=1 factor e_1=(1-delta)/(1-4delta) is
itself one fixed rational number; the growing height in(15) belongs to its
chosen geometric-mode approximants, not to that exact rational value.
Multiplication by Jacobi moments or later discriminant
formation could cancel factors; (15) is not a lower bound for every final
critical expression or a proof against every possible height method.

## 8. Evidence, applicability, and remaining implication

The exact checker verifies108 full-source identities at ordinary x=0,...,8,
r=1,2,3,5 and sqrt(lambda)=1,3,5/3. The common factor2^154 is suppressed
on both sides. It also verifies270 normalized actual-correction identities,
25 exact reduced-height/gcd bounds, and117 generating-function coefficient
identities. These bounded checks corroborate the displayed general proofs.
No actual critical value, additional T digits, or new model-rank search is
performed. Evidence is governed by `contract.json` and recorded in
`certified_run/{manifest.json,results.json}`.

The completed bridge is substantive: finite Jacobi source models are finite
exponential polynomials after an explicit polynomial multiplication, and
normalized finite-mode models approximate the actual target at every depth.
The exact model with undepletion retained has no finite moment recurrence;
individual-mode expansion of its infinite block sum is not a convergent
rearrangement. Finite approximants incur growing order and explicit height
costs. No unconditional common-zero or stationary-discriminant separation
result with these hypotheses has been applied. The missing implication
remains a strict nonzero stationary-value bound below the certified model
error, with the exceptional zeros of D_r handled. The actual Euler target
is still open.
