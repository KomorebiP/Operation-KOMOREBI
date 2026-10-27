# Independent audit of the full-source exponential dictionary

**Normalized claim.** A finite shifted Jacobi moment model, transformed with
the complete Euler source, becomes a finite exponential polynomial after
multiplication by the specified D_r. Jordan blocks are allowed. Exact ordinary
undepletion destroys rationality of the moment generating function, while a
normalized finite undepletion sum gives finite moment rank at most mK and
retains the original all-depth approximation bound when K is chosen as stated.
The note also proves a rational-height lower bound specific to this finite
geometric construction.

**Primary verdict: proved as written in the corrected frozen revision.**
The full-source identity, analytic domain, Jordan dictionary, denominator
exceptions, extreme-pole proof, finite approximation bounds, and scoped height
cost pass this independent audit. No stationary nonvanishing conclusion is
proved by these results.

Reviewer: `/root/cross_cartier_review`. Author files were read-only for the
reviewer. Two corrections were incorporated by the author before the final
freeze: the mode domain was extended explicitly to nonzero algebraic lambda
with v_2(lambda)>=0, covering the nonunit scaled eigenvalues; and polynomial
degree bounds at fixed bases 1 and 9 were qualified before collecting
coincident bases. The total differential-order bounds were unchanged.

Frozen proof SHA256:
`0a663a646486125caa49ce47e4c1f5080335a0032045a43d3c7f9883b097cc60`.
Frozen checker SHA256:
`a6a91d11adaa0b17aa27cabe1eb828d689f4ea2043645a128fc5e9bb300906b2`.
All reviewed artifacts and replay pins are in
`EXPONENTIAL_MODEL_REVIEW_HASHES.json`. No Lean compilation, new model-rank
search, T digit, or numeric range was introduced.

## Dependencies and obligation matrix

The dependencies are the previously reviewed shifted Jacobi all-q error,
the exact actual/depleted Bernoulli ratio, the actual quadratic chart, and
the explicit source A. The new dictionary is derived internally using
binomial summation and finite-dimensional linear algebra. No external
common-zero or transcendence theorem is imported.

| Obligation | Status | Decisive reason |
|---|---|---|
| Packet normalization and complete source | Passed | The exact source cancellation gives the stated F_r difference with factor 4 C_r lambda |
| Auxiliary binomial-tail identity | Passed | Falling-factorial concatenation and termwise integration give H_r after clearing D_r |
| Power branch and nonunit scaled modes | Passed in corrected domain | v_2(t)>=2; all squared exponential bases lie in 1+8 O |
| Jordan modes without diagonalization | Passed | Nilpotent binomial expansion is represented by finite lambda derivatives divided by j! |
| Base count and differential-order bound | Passed | Four variable bases per eigenvalue and degree at most its relevant block size; fixed-prefix terms add 4r+2 |
| Coincident-base degree accounting | Passed after qualification | Merged coefficients use the maximum contributing degree, while summed annihilator orders remain a safe bound |
| Denominator zeros and contact | Passed | D_r has simple zeros; cleared double contact alone is insufficient there |
| Exact reinsertion gives nonrational moments | Passed | A rational solution of the formal dilation identity contradicts the extreme pole valuations |
| Complete-block convergence versus individual exponentials | Passed in stated scope | Block norms are uniformly bounded, whereas the displayed scalar expanded term has valuation decreasing by k |
| Normalized finite correction and rank | Passed | The finite geometric sum fixes q=0 and is represented by K scaled Jacobi blocks |
| All-q and stationary error | Passed | Minimum of h_m and K nu transfers with loss 178; half differentiation loses one further bit |
| Construction-specific height lower bound | Passed | The reduced gcd divides 2^K-1 because nu is odd |
| Actual stationary separation | Not established | A strict nonzero-value/error estimate and denominator-zero handling are still required |

## Full-source summation reconstructed

The exact identity

    P_q(x)A(x-q)=P_(q-1)(x)(9^(x-q+1)-1)/8

holds as an analytic identity, including the removable integer points. Also
`(2r+2q-1)/(2r+2q)!=1/[(2r+2q)(2r+2q-2)!]`. Substituting h=q-1 and
`P_h=2^-h(2x)_fall(2h)` leaves the factor `4 C_r lambda`, with series arguments
`16lambda/9` and `16lambda`. Thus formula (4) retains the complete A and its
9^x term; it is not a constant-source or leading-jet approximation.

For the auxiliary sum, multiplying by `(s)_fall(2r)` concatenates the falling
factorials because s-2r=2x. This turns the summand into the even binomial tail.
Integrating u times that tail and dividing by t^(2r+2) gives the factor
`1/(2r+2h+2)`. The displayed elementary antiderivative of u E_s(u) has the
correct signs. Multiplication by (s+1)(s+2) gives H_r exactly. Apparent
division by these factors is used only before clearing; the final identity
extends through their zeros by analyticity.

An independent integer-index derivation gives the same normalization. Set
j=r+q. After multiplying by D_r, the source sum is proportional to
`(2j-1) binom(s+2,2j)`, with source bracket
`9^(x+r+1)3^(-2j)-1`. Isolating j=r gives the initial `2^154 D_r A` term,
and the remaining even tail is precisely H_r. The extra terminal binomial
index has zero source bracket, so it introduces no boundary term.

For fixed ordinary r the factorial losses are dominated by v_2(t)>=2.
Integral x derivatives remain convergent. The correct mode domain is all
nonzero algebraic lambda with nonnegative valuation: a chosen square root
has nonnegative valuation, so t=4 sqrt(lambda) has valuation at least 2.
This covers the scaled modes 4^k lambda. Changing the square-root sign only
exchanges the two terms in each even expression.

