# Beal research, Block59
## Natural49-torsion and a geometric nodal-period obstruction

Version5.9.0. 19September2026.

The depth-two target is not completely eliminated. This block proves a new
necessary condition using the actual Frey Jacobian's geometry, reduces its
possible ramification support in the retained ten-prime class, and resolves
the previously undetermined vanishing of the global unit coefficient at bad13.
All arithmetic statements retain TARGET_CONTRACT.md's inherited hypotheses.
Evidence consists of written proofs and exact finite checks, not new Lean
compilation or independent mathematical review.

## 1. At depth two the natural representation is locally trivial modulo49

Let beta ramify at a variable place v. In the fixed natural basis, write

    N=mu[[-xy,x^2],[-y^2,xy]], F=I+(x,y)^T(p,r).

At n=2, the actual eta_2 is trivial. The inherited ramification formula gives
s=w(y)=0,t=w(mu)=2. Thus y is a unit. The SAME Frobenius entries give

    yp=F21 in49O, yr=F22-1 in49O.

It follows that p,r are in49O, while every entry of N is in49O. Therefore

    rho_natural|G_v=I mod49,
    J^nu[49] is entirely K_v-rational.

This is stronger than vanishing of the residual class alpha. It concerns the
natural Jacobian lattice, not just the changed lattice defining beta. More
generally beta support forces natural precision d=min(t,floor(t/2)+1), and a
maximal-order eta inertia place forces natural precision t.

## 2. The geometry supplies a previously unused unit period

The normalized twisted stable fiber is

    Z^2=delta*(X^2+X-1)^2*(X^2-2X+5),
    delta=3(5-sqrt5)/2.

Its normalization is the split conic Y^2=delta*((X-1)^2+4). The two node
pairs have preimages (a,+-delta),(b,+-phi*delta), where a=phi-1,b=-phi.
In a rational parameter through the first branch, their values are

    phi-2, infinity, 3phi-6, 3phi.

Their paired cross-ratio is exactly

    c=-phi^(-4).

Mumford's split uniformization and the multiplicative period product, with
the adapted node-cycle marking, imply that the off-diagonal unit period q12
reduces to c or c^(-1). The product's other factors are1 modulo the local
maximal ideal. The source-to-marking dictionary, orientation, distinct branch
conditions and smoothing-parameter boundary are proved in NODAL_PERIOD.md.
The relevant published formula pages were inspected directly.

Full natural J^nu[7^d] rationality forces EVERY multiplicative period coordinate
to be a7^d power. This follows directly from the torsion exact sequence for
G_m^2/Lambda and Lambda intersect mu_(7^d)^2={1}. In particular q12 must be a
power; its residue then gives

    phi in (k_v^*)^(7^d).

Thus every beta-supporting place requires phi to be a seventh power, and at
DEPTH TWO it must be a FORTY-NINTH power. This requirement is geometric: the
old abstract local toric matrices did not specify this unit period.

## 3. The global unit coefficient is nonzero exactly on bad13

When13|C, natural inertia modulo7 is trivial and Q=169=1 mod7. If the
local natural class alpha vanished, the entire natural J^nu[7] would be
locally rational, forcing phi to be a seventh power. But in F169,

    phi^24=5+10phi !=1, 3^24=1, (sqrt5)^24=1.

The same global class restricts to a_phi times the nonzero phi class.
Therefore13|C implies a_phi!=0. The inherited actual good13 scalar-Frobenius
argument gives13 not dividing C implies a_phi=0. Consequently

    a_phi=0 if and only if13 does not divide C.

This determines vanishing, not the numerical coefficient. Since n>=2 already
forces13|C, the depth-two target has a_phi!=0.

On the good13 subcase, inert q=-1 mod7 has locally trivial natural alpha
because the remaining generators3 andsqrt5 are seventh powers. Such a prime
can divide C only if phi is also a seventh power. In particular97,293,587,1567
cannot divide C on that subcase. No depth-one nonexistence theorem follows.

## 4. Depth-two support narrows to four rational primes in the retained class

Let U={97,197,293,491,587,883,1373,1471,1567,1667}. Define H(C) to be the
COMPLETE set of variable rational divisors with h=v7(q^f_q-1)>=2.
Block58 gives H(C) subsetU =>n<=2,eta=1, allowing arbitrary additional low-h
prime divisors, of any size and multiplicity.

The new geometric test gives:

| Possible rational prime | phi a7th power? | phi a49th power? | beta support allowed by this test? |
|---|---|---|---|
|97,293,491,587,1471,1567|no|no|no, at any depth|
|197,883,1373,1667|yes|yes|not excluded|

