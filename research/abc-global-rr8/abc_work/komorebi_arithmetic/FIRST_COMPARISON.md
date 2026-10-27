# First independent multiplicative dilation test

Base: ABC-20261025-RR6, archive SHA-256
026d1f544ba86acc3fd9d63b75b4a8fc73595407f67e15f1b9b7f7e5144d993a.
This is an independent candidate inside Realization Calculus. It does not
assert that the following elementary power map models the full IUT link.

## The two arithmetic realizations

Fix an integer s>=2. On the set I_s={n^s:n is a nonnegative integer}, define

    x plus_s y=(x^(1/s)+y^(1/s))^s.

The roots here are the unique nonnegative integer roots. Give I_s its
ordinary multiplication. Then n -> n^s is a semiring isomorphism from
nonnegative integers with ordinary addition and multiplication to I_s
with plus_s and multiplication. This follows by transporting each law;
multiplication is unchanged since (mn)^s=m^s n^s. This realization is
therefore exact as a semiring with its declared law.

For a primitive positive a+b=c, the transported relation is

    a^s plus_s b^s=c^s.

The ordinary-addition comparison is a different arrow, with integer defect

    D_s=c^s-a^s-b^s
       =sum_(k=1)^(s-1) binom(s,k) a^k b^(s-k)>0.          (1)

In particular D_2=2ab and D_3=3abc. No addition compatibility is inferred
merely from the multiplicative isomorphism. The diagram commutator (1)
is an explicit residual in the ordinary integer view.

Before this comparison, the radical of the three coordinates remains
rad((abc)^s)=rad(abc), while the logarithmic output height is s log c.
An apparent height amplification with unchanged support has thus been
constructed, but it belongs to the transported additive realization.
It is not yet an ordinary additive ABC triple.

## Protected ordinary repair has a concrete cost

Protect the first two coordinates a^s and b^s. Restoring ordinary addition
then forces the third coordinate to be

    c_s=a^s+b^s=c^s-D_s.                                  (2)

This is a positive primitive additive triple. The correction is unique
under these protected data. Declare its additive correction norm to be
the usual integer absolute value D_s, and its logarithmic cost to be
log(1+D_s). These are explicit cost choices, not a cost inferred from
the existence of the semiring isomorphism.

For every fixed s>=2, this logarithmic cost is not uniformly sublinear
in the original height. Indeed use a=1,b=t,c=t+1, t>=1. Then

    s t^(s-1) <= D_s <= (2^s-2)t^(s-1),

by the binomial expansion with positive coefficients. Hence

    log(1+D_s)/log c -> s-1    as t -> infinity.             (3)

The formal height increment from log c to s log c is also (s-1)log c.
This candidate therefore does not give a free height gain when its
ordinary additive correction is measured in this stated norm. The result
does not rule out different adaptive comparisons or cost estimates with
an independently justified arithmetic meaning.

## The radical after repair must be recomputed

Since b=-a modulo c and gcd(a,c)=1,

    gcd(c,c_s)=gcd(c,2)       if s is even,
    c divides c_s            if s is odd.                  (4)

For odd s, write Q_s=c_s/c. The alternating factorization gives

    Q_s=sum_(k=0)^(s-1) (-1)^k a^(s-1-k)b^k,
    Q_s congruent s a^(s-1) mod c,
    gcd(c,Q_s)=gcd(c,s).                                   (5)

Thus even dilation can lose all odd primes of the old c, while odd
dilation retains c and introduces the quotient Q_s. In either case
the repaired radical is rad(ab c_s); no theorem here bounds it by the
original radical at a useful height scale. Equations (4)-(5) follow
from modular reduction and multiplication by the unit a^(s-1) modulo c.

## Outcome of the attempt

We have constructed two exact arithmetic presentations and an explicit
comparison residual, together with a protected correction and its cost.
The candidate mechanism fails to yield the required sublinear correction
cost in the chosen ordinary norm, by the universal family (3). Treating
the transported relation as ordinary addition or retaining the original
radical after repair would conceal the missing arithmetic estimate.

The next positive target is a different comparison whose residual and
reconstruction cost admit a bound from radical/conductor data while its
output remains an intended global arithmetic point. Such a bound is not
proved here. No ABC counterexample, IUT refutation, or novelty claim is
made. These are written algebraic proofs, with no Lean run or load-bearing
finite computation.
