# Beal research — Block 65
## Coefficient rigidity and an actual Frobenius obstruction

Version6.5.0. 20 September2026.

The two retained depth-one547/743 configurations are now excluded. A second,
conductor-independent argument proves normalized coefficient rigidity whenever
the actual opposite class descends to Q: alpha=(v*w,r,1), with v,r in F7^*, and
beta has an F7-valued representative. This reduces the natural coefficient
possibilities from2304 to36 without a finite conductor hypothesis.

All conclusions retain the explicit actual-model and representation hypotheses
in TARGET_CONTRACT.md. The complete reducible branch of A^3+B^5=C^7 is NOT solved.
There is no new Lean compilation, independent mathematical review, or novelty claim.

## 1. A uniform coefficient theorem in the descended depth-one regime

Normalize a5=1 and write alpha=u[phi]+r[3]+[sqrt5]. The inherited unit theorem
makes u and r nonzero. Suppose beta descends as a chi^-1 cohomology class to Q.
No assumption on its conductor size or support is added. Then

    u^7=-u,       r in F7^*,       beta represented over F7.

The mechanism has three distinct parts.

First, the Kummer classes of phi,3,sqrt5 are independent over L=K(zeta7).
Second, their chi-isotypic image and beta's chi^-1 image are independent in the
ACTUAL finite joint Galois quotient. Explicit eigenspace projection proves
that product statement. This is not a choice of unrelated local characters.
Third, Chebotarev realizes each joint vector at good rational primes split in L.
The identical quartics at the two K-places make distinct trace products
coefficient-conjugate. Two joint probes force beta's image into F7, u into the
trace-zero line, and r into F7.

Consequently alpha=(v*w,r,1), v,r in F7^*. This is actual normalized
cohomological coefficient rigidity, not merely a smaller sufficient test
family. It does NOT descend a Tate lattice or identify the base radical with w.
It is stated only at n1 and only when beta's cohomology descent is available.
See notes/COEFFICIENT_RIGIDITY.md for the full argument and source translations.

## 2. Prime379 excludes the two old tuples

The old configurations are alpha=(+/-w,6,1), with beta inertia(5,1) at547,743.
New complete counts at379 give20466 admissible good equation pairs. Of these,
432 meet the full residual Frobenius condition, in eight curve orbits. Their
possible rank-two trace corrections are

    G379={2,4,+/-w,+/-3w,1+/-2w,4+/-2w,2+/-3w,6+/-3w}.

The exact generator

    pi379=-2-2zeta-zeta^2+zeta^3-2zeta^4-2zeta^5

has norm379 and primitive residue root195. It gives natural rows(5,1,4),(2,1,4)
and twisted beta row(2,5) on547,743. The old inertia vector therefore gives
beta379=1 and the two required products3+/-2w.

Neither product is in G379 and neither is zero. Good379 requires membership
in G379; bad379 requires product zero. Thus both reduction cases fail. No
assumption that379 is good or that all arbitrary C must contain379 is made.
This closure also follows directly from the frozen full-F49 two-survivor
list, independently of accepting the new coefficient-rigidity theorem.

Both point-count implementations cover381 degree-one curve classes and41
degree-two classes. The independent algorithm checks all20466 smoothness gcds
and every curve-orbit assignment. Degree-two values not needed after a failed
degree-one trace condition are explicitly null. No point count at any other
new prime is promoted to a theorem. See notes/PRIME379.md.

## 3. A complete21-prime conductor class is excluded

Let P2000 contain every rational prime q between11 and2000 that is inert in K
and1 modulo7. It has25 primes. Put

    W65=P2000 minus {673,1163,1723,1933}
       ={43,113,127,197,337,463,547,617,743,757,827,883,953,967,
         1093,1303,1373,1583,1597,1667,1877}.

No actual depth-one beta has all its ramification in W65. Arbitrary additional
prime divisors of C UNRAMIFIED in beta are permitted.

