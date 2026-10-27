# Translation norm tests recover the intended diagonal source

RR8 route: translation_gluing. Base checkpoint: RR7 archive SHA-256
`83c7020fd03361142fcac0567bd097c6b61c244f3a953c4618d13fd0cf4ead0a`.

This note strengthens the weak adelic contract tested in RR7. It uses the
ordinary translated elements x-n, with the same marked integer n in every
completion, rather than balancing the norms of three unrelated coordinates.
It does not import a global-field characterization theorem. The resulting
source-recovery theorem does not provide a radical-dependent height bound.

## 1. A product convention and the exact rational theorem

Let E_Q=R times product_p Z_p. Write a point as x=(t,(x_p)_p), where t is a
real number and each x_p is a p-adic integer. For n in Z define

    P_n(x)=product_p |x_p-n|_p in [0,1].

The product is the infimum of its finite subproducts. Every factor is in
[0,1], so this definition always exists. A zero factor gives product zero.
For x_p-n nonzero, write |x_p-n|_p=p^(-v_p(x_p-n)); its valuation is a
nonnegative integer.

The translated test at n is the Boolean condition

    T_n(x):  t=n  OR  (|t-n| P_n(x)=1).                 (1)

Thus the test imposes no condition at a zero archimedean difference. In
particular, no rule asserting that an archimedean zero is simultaneously
zero at the finite places is built into the definition.

**Theorem 1.** All tests T_n(x), n in Z, hold if and only if there is an
integer m such that t=m and x_p=m in Z_p for every prime p.

Proof. If x is the diagonal integer m, the test at n=m holds by its first
alternative. For n!=m, unique factorization of the nonzero integer m-n
gives |m-n| product_p |m-n|_p=1, so the second alternative holds.

Conversely, if t is not an integer, choose an integer n with
0<|t-n|<=1/2. Since P_n(x)<=1, the product |t-n|P_n(x) is strictly less
than 1. Neither alternative of (1) holds. Therefore t=m is an integer.

Fix a prime p. For every positive integer k, the integer n=m+p^k differs
from t. Its test gives

    product_q |x_q-m-p^k|_q = p^(-k).                  (2)

A positive product of the indicated integral local norms has only finitely
many nonunit factors. Indeed, infinitely many positive valuations would
give finite subproducts at most 2^(-r) for arbitrarily large r, forcing the
infimum to zero. No factor can be zero either. Consequently (2) is an
equality between finite products of rational prime powers. Unique prime
factorization gives

    v_p(x_p-m-p^k)=k.                                  (3)

In particular x_p-m is divisible by p^k. This holds for every k, so
x_p=m in Z_p. Repeating for every prime proves the assertion. QED.

The proof actually uses only the nearest-integer tests to establish the
archimedean marking and then the prime-power translation tests based at
that integer. It does not need a product formula at the zero translate.
Omitting an explicit common-zero axiom therefore does not produce a
counterexample to this full-family theorem. This is stronger than the
initial candidate contract that included such an axiom.

## 2. The actual Set-valued view system

Use a category with objects raw, arch, local_p, residue_(p,j) for p prime
and j>=1, and test_n for n in Z. Include arrows

    arch -> raw,       local_p -> raw,       test_n -> raw,
    residue_(p,j) -> local_p,
    residue_(p,j) -> residue_(p,j+1).

Impose the relations identifying all paths with the same endpoints.
In particular, both ways of restricting a finer residue through local_p
or an intermediate residue level agree. This defines a small poset
category, with residue arrows into raw supplied by composition.
Let F be the contravariant Set-valued functor with

    F(raw)=E_Q,          F(arch)=R,         F(local_p)=Z_p,
    F(residue_(p,j))=Z/p^j Z,              F(test_n)={false,true}.

Restrictions from raw are the actual projections and the actual Boolean
functions T_n from (1). Restrictions between residue objects and from
local_p are ordinary modular reductions. These maps satisfy the declared
relations by the compatibility of reduction. All maps, including the
nonlinear norm tests, are maps of sets. No additive correction quotient is
being imposed on the mixed diagram.

Protect the value true at every test_n object. Every coherent extension
is determined by its raw component, and its raw component must pass every
T_n. Theorem 1 therefore identifies this protected coherent-extension
fiber exactly with the source Z through the diagonal map

    m |-> (m,(m in Z_p)_p).

