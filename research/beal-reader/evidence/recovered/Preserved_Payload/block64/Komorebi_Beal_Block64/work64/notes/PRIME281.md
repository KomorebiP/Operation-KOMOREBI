# B64.1–B64.2. The actual prime281 Frobenius excludes the two617 tuples

## Complete good-reduction locus

281 is prime, splits in K, and is1 mod7. Its two phi residues are38 and244.
The twist delta=9-3phi is nonsquare at both. Every primitive integer solution
with281 not dividing C supplies a residue pair(a,b) for which a^3+b^5 is a
NONZERO seventh power. There are11240 such pairs. Every pair is independently
checked for smoothness. Values a=0 or b=0 are not silently omitted.

The primary counts complete untwisted curves, including both points at infinity,
over F281 and F281^2, using quadratic characters. It partitions the finite
locus using transformations(a,b)->(a*t^5,b*t^3), but tests seventh-power
admissibility for EACH orbit member. This matters because the sum scales by
 t^15, which need not itself be a seventh power. There are285 degree-one
counts and41 degree-two counts. Degree-two counts are omitted only after the
necessary rational trace condition modulo7 has already failed, and are marked
null. No claim of11240 direct degree-two counts is made.

The independent counter uses theta^2=theta-d rather than the primary square-root
basis, explicit square-root multiplicities rather than norm characters, and a
discrete-log canonicalizer rather than the same orbit representatives. It
regenerates the entire eligible pair set and11240 smoothness gcds, checking
every member assignment and both computed counts for each needed class.

If N1,N2 are the complete untwisted counts, let s=282-N1 and
b2=(s^2-281^2-1+N2)/2. The untwisted polynomial is

    T^4-s*T^3+b2*T^2-281*s*T+281^2.

Twisting negates its roots. The full residual target is
(T-1)^2(T-281)^2 modulo7. EXACTLY80 admissible pairs survive, in two
counted curve orbits:

| representative | N1 | N2 | admissible members | twisted polynomial |
|---|---:|---:|---:|---|
|(9,37)|307|79651|40|T^4-25T^3+657T^2-7025T+78961|
|(26,11)|265|79819|40|T^4+17T^3+573T^2+4777T+78961|

For P=T^4-S*T^3+C2*T^2-Q*S*T+Q^2, the two rank2 traces have sumS and normC2-2Q.
Both displayed discriminants S^2-4(C2-2Q) equal245=5*7^2. Thus the possible
actual corrections (tau-282)/7 modulo7 are precisely

    G281={3w,-3w,4+3w,4-3w}.

More precisely the first polynomial gives the pair{3w,-3w}, and the second
gives{4+3w,4-3w}. The independent program recovers these by enumerating all49
coefficient-field elements with the computed trace and norm, not by the
primary discriminant-square-root extraction.

## Correctly twisted Frobenius value of the old survivor

An integral generator of a prime of Q(zeta7) above281 is

    pi281=-2-2zeta-zeta^2-2zeta^3+zeta^5.

Its exact norm is281, and its unique primitive seventh root zero modulo281 is59.
Norms are checked independently by a six-conjugate cyclic group-ring product.
Use that root for the natural Kummer symbols, giving

    phi=38:  (1,3,6),
    phi=244: (6,3,6)

in coordinates(phi,3,sqrt5). At a conductor prime q the least primitive root
 g_q determines r_q=g_q^((q-1)/7). The opposite chi^-1 Frobenius row is

    R281,q=-sum_(b=1)^6 b*log_gq(pi281(r_q^b)) mod7.

The coefficients b are essential. They encode the retained chi^-1 prime/character
covariance and are not the ordinary ray-character weights. On113,617,883 the
row is(3,4,1). The old inertia vector(6,5,3) gives beta281=6.

For alpha=(+/-3w,4,1), the two natural values are4+/-3w. Their products with
beta281 are3+/-4w. These have scalar part3, whereas G281 has scalar part0 or4.
Neither product is zero.

If281 is good, actual Frobenius requires both products in G281, impossible.
If281 is bad, the exact toric trace requires product0, also impossible.
The test is unramified for beta because281 is outside its stipulated conductor.
No hypothesis that281 must be good or bad is inserted. This excludes the
specific two113/617/883 tuples with arbitrary other C divisors unramified in beta.
It does not prove281 divides C in an unrestricted representation.

All finite-to-arithmetic arrows remain conditional on TARGET_CONTRACT.md.
