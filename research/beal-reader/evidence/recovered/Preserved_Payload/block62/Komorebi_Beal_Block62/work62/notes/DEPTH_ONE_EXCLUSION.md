# B62.3. Depth one cannot have its complete beta conductor in S

S={197,883,1373,1667}. Retain the actual hypotheses. Suppose n=1 and all beta
ramification is in S. Normalize the SAME global natural class by a5=1:

    alpha=(u,r,1),  u in k=F49, r in k^*.

Let the opposite inertia vector be s=(s197,s883,s1373,s1667), in the compatible
normalization of TWISTED_TRACE_DATA.md. It is nonzero, since a class with no
ramification and split7 is zero by the inherited class-number argument.

## Start with the justified71 condition, not the old three-row kernel

The natural Kummer rows on S are(0,6,6),(0,0,0),(0,3,4),(0,3,4). Ramified beta
forces their value on alpha to be zero. Thus197 support requires r=6, while
1373 or1667 support requires r=1. If r is neither, only883 could ramify, but
R71=(6,2,0,5) excludes a nonzero single883 coordinate.

There are therefore exactly two possible types before the new tests:

    r=6: s=(c,4c,0,0), c in k^*;
    r=1: s=(0,a,b,a), (a,b) in k^2 minus{(0,0)}.         (5)

The coefficient u remains arbitrary. This deduction inspects all48 possible
nonzero k-ratios; it is not an assumed prime-field descent. Counting all u and
parameters in (5) gives119952 candidate pairs.

## Rule for each auxiliary prime

The test primes29,43,491,211,239 do not belong to S, so beta is unramified there
whether or not the curve is good. At a good place the product of the two
Frobenius values must lie in its exact set G_ell. At a bad place the product is
zero. At29 and491 the nonseventh phi condition additionally forces beta itself
to vanish at a bad place. Neither prime is assumed bad in advance.

At split places we allow independent choices from G_ell for the two primes of K.
This is a deliberately larger system than requiring the same actual equation
residue and conjugate comparison. Excluding this larger system is sufficient.

## Reduction at29,43,491: a hand-checkable nine-candidate set

For r=6, beta29=5c is nonzero. Thus29 must be good, and both products equal2.
The two natural29 values differ by u. Hence u=0; solving6c=2 gives c=5.
At491 the product is then3. It is neither zero nor the only rational member5
of G491. The r=6 type is excluded.

For r=1 put s=(0,a,b,a). Direct evaluation gives

    beta29=3a-b,
    alpha43*beta43=2a-b,
    beta491=5a+b.

At29 there are two cases.

1. If beta29=0, then29 is bad and b=3a, a!=0. The43 product is -a, so43 must
   be good and a is one of2,3,4. At491 the products are a(6u+6) and a(u+6).
   Since the scalar parts of G491 are only5 and6, their sum excludes a=3,4.
   At a=2, membership of both values requires the scalar part of u to vanish.
   This leaves a=2,b=6 and u=v*w for v in F7.

2. If beta29!=0, then29 is good. Its two products both equal2, forcing u=0
   and3a-b=5. Thus b=3a+2. The43 condition gives a in{0,1,2,5}. The491 product
   is5-a. Good reduction permits only5 among rational products, hence a=0.
   Bad reduction requires beta491=a+2=0, hence a=5. The other two values fail.

Therefore the remaining nine candidates are precisely

    A: alpha=(0,1,1),    s=(0,0,2,0);
    B_v: alpha=(v*w,1,1),s=(0,2,6,2),  v in F7;
    C: alpha=(0,1,1),    s=(0,5,3,5).                   (6)

The exhaustive check independently gives the staged counts2402,152,9.
These are coefficient/character tuples, not global representations.

## Prime211 leaves just B_0

At211 the natural values are u+2 and -u+2. For A the beta value is2, so the
products are both4. For C the beta value is6, so both products are5. Neither
is a bad-place zero or a member of G211, whose only rational values are0 and6.

For B_v, beta211=3, and the products are6+3v*w and6-3v*w. No nonrational member
of G211 has scalar part6. Thus v=0. Bad reduction cannot evade the conclusion,
since the sum of the products is12=5 mod7, not0.

Only

    alpha=(0,1,1), s=(0,2,6,2)                         (7)

remains. This tuple still passes all preceding necessary tests and is retained
as a negative control against declaring an earlier stage empty.

## Prime239 closes the contradiction

For (7), beta239=2 and both natural239 values are3. Hence both products are6.
If239 is bad, the exact toric trace would require product0. If239 is good,
its products must belong to G239, which contains no rational F7 element.
Both alternatives fail. No good-reduction assumption has been inserted.

Consequently

    actual n=1 => beta ramifies at a prime outside S.  (8)

Additional primes may divide C while beta remains unramified there. Such
additional divisors are already allowed throughout the good/bad tests. New
BETA ramification outside S adds twisted columns and is the remaining case,
not a case covered by (8).

All four actual local49-torsion families in Block60 remain valid. Neither this
argument nor its finite certificate asserts that any one local Frey family
is impossible. The obstruction is their inability, on the stipulated complete
conductor, to satisfy actual Frobenius traces with one common pair(alpha,beta).