This is an intended-source image theorem. The source coordinate is not
included as an object and its existence is not part of the definition of
the allowed raw points. It is recovered from the explicitly supplied
local, archimedean and translated-norm observations.

The restrictions deliberately carry more arithmetic information than a
multiplicative reduct. They use the same labelled integer n and the
ordinary local subtraction x_p-n at every place. This theorem cannot be
inferred from multiplication alone, and it does not prove that a proposed
link preserving a multiplicative reduct preserves these test functions.

## 3. Gaussian integers: the one-complex-place analogue

The same mechanism works over K=Q(i), the fixed field of the RR7 weak
adelic counterfamily. Write O=Z[i], let v run over its finite places, and
let O_v be the local integer ring. For a Gaussian prime pi_v write

    N_v=|O/(pi_v)|,       |y|_v=N_v^(-ord_v(y)).

At the complex place use the standard squared absolute value. Put
E_K=C times product_v O_v. For x=(z,(x_v)_v) and a in O, define

    P_a(x)=product_v |x_v-a|_v,
    T_a(x): z=a OR (|z-a|^2 P_a(x)=1).                 (4)

Again the product is the infimum of finite subproducts in [0,1].

The elementary arithmetic used below can be obtained directly from the
Gaussian norm. Rounding both real and imaginary parts gives Euclidean
division with remainder of norm at most one half the divisor norm. Thus
Z[i] is Euclidean; the gcd identity implies that irreducibles are prime,
and induction gives unique factorization. The index of multiplication
by u+iv is its determinant u^2+v^2. For a Gaussian prime above a rational
prime p, its quotient is a finite field of cardinality p^f for f=1 or 2.
Writing the factorization of p with exponents e_v and taking norms gives

    N_v=p^(f_v),        sum_(v|p) e_v f_v=2.            (5)

The rational integer p has local order e_v at v|p and order zero at the
other finite places. These facts also prove the Gaussian-integer product
formula |a|^2 product_v |a|_v=1 for nonzero a in O.

**Theorem 2.** All tests T_a(x), a in Z[i], hold if and only if x is the
diagonal image of a Gaussian integer m.

Proof. Diagonal Gaussian integers satisfy the tests by their product
formula, with the zero translation skipped. For the converse, choose a
nearest Gaussian integer a to z by rounding both real and imaginary parts.
If z is not itself Gaussian integral then

    0<|z-a|^2<=1/2<1.

As P_a(x)<=1, its test fails. Thus z=m belongs to O.

Fix a rational prime p. For every k>=1 use a=m+p^k in (4). Its nonzero
archimedean difference has squared absolute value p^(2k), so

    product_v |x_v-m-p^k|_v=p^(-2k).                  (6)

As before, a positive product implies that only finitely many local
valuations are positive and none is infinite. Factoring the positive
rational numbers N_v into rational primes in (6) gives

    sum_(v|p) f_v ord_v(x_v-m-p^k)=2k.                (7)

For a place v|p at which x_v=m, its contribution is f_v e_v k. At any
place v|p for which x_v!=m, write A_v=ord_v(x_v-m), a fixed nonnegative
integer. For all sufficiently large k, e_v k>A_v, and the nonarchimedean
valuation of x_v-m-p^k equals A_v. Since only finitely many places lie
above p, equation (7), for every sufficiently large k, becomes

    2k = k sum_(v|p, x_v=m) f_v e_v
           + sum_(v|p, x_v!=m) f_v A_v.              (8)

If any place above p had x_v!=m, the slope of the right side would be
strictly less than 2, by (5). Equality for all large k would be impossible.
Thus every x_v above p equals m. Letting p vary proves the theorem. QED.

The same raw/local/residue/test category as in Section 2, now with local
integer rings O_v, their finite residue quotients and tests indexed by
Z[i], gives a Set-valued Komorebi system whose protected extension fiber
is exactly the diagonal Z[i]. This assertion uses the actual maps (4),
not the weaker three-coordinate norm balance from RR7. The theorem
excludes the unintended weak adelic points by an explicitly stronger
compatibility contract. It makes no assertion that those points violate
ABC or that the new tests are preserved by IUT links.

## 4. A genuinely finite-resolution rational variant

The full-family theorems involve infinitely many tests and arbitrarily
fine local information. A finite variant recovers a prescribed finite
resolution at a supplied archimedean budget. Its conclusion is purposely
weaker than exact diagonal membership at all local precisions.

