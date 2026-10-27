# The radical-height envelope and exact source recovery

Checkpoint ABC-20261025-RR8, parent RR7 archive
83c7020fd03361142fcac0567bd097c6b61c244f3a953c4618d13fd0cf4ead0a.

## Target and source

Let X be the set of ordered positive integer triples (a,b,c) with a+b=c
and gcd(a,b)=1. Let R(a,b,c)=rad(abc). For real T>=2 define

    X_T={x in X:R(x)<=T},       B(T)=max{c:(a,b,c) in X_T}.       (1)

We first prove that this maximum exists. We do not use (1) to claim an
effective algorithm or an already known near-linear bound.

The source-dependent leaf is fixed-support finiteness, verified in the
fixed_support route against Evertse, Schlickewei and Schmidt, Theorem 1.1,
author preprint https://pub.math.leidenuniv.nl/~evertsejh/00-equation.pdf,
checked 2026-10-25, PDF pages 1-2. The source theorem bounds the NUMBER of
nondegenerate solutions in a finite-rank multiplicative group. It is not
a height bound. Its exact version/hypotheses and application are recorded
in that route; no source proof is reproduced or claimed rechecked here.

## Theorem 1: finite radical fibers, without a growth estimate

For every T>=2, X_T is finite and nonempty. Consequently B(T) exists as a
finite positive integer, is nondecreasing, and bounds every intended
integer realization with radical at most T.

### Proof

Let S_T be the finite set of primes at most T. Every triple in X_T has
all its prime factors in S_T. Put

    U_S={product_(p in S) p^(e_p):e_p in Z} subset Q_(>0).

For x=(a,b,c), the pair (a/c,b/c) lies in U_S x U_S, a group of rank 2|S|,
and solves u+v=1. In an algebraic closure of Q, Theorem 1.1 applies with
n=2, coefficients 1,1 and rank 2|S|. Both variables are nonzero, so no
nonempty subsum vanishes. Hence only finitely many pairs occur.

The map from primitive triples is injective. Indeed a/c is reduced because
gcd(a,c)=gcd(a,a+b)=1. Its reduced positive numerator and denominator
recover a,c, and then b=c-a. Thus X_T is finite. The triple (1,1,2)
belongs to X_T for T>=2, proving nonemptiness.

This uses classical Diophantine finiteness, now coupled to the explicitly
reconstructed intended source. The known counting theorem is not a new
ABC bound and supplies no numerical value for the maximum in (1).

## Theorem 2: an elementary lower scale

For every real T>=4,

    B(T)>T/4.                                                   (2)

Choose n=floor(log_2(T/2)), so n>=1 and T/4<2^n<=T/2. The primitive triple
(1,2^n-1,2^n) has radical

    2 rad(2^n-1)<=2(2^n-1)<2^(n+1)<=T.

Its c-coordinate is 2^n, proving (2). In particular

    liminf_(T->infinity) log B(T)/log T >= 1.                     (3)

No assertion is made that this family supplies unusually good ABC
qualities; it only fixes the scale of this height envelope.

## Theorem 3: the exact remaining growth target

The usual ABC conjecture for positive primitive integer triples is
equivalent to

    lim_(T->infinity) log B(T)/log T = 1.                        (4)

Here the ABC formulation is: for every epsilon>0 there is a finite
C_epsilon such that

    log c <= (1+epsilon)log rad(abc)+C_epsilon                   (5)

for all x in X.

### Proof

If (5) holds, every triple in X_T satisfies
log c<=(1+epsilon)log T+C_epsilon. Take the maximum, then the limsup.
For every epsilon>0 this gives limsup<=1+epsilon, hence limsup<=1.
Combine with (3) to obtain (4).

Conversely, if (4) holds, fix epsilon>0. There is T_0>=2 such that
B(T)<=T^(1+epsilon) for all T>=T_0. For a triple with radical R>=T_0,
c<=B(R)<=R^(1+epsilon). For the remaining triples, R<T_0 and
c<=B(T_0). Thus (5) holds with C_epsilon=log B(T_0), for example.

The proof does not estimate the onset T_0 or C_epsilon. Equation (4)
is an exact quantitative target, not evidence that the target is true.

## Source-aware finite-view consequence

For fixed T let G_N(T) be the image of X_T in triples modulo N!, N>=3.
These images form a contravariant inverse system under reduction. The
natural map

    X_T -> lim_N G_N(T)

is a bijection.

Indeed take N_0 with N_0!>B(T). Reduction is injective on positive
coordinates bounded by B(T). At all N>=N_0 the image map identifies
G_N(T) with the same finite set X_T, and reduction maps become identities
under those identifications. Hence the inverse limit is exactly X_T.

This is an intrinsic source-image statement, since G_N(T) is defined as
the image of actual exact triples. It is NOT a proof that arbitrary
locally compatible residue triples with fixed radical are eventually
exact. The radical_precision route gives an explicit obstruction to
that stronger assertion. Nor does this proof compute N_0 without a
height bound or an independently effective procedure.

## Coupling to the Komorebi construction

The full translated product-formula system in translation_gluing recovers
one diagonal integer from the ambient real and p-adic coordinates.
Apply it to each of the three coordinates. Protect positivity, primitive
local behavior and exact additive compatibility. The surviving coherent
families then identify with X. Protect R<=T to obtain X_T, a finite fiber
by Theorem 1.

Thus this pass replaces the earlier *supplied* integer height budget by
a qualitative radical-dependent existence theorem after enforcing the
intended source. It does not yield the near-linear growth of that budget.
It also does not turn the nonlinear radical observation into a bounded
linear map or make the Hilbert-space repair theorem a proof of (5).

## Active quantitative question

The global target remains (4). A useful next arithmetic estimate must
bound the largest exact intersection of the exponential integer
coordinate locus with a+b=c as S varies, while accounting for the sizes
of its primes. The fixed-support cardinality theorem, local carry
reconstruction and global translation tests do not provide this growth
rate. They are verified dependencies and controls for an attempted
quantitative comparison, not substitutes for it.