Both split places are checked at491 and1471. At the remaining inert primes,
q=1 mod7 and phi^(q+1)=-1, so phi has order prime to7. Their positive results
are structurally expected. The test does not remove them.

If n=2 within this COMPLETE H(C) class, beta can ramify only above

    {197,883,1373,1667}.

At an actual supporting prime its multiplicity in C must still satisfy
v7(v_q(C))=1. No assumption removes this possibility.

In particular the genuine subcase theorem is

    H(C) subset {97,293,491,587,1471,1567} =>n=1.

For the four survivors, the natural Kummer rows in coordinates(phi,3,sqrt5)
are197:(0,6,6),883:(0,0,0),1373:(0,3,4),1667:(0,3,4). Hence support197 forces
r=a3/a5=6; support1373 or1667 forcesr=1. These two support types cannot occur
together. Support at883 alone remains compatible with every r!=0; the new
bad13 condition requires the normalized unit coefficient u=a_phi/a5!=0.
The four-row test plus this nonvanishing leave2304 coefficient directions,
not2304 representations or solutions.

## 5. The modulo49 condition is genuinely stronger, but still necessary only

At inert14503, phi is a seventh but not forty-ninth power. Both split places
at18229 have the same property. Such primes are excluded as depth-two beta
support by the new test, even though the residual period test passes.
The declared finite scan covered all high primes11<=q<=20000,108 prime ideals.
It is not a classification of arbitrary prime support.

The opposite direction fails as a proof route: passing this one period test
is not enough to split the full period lattice. Diagonal period coordinates
and their actual smoothing units remain untested. The197 local matrix model
passes the period residue condition; it is not eliminated or claimed realized.

## 6. An attempted abstract higher-Kummer shortcut failed

The actual natural extension modulo49 may include new coefficients7d[pi_v]
at variable places where only its modulo7 reduction was unramified. Omitting
these classes would impose an unjustified ramification restriction.

Using twelve classes supported at the already-forced primes and fixed units,
the transpose local residue evaluation matrix has rank12, with determinant

    -237892440 =5 modulo7.

Thus freely varying those abstract correction coefficients can cancel every
prescribed unramified local error at the twelve U places, keeping the residual alpha
unchanged. This cannot by itself yield a contradiction. It does not realize
those coefficients in the actual natural representation or preserve every
fixed-prime local value. The new marked period supplies a distinct geometric
restriction that this enlarged abstract lift model lacks.

## 7. Verification and provenance

The original Block58 replay passed with its selected nested predecessor chain.
The new exact programs check:

| Check | Coverage |
|---|---:|
|Same-lattice toric algebra instances|5760|
|Instances with nonrational coefficients|5730|
|Depth-two instances|192|
|Marked conic/cross-ratio residue fields at all primes11<=q<=2000|445|
|High-prime residue fields in the complete declared scan through20000|108|
|Named U residue fields|12|
|Direct inherited residue-symbol checks in independent code|180|
|Additional bad13 power symbols|3|
|Normalized F49 natural coefficient directions|2352|
|Coordinate-basis preimages for the abstract Kummer correction map|12|

The independent finite-field program uses a sqrt5 basis, secant/tangent
coordinates from the conic, left-to-right exponentiation, a sieve and a
subset-expansion determinant. It imports no primary arithmetic module. The
primary uses a phi basis, right-to-left powers, trial primality and Bareiss
elimination. Both implementations agree on all declared finite assertions.
The local algebra grid is not called an independent second mathematical proof.
No new point counts are performed.

The release verifier regenerates all new outputs in a scratch copy, compares
complete JSONs, verifies16 named inherited source hashes and the derived
reciprocity cache, and rejects deliberately altered period and residue data.
The final fresh-extracted replay and archive checks are recorded separately.
The entire original Block58 archive is preserved unchanged.

The initial session-based execution launch failed before starting; its
replacement and startup replay completed. Broad searches returned irrelevant
results that were discarded. A draft prose residue for the determinant was
corrected from2 to5; the exact integer and computations were unchanged.
The failed mathematical shortcuts and local controls remain in the archive.
No new Lean compilation or independent mathematical review was performed.

## 8. Remaining objective

The immediate target is now the OTHER actual period coordinates, or a proven
comparison tying the natural modulo49 Kummer class to the opposite endpoint
at197,883,1373,1667. The special role of883 is explicit: the present natural
residue rows impose no ratio restriction there, and its off-diagonal period
has prime-to7 order. A new argument must use genuinely additional data.
General depth1, the remaining depth2 cases, unrestricted high support,
independent upstream proof audit, CM nonboundary points, higher Hilbert levels,
the complete signature and full Beal remain open obligations.