Fix an integer B>=1, a finite set S of rational primes, and an integer
N>=1. Define

    M={m in Z: -B<=m<=B},
    T=M union {m+p^N: m in M, p in S},
    D=2B+max({p^N:p in S} union {0}),
    Q={q prime:q<=D}.

Every nonzero difference m-n with m in M and n in T has magnitude at most
D. Each p in S belongs to Q. Choose an integer L>N with 2^L>D. The raw
finite-resolution space is

    E_fin=[-B,B] times product_(q in Q) Z/q^L Z.

For r_q in Z/q^L Z and n in T, let c_(q,n)(r_q) be the largest j in
{0,...,L} for which r_q=n modulo q^j. This is a well-defined capped
valuation determined by the finite residue. Define the Boolean test

    T_n^fin(t,r): t=n OR
       (|t-n| product_(q in Q) q^(-c_(q,n)(r_q))=1).  (9)

There are finitely many translations, primes and local residue objects.
The remaining real coordinate is retained exactly. The observer values
are exact mathematical values, not floating-point approximations.

**Theorem 3.** Every diagonal integer m in M satisfies all tests (9).
Conversely, a point satisfying all these tests has t=m in M and

    r_p=m modulo p^N             for every p in S.    (10)

Proof. For the forward direction, when n!=m every prime factor of m-n
belongs to Q, and |m-n|<=D<2^L<=q^L implies v_q(m-n)<L. Thus none of
the relevant valuations is truncated, and the ordinary integer product
formula proves (9). The test at n=m holds by its first alternative.

Conversely, if t is not an integer, some n in M has 0<|t-n|<=1/2.
All the finite factors in (9) are at most 1, so this test fails. Thus
t=m is an integer in M. Fix p in S and use n=m+p^N in T. This n differs
from t, and its test gives

    product_(q in Q) q^(-c_(q,n)(r_q))=p^(-N).

Unique factorization gives c_(p,n)(r_p)=N. As N<L, this in particular
implies r_p=n=m modulo p^N, proving (10). QED.

Declare the finite star-shaped view category with raw object E_fin,
arch object [-B,B], local residue objects Z/q^L Z and Boolean test
objects indexed by T. Restrictions are the corresponding projections
and (9), and all test values are protected true. Theorem 3 says that the
image of its extension fiber under the projection

    (t,r) |-> (t,(r_p modulo p^N)_(p in S))

is exactly the finite-resolution diagonal graph of M. Surjectivity onto
that graph is supplied by the actual diagonal residue family of each m.
It does not say that every point of the larger raw fiber has all local
coordinates equal to m at every precision.

The parameter B is an input. The translation set, prime set and precision
L explicitly depend on B and the requested resolution. In particular,
this theorem does not construct B from rad(abc), and it supplies no
constant independent of B for the cost of the tests. A complementary
RR8 finite-test insufficiency route is owned by the coordinator; no
claim of exact certification from an arbitrary finite test list is made
here.

## 5. Arithmetic consequence and the remaining height gap

Apply Theorem 1 separately to three raw rational coordinates. If they
pass every translated test, their archimedean values are the same
ordinary integers as all their finite local coordinates. Adding the
actual local or archimedean relation a+b=c and the usual positivity and
primitivity observations then gives exactly the intended ordinary ABC
source. Theorem 2 supplies the corresponding Gaussian-integral statement.

These are positive source-recovery results. They replace the previous
weak coordinatewise norm contract by one whose extension fiber is proved
to be the correct source. The retained translated additive markings are
essential data of the new construction, not an automatic consequence of
the earlier weak contract.

On genuine diagonal additive triples, all translated tests already hold.
They impose no new inequality between log c and log rad(abc). Neither
their availability, the inverse-limit reconstruction nor the finite
resolution theorem gives

    log c <= (1+epsilon) log rad(abc)+C_epsilon

with C_epsilon independent of the triple. The remaining program needs an
arithmetic estimate for the amount or cost of this compatibility sufficient
to control height from radical data. A finite family depending on a
supplied height budget cannot be substituted for such an estimate.

Evidence: complete elementary written arguments in this note. No Lean
run, proof-assistant formalization or load-bearing numerical experiment
has been performed for these claims. Historical novelty is not asserted.