The squared bases in (6) lie in 1+8 O of a finite dyadic extension. Their
restricted powers are therefore unambiguous. In particular
`9^x(1+t/3)^(2x)=[(3+t)^2]^x`; no power of the nonprincipal unit 3+t is
introduced. The unscaled factors with integer exponents are algebraic
constants, independent of a branch choice.

## Jordan modes, orders, and denominator exceptions

For a Jordan block lambda I+N, the exact finite expansion is
`sum_j binom(q,j)lambda^(q-j)N^j`. Each scalar sequence is obtained from
lambda^q by the j-th lambda derivative divided by j!. This is valid for
repeated eigenvalues and makes no diagonalization assumption. Termwise
derivatives of the source series converge: only finitely many derivatives
are used, and for ordinary q>=j the binomial coefficient is integral and
lambda^(q-j) remains bounded in the stated domain.

A derivative increases the polynomial degree of a variable exponential
contribution by at most one. For a relevant block size d_lambda its degree
is therefore at most d_lambda. The two explicit fixed-prefix contributions
have degree at most 2r before merging. If a variable base equals 1 or 9,
its degree may be larger and is retained in the merged coefficient.
Summing annihilator orders nevertheless gives

    2(2r+1)+4 sum_lambda(d_lambda+1) <= 4r+2+8m.

The same reasoning gives 4r+2+8mK for K blocks. Coalescence can reduce this
safe summed bound; distinct bases are not required. The differential
annihilator uses logarithms of the bases in the finite dyadic extension.
The global algebraic splitting-field degree bound does not assert that
those logarithms or a critical point are algebraic over Q.

Clearing D_r must not be treated as multiplication by an analytic unit.
Its integral zeros are exactly -1,...,-(r+1), each simple, and some occur
in the focused chart. Away from them, double contact is equivalent before
and after multiplication. At a zero of D_r, a simple zero of G already
produces a double zero of D_r G. A double zero of G would instead require
order at least three in the cleared function. The note correctly retains
these exceptions and makes no unsupported global common-zero inference.

## Exact versus finitely truncated reinsertion

The Jacobi resolvent R_m is strictly proper because J_m is invertible, and
R_m(0)=1. Thus it has at least one finite pole after cancellation. Every
remaining pole has valuation zero: J_m=I+4K with integral K makes all
eigenvalues units. The exact correction gives the formal rational-function
candidate identity

    M(z)-delta M(4z)=(1-delta)R_m(z).

If M were polynomial, this would contradict a pole on the right. Otherwise,
let a and b be the minimum and maximum valuations of its finite poles.
The minimum valuation a-2 of the poles of M(4z) cannot cancel with M,
so it must equal zero and a=2. The maximal pole valuation b of M then
cannot cancel with M(4z), whose maximum is b-2, or with R_m, whose poles
have valuation zero. Since b>=2 this is impossible. The argument is entirely
formal once rationality is hypothesized; it does not assume a meromorphic
continuation of the actual infinite series.

The complete-block expansion (9) is nevertheless convergent. Scaled matrices
4^k J_m have integral bounded moments and the source estimates give a common
block norm. The factor delta^k tends to zero. Individual expanded exponential
terms are different: for a scalar mode their displayed coefficient changes
in valuation by

    k nu+2k-(2r+2)k=-k.

The other specified constant factors are units. Those terms therefore do
not tend to zero, so expanding and rearranging the complete-block sum is
not justified. This does not exclude a different finite exponential formula
for the transformed function by another argument.

For finite K the normalization factor in (10) makes e_0^[K]=1 exactly.
Every e_q^[K] is a unit. Direct geometric algebra gives (11); for q>=1,
all factors except delta^K are units, proving exact error valuation K nu.
Multiplication by d_q^[m] therefore gives rank at most mK and all-q error
at least min(h_m,K nu). The q=0 moment remains exact, but exact agreement
at 1<=q<2m is generally lost. The corrected note explicitly says so.

Taking K=ceil(h_m/nu) restores the h_m all-q guarantee. The actual packet
scalars and complete source then give the same loss 178 as in the reviewed
parent theorem. For L>=9 the actual chart persists; half-derivative error
is at least L-1, center displacement has that valuation, and the stationary
value error is at least L because displacement contributes at least 2L-2.
No cap at E=nu-24 is imposed, since the finite correction itself is
approximated to the selected precision.

## Height claim and evidence scope

At q=1 the normalized correction is N_K/D_K. A common divisor of these
geometric sums divides both `2^(nu K)-1` and `2^((nu+2)K)-1`. Since nu is
odd, their gcd is `2^K-1`. Dividing the largest summand lower bounds by
this gcd bound gives exactly (15). For K>nu+2, the numerator-height lower
bound exceeds the correction's K nu error precision. This concerns the
chosen finite geometric representation only. The exact e_1 is itself a
fixed rational number; later moment multiplication and discriminant
formation could also cancel factors. The note correctly states both limits.

The checker was inspected and replayed only in its declared ranges into
`review/exponential_replay`. Results are byte-identical to the author result,
and both manifests validate. The replay covers 108 full-source identities,
270 correction identities, 25 height/gcd checks, and 117 generating-function
coefficient identities. The sampled full-source modes are units; the
nonunit-domain extension, Jordan argument, pole contradiction, and all-depth
stationary theorem are justified by the proofs above, not silently inferred
from those samples. No actual critical scalar was computed.

The remaining mathematical implication is a strict nonzero model
stationary-value bound below the certified approximation error, together
with correct treatment of the zeros of D_r. The finite exponential
dictionary makes that question more explicit but does not supply such a
separation theorem.

Self-review: conservative proofreading covered this report. The two author
scope corrections are recorded above. No unresolved local issue remains.
