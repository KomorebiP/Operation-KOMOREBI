# Good/bad Frobenius closure

All arithmetic applications retain TARGET_CONTRACT.md.

## B58.1. Two exact finite good-reduction exclusions

The actual inherited Frey curve is

    Z^2=X^6+10 B X^3+12 A X+5 B^2.

For q=41,59, both primes split in K. The two values of
3(5-sqrt5)/2 have the same quadratic symbol: -1 at41, +1 at59.
The independent implementation computes these signs from both roots of5.

For each A,B in F_q, test A^3+B^5 in (F_q^*)^7 individually. In these two
fields gcd(7,q-1)=1, so this is equivalent to A^3+B^5!=0. There are respectively
1640 and3422 admissible pairs. Every one is independently checked smooth by
polynomial gcd. Both zero-coordinate cases are included; (0,0) is excluded.

Let N1,N2 be curve counts, including both rational points at infinity. Put
s=q+1-N1 and c=(s^2-q^2-1+N2)/2. Then the rational Jacobian polynomial is

    Pq(T)=T^4-s T^3+c T^2-q s T+q^2.

The twist multiplies s by nu and leaves c fixed. This follows from the
curve/Jacobian trace formula, Newton identities, and the quadratic twist
on the actual Tate module. The latter identification is an inherited input.

Exact results:

| q | good pairs | full target mod7 | full target mod49 | twisted traces on mod7 locus |
|---|---:|---:|---:|---|
|41|1640|120|0|0,7,14|
|59|3422|116|0|-6,1|

The target is (T-1)^2(T-q)^2. Required rank-four traces modulo49 are35
at41 and22 at59. None of the residual-locus trace values qualifies.
All lower-precision survivors are retained: no depth-one exclusion is claimed.

The primary counts104 weighted curve orbits, in both degrees, filtering
admissibility member by member. The isomorphism is X->uX,Z->u^3 Z with
(A,B)->(u^5 A,u^3 B). The independent program instead counts BOTH degrees
for EVERY one of5062 pairs, with a different quadratic field and explicit
square-root multiplicities. It uses no curve-orbit reduction.

## B58.2. The good/bad implication uses the same representation

Suppose n>=2. At either prime, h=v7(q-1)=0 and m=floor(n/2)+1>=2.
The retained rank-two congruence tau=q+1 mod7^min(n,m) therefore implies the
rank-four target modulo49. B58.1 contradicts good reduction. Hence

    n>=2 => 41*59 divides C.                              (1)

Now these are VARIABLE BAD places, not good ones. At their local groups,
the actual toric trace and the same global eta give

    chi(g) eta(g)+eta(g)^(-1)=chi(g)+1 mod7^n.

Equivalently (eta(g)-1)(chi(g)eta(g)-1)=0. Since eta=1 mod7,
chi(g)!=1 mod7 makes the second factor a unit. Thus eta(g)=1.
A residual-separating Frobenius g0, and then g0*g for any element with
chi(g)=1 mod7, prove triviality on the entire decomposition group.
This proves FULL local triviality at both places over41 and59.
No claim of good reduction is used after (1).

## B58.3. Four actual splitting rows

Generators of those prime ideals are

    pi41=6+phi, bar_pi41=7-phi,
    pi59=7+2phi, bar_pi59=9-2phi.

The norm formula a^2+ab-b^2 gives41,41,59,59. All are units at every
possible highest-layer conductor place, which has h>=2.

If eta is nontrivial, n>=3 and (1) applies. The highest nonzero layer
lambda=eta^(7^(e-1)) is locally trivial at the four new ideals. The
class-number-one ray sequence therefore adds the four generator rows

    sum_v ell_v(pi) lambda_v=0.

These hold for the COMPLETE support of lambda, not just for divisors of C
that are chosen for a computation. Arbitrary additional C divisors without
lambda ramification cannot change the equations. Additional actual highest-
layer ramification contributes additional columns and must be retained.

This is a reusable good/bad mechanism: an excluded good-reduction locus
forces a bad prime; a residual-separation theorem at that bad prime supplies
an actual local character value; global reciprocity supplies a new row.
A necessary divisor alone is not a contradiction.

The H3 toric sign is load-bearing. Using an untwisted toric trace instead
of the stipulated actual twisted trace would not justify these rows.
