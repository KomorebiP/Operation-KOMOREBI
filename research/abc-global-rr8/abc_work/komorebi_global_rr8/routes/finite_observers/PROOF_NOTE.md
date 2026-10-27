# Finite translation observers and their precision cost

Checkpoint ABC-20261025-RR8. Parent RR7 archive SHA-256:
83c7020fd03361142fcac0567bd097c6b61c244f3a953c4618d13fd0cf4ead0a.

## Exact question and conventions

Let A_int=R x product_p Z_p, with ordinary absolute value at infinity
and |p|_p=p^(-1). A diagonal integer m gives coordinates (m,(m)_p).
For an integer n, a translation-norm observer records the archimedean
distance and every individual p-adic norm of x_p-n. When only finitely many
of those norms differ from 1 and none is zero, the associated product test is

    |x_infty-n| product_p |x_p-n|_p = 1.                     (1)

This note tests the sufficiency of a *fixed finite* set of translations.
It does not impose a product formula on every rational function or the
infinite translation contract in the neighboring translation_gluing route.

## Theorem 1: a finite profile cannot certify diagonal membership

Fix a finite set T subset Z. Fix also a finite collection of digit
observers x_q mod q^e, with nonnegative finite exponents e.
There exist a diagonal integer d and a non-diagonal x in A_int such that:

* x_infty=d, so every archimedean observation agrees exactly;
* every declared digit observer has the same value at x and diagonal d;
* for every n in T and every prime q, |x_q-n|_q=|d-n|_q;
* all products (1) for n in T are defined and equal 1.

In fact one can prescribe any d in Z minus T, any prime p, and make the
perturbation at p have arbitrarily large valuation.

### Proof

Choose d outside T, and put

    h=max({v_p(d-n):n in T} union {0}
          union {e: a declared digit observer has prime p}).

For any integer L>h put x_infty=d, x_q=d for q different from p, and

    x_p=d+p^L in Z_p.

These are integral coordinates. The tuple is not diagonal: if it were
diagonal r, its real coordinate would force r=d, whereas x_p differs from
d in Q_p. Every declared p-adic digit observer agrees, because L is
larger than its precision. All other digit observers agree identically.

For n in T we have v_p(d-n)<L, so the unequal-valuation rule gives

    v_p(d+p^L-n)=v_p(d-n).

At all q different from p the equality of norms is immediate. Each d-n is
a nonzero integer, so its individual norms have finite support, are
nonzero, and satisfy the elementary rational product formula. The same is
therefore true for x-n. This proves every assertion.

No finite computation is being extrapolated in this proof. The
construction works for every finite T and every finite set of digit
precisions.

## Corollary 2: any fixed translation window can miss arbitrary precision

For an integer W>=0, take T={n in Z:|n|<=W}, d=W+1 and any prime p.
If p^L>2W+1, then L>v_p(d-n) for every n in T. Therefore the perturbation
x_p=d+p^L has exactly the same entire translation-norm profile as d on
this window, despite differing from d.

The elementary upper bound used here is v_p(d-n) log p<=log(2W+1).
The mismatch can be placed beyond any prescribed finite digit budget by
increasing L further.

The choice d=W+1 is deliberate. This statement does not say that a
finite-window test fails when the source height is already restricted to
a smaller window and exact common-zero membership is separately tested.

## Proposition 3: a precision test with declared integer separation

Suppose x_infty=d in Z, every x_q is integral, and the translation
n=d+p^N, N>=1, satisfies (1) with its full finite nonzero norm profile.
Then x_p is congruent to d modulo p^N.

Indeed the archimedean distance is p^N. Write
k_q=v_q(x_q-d-p^N), which are nonnegative integers, zero for all but
finitely many q. Equation (1) says product_q q^(k_q)=p^N. Unique
factorization forces k_p=N and k_q=0 for q different from p.
Consequently x_p-d-p^N is divisible by p^N, as is x_p-d.

The test produces precision N at a translation whose displacement from
the real coordinate is p^N. Its logarithmic displacement cost is N log p.
This is an explicit sufficient construction, not an optimal lower bound
for every conceivable adaptive observer or an ABC cost estimate.

## Komorebi realization of the finite profile

Use the source set A_int, not just the diagonal subsource. Include a
central raw object with value A_int, a real-coordinate object with value
R, one norm object with value [0,infinity) for each (n,q), n in T, q a
prime, and every declared finite digit object with value Z/q^eZ.
In the view category put arrows from each observer object to the raw
object. For the contravariant Set-valued diagram the restrictions are
the corresponding coordinate, norm and reduction maps. There are only
identity arrows besides these, so functoriality is automatic.

Protect the observer values of a chosen diagonal d. The theorem gives
at least two raw extensions in this protected fiber, one of which is
outside the diagonal source image. Thus the full finite protected
profile is insufficient to recover source membership. This is a
Set-valued extension statement. No additive obstruction quotient is
asserted for the nonlinear norm maps.

## What this changes, and what it does not

The all-translation theorem and this finite-profile theorem are
compatible: infinitely many declared observations can be jointly rigid,
while each fixed finite collection misses a high-precision local change.
This quantifier distinction must survive any finite implementation.

These examples do not have prescribed radical support for an additive
triple. They prove no limitation on every arithmetic reconstruction
method. In particular they are not intended ABC triples and are not
counterexamples to ABC. The neighboring radical_precision route tests
actual integer multiplicative data under that additional support
constraint.

The route remains open for adaptive finite certification at supplied
height and precision. Such certification must report those budgets.
Recovering a budget with log height <= (1+epsilon) log radical+C_epsilon
is a separate open quantitative theorem.

