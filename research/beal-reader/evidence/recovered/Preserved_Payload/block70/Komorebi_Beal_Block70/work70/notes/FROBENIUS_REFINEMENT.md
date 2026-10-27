# B70.2–3. Exact nine-prime classification in the bounded depth-one branch

Retain all inherited actual hypotheses, n=1, and COMPLETE rational beta ramification
at primes<=2000. The frozen Block69 list is a necessary cover of18 tuples.
The split primes2129,2269,2311 are greater than2000 and therefore outside that
conductor. No good-reduction assumption for the curve is inserted.

In the basis1,zeta,...,zeta^5, integral generators of norm ell are

    2129: (-2,-2,1,0,2,-2)
    2269: (-2,-2,0,-1,2,2)
    2311: (-2,-2,-1,2,-1,0).

Norms are verified by multiplication determinants and a separate product-of-conjugates
algorithm. Their roots identify the natural and twisted residue normalizations.
Targeted certificates at all three primes retain both good and bad alternatives.

|ell|All admissible pairs|N1 curve classes|Required N2 classes|Remaining after stage|
|---:|---:|---:|---:|---:|
|2129|647216|2129|157|14|
|2269|735156|2271|90|12|
|2311|762630|2317|110|8|

Every2,145,002 admissible pair is checked for equation membership, curve assignment,
and smoothness by the secondary implementation. The degree-two coverage357 is
complete for the targets in TARGETED_CERTIFICATE.md, not a full good-polynomial list.

## The old eight-prime pair fails at2269

Its natural coefficients are alpha=(+/-2w,4,1), with inertia
(4,6,2,3,5,6,1,2) on113,307,463,617,883,967,1483,1723. The actual twisted row
gives beta(F)=1. Both natural rows at2269 are(0,4,4), so both products are6.
They are nonzero and hence cannot arise from the bad toric trace.

Their coefficient trace/norm signature is(5,1). Every admissible curve whose exact
first trace could give5 is counted to degree2:41 curve classes. On the full residual
polynomial locus inside that trace slice the only correction pairs are

    {6+w,6-w}, {6+2w,6-2w}, {6+3w,6-3w}.

Their norms are3,2,5, never1. Thus the actual good case also fails. This is an
exhaustive trace-slice exclusion, not a claim that all other trace slices were
computed. It excludes BOTH conjugate old minimum tuples.

## Complete surviving list and consequence

The complete survivors are the eight records in refinement70.json. They have
ratio r=6, exactly nine nonzero rational inertia coordinates, and mandatory support

    D={307,337,547,883,1483,1933}.

Each support is D together with exactly three of{197,673,743,797}. The four inertia
patterns, each accompanied by the displayed coefficient conjugate, are in SURVIVORS.md.
Thus an ACTUAL bounded-conductor depth-one representation must have one of those
four patterns. This conclusion is conditional on the complete-cover theorem, not
an assertion that the patterns are realized. No condition on all divisors of C
or on prime multiplicities is silently added.

In particular the result is EXACTLY nine primes in this bounded necessary system,
not merely a lower bound of nine. Changing the allowed beta conductor changes the
system and invalidates extending this classification without adding all new columns.
