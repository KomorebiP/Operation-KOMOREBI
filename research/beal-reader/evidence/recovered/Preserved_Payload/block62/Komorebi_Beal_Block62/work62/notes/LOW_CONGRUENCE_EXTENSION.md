# B62.4. Including three genuine low-congruence conductor primes

The depth-one target cannot omit possible low-congruence beta ramification.
The following extension explicitly includes three such primes:

    Splus={43,113,127,197,883,1373,1667}.

All are inert in K/Q and1 mod7. Thus the same cohomological descent and
chi^-1 reciprocity apply. At43,113,127, h=v7(q^2-1)=1 and phi is a seventh
power, so none is removed merely by the older high-support or phi conditions.

## New columns, with the correct twist

For113 and127 use prime generators, in the cyclotomic basis,

    pi113=(-1,-1,0,-1,1,1),
    pi127=(-2,-2,-2,1,1,1).

Their norms are113 and127. The pi43 generator is already in the base certificate.
The residue generators are3 at these three primes, while the original four
support primes use2. The definitions are per-column consistent, not an
unrecorded identification of local generators.

In column order197,883,1373,1667,43,113,127 the relevant Frobenius rows are

    R29  =(4,2,6,1,2,6,5),
    R71  =(6,2,0,5,4,2,3),
    R491 =(3,6,1,6,1,3,0).

The new natural Kummer zero conditions impose respectively

    43 ramified  => r=5,
    113 ramified => r=4,
    127 ramified => r=2.

They cannot occur together, or with197,1373,1667 ramification, because those
places require different values of the SAME ratio r. The883 row is zero.
Therefore, if one of the three added primes ramifies, all remaining possible
ramification is at883. The71 equation gives, up to a nonzero scalar c in k:

    43:  (s883,s43)=(5c,c), r=5;
    113: (s883,s113)=(6c,c),r=4;
    127: (s883,s127)=(2c,c),r=2.

These are not assertions that only two arbitrary primes can ramify in general.
They follow on this explicitly specified Splus from incompatible natural ratios.

## The same two actual test primes exclude the three types

In the43 type, beta29=5c. The two products at good29 force u=0 and c=2;
bad29 is impossible because beta29!=0 and phi is not a seventh-power residue.
At491 the product is then6, whereas its good rational product set is{5},
and a bad place requires0. Contradiction. NO unramified Frobenius test at43
has been imposed in this ramified43 case.

In the113 type, beta29=4c, and the same reasoning gives u=0,c=2. The491
product is4, again neither the good rational value5 nor the bad value0.

In the127 type, beta29=2c!=0. The two natural values at29 are4u and3u,
which are opposite. They cannot both give product2. Bad29 is again impossible.

The three additional types comprise2352 parameter choices each. Independent
checks of all7056 choices reproduce these exclusions. Thus

    actual n=1 => beta ramifies outside Splus.        (9)

If none of the added primes ramifies, B62.3 supplies the original four-prime
exclusion. This proves (9) for all possible conductors contained in Splus,
not only for conductors containing every displayed prime.