All conductor columns are explicitly recomputed with their chi^-1 weights.
The new coefficient theorem reduces the exact solver to six nonzero trace-zero
u-values, six possible r-values and F7 inertia coordinates. After the justified
71 and29 rows there are4392 coefficient/character pairs. The old tests leave
eight tuples before379, and the new379 test rejects all eight.

The primary affine solver and independent Cramer-kernel solver agree on each
stage and complete survivor list. The latter enumerates732 nonzero inertia
vectors and tests all six u-values. Six of the21 named allowed primes already
have no permitted nonzero Kummer ratio; this is recorded rather than presented
as21 entirely new independent exclusions.

As a conditional corollary, if the FULL geometrically eligible divisor set
E(C) lies in U union W65, there is no retained reducible representation at any
depth. This uses the explicit inherited highest-layer and full-eta higher-depth
exclusions. It is not a bound on arbitrary E(C) or a solution of Beal.
See notes/CONDUCTOR_EXCLUSION.md and ARITHMETIC_CONSEQUENCES.md.

## 4. The full25-prime system still has112 survivors

The attempted extension to all of P2000 does not give zero. It leaves112 exact
necessary-system tuples,38 at ratio4 and74 at ratio6. A smaller17-prime
expansion already has ten survivors.

One concrete survivor is

    alpha=(w,6,1),
    (s197,s337,s547,s673,s883)=(2,4,5,2,2),

with all other inertia values zero. Its beta values at rational tests
71,29,491,43,211,239,281,379 are0,0,0,1,0,5,0,0. At43 the K-value has the
required factor two. The zero value at379 permits bad379, so the old two-tuple
contradiction does not eliminate it.

These tuples satisfy only the stated necessary system. No actual global Frey
representation, simultaneous smoothing-unit data, or integer solution is
constructed. The four older local positive Frey families remain valid.

Within a stipulated COMPLETE conductor inside P2000, actual ramification must
occur at one of673,1163,1723,1933. Once arbitrary further primes are permitted,
their columns can change all Frobenius values. No universal zero is claimed.

## 5. Verification and provenance

The original Block64 archive passed its clean selected-chain replay in
148.667886309 seconds before editing. It is preserved byte for byte.

|New exact check|Coverage|
|---|---:|
|Good379 parameter pairs|20466 in both count implementations|
|Degree-one / degree-two curve-class counts|381 /41 in each implementation|
|Independent smoothness gcds|20466|
|Complete nonzero coefficient triples in the algebra check|110592 in each implementation|
|Two-probe survivors|216, exactly the proved coefficient form|
|Further complete coordinate tests on those triples|74088 in each implementation|
|Exact eigenspace-projection vector tests|16807 in each implementation|
|W65 coefficient/character pairs after two rows|4392|
|Full25-prime coefficient/character pairs after two rows|201960|
|Independent direct twisted seventh-power symbols|1194|
|Independently checked integral cyclotomic norms|8|

The secondary implementations import no primary arithmetic. Their field bases,
point-count tables, curve canonicalizations, residue symbols and finite solvers
are distinct. They do not constitute independent mathematical proof review.

verify.py regenerates all six new outputs in a scratch copy and compares full
JSON records. It audits exact payload members and hashes,13 immediate named
inherited source files, the merged fixture provenance, and the original archive.
Deliberately altered counts, residue rows, trace-pair data, candidate totals,
coefficient data and package contents must be rejected. With the explicit flag,
the frozen Block64 verifier and its declared nested chain are run again.

Final archive checks, observed elapsed time and fresh-extraction replay are
recorded externally, avoiding circular manifest claims. No timeout is treated
as a mathematical exclusion. All analytical geometric inputs remain conditional.

## Next obligation

The old547/743 configurations and the complete W65 conductor are closed. The
new coefficient theorem applies to arbitrarily large descended n1 conductors,
but it does not make beta vanish. The112 retained tuples, or a genuinely new
support-uniform actual representation constraint, are the next targets.
General non-descended depth one, general depth two/higher support, CM and
higher Hilbert levels, full signature and Beal remain unresolved.
