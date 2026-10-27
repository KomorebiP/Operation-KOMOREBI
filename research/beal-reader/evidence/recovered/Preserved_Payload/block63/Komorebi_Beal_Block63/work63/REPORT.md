# Beal research — Block 63
## Torsion exponent at83, nonzero unit coefficient, and enlarged conductor exclusion

Version6.3.0. 20 September2026.

The main new result is independent of the actual depth and the ramification
support:

    a_phi !=0,                         13 divides C.

It closes the good13 subcase of the retained reducible branch. The proof uses
the actual natural Jacobian at83, including a finite group-exponent computation
that cannot be replaced by Frobenius polynomial or order divisibility alone.

All arithmetic applications are conditional on the explicit inherited Frey
geometry, natural-lattice/Kummer and other named hypotheses. This does not
solve the complete reducible branch, the(3,5,7) signature, or Beal. These are
written proofs with exact finite certificates. No new Lean compilation or
independent mathematical review is claimed.

## 1. A local obstruction valid with unrestricted global support

At the inert prime83, the local residue norm is6889=1 mod7. The fixed rational
Kummer generators3 andsqrt5 are seventh-power residues, but phi is not:

    phi^984=76+29phi !=1,          3^984=(sqrt5)^984=1.

Thus a_phi=0 would make the natural residual representation locally trivial,
and all of J^nu[7] locally rational.

If83 divides C, the inherited actual period obstruction immediately rules
that out. If83 does not divide C, rational prime-to83 torsion injects into the
good finite Jacobian. The new computation proves that EVERY possible good
Frey reduction at83 also fails full rational7-torsion. Both cases contradict
a_phi=0. The retained good13 theorem then forces13 into C.

Neither reduction type at83 was assumed. The result does not say83 divides C.
It does not determine the nonzero numerical value of a_phi or identify the
base-field radical with a coefficient-field radical.

## 2. The exceptional finite Jacobian: order divisibility is not enough

All6806 admissible good pairs modulo83 were counted. The primary reduces them
to83 curve orbits. The independent implementation counts BOTH extension
degrees directly at every pair and checks every smoothness gcd.

Full rational7-torsion would require2401 to divide the Jacobian order. Only82
pairs pass this condition, forming one isomorphism orbit represented by(A,B)=(1,30).
Its rational untwisted Frobenius polynomial is T^4+128T^2+6889. After the inert
base extension and actual negative twist the polynomial is

    (T^2-128T+6889)^2,

and the group order is

    45,724,644 = 7^4 * 19044.

This is a genuine survivor of the order test. We then changed to an isomorphic
odd-degree model using the rational root5 and computed in its divisor class
group. An explicitly displayed rational divisor E satisfies

    [7]E !=0,                        [49]E=0.

Therefore the group has an element of exact order49. Its7-primary subgroup
has size7^4, so it cannot simultaneously contain ALL7^4 geometric7-torsion
points: those alone would fill that subgroup with elements killed by7.

This last step excludes the exceptional orbit. The full77-operation divisor
transcript and reduced representatives are supplied. A separate implementation
uses a different finite-field basis, CRT/Hensel interpolation rather than the
primary extended-gcd composition, and a different scalar ladder. It independently
reproduces the order49 witness and each transcript operation. No full group
decomposition is asserted. See notes/FINITE_TORSION_83.md and UNIT_COEFFICIENT.md.

## 3. The new unit restriction closes an enlarged depth-one conductor

Let

    W={43,113,127,197,337,463,547,883,1373,1667}.

At n1, all beta ramification cannot be confined to W. The new primes337,463,547
are low-congruence primes outside the previously excluded Splus. Their actual
chi^-1 twisted columns are included. Additional divisors of C that do not
ramify in beta are allowed.

Without a_phi!=0, the enlarged necessary system has THREE survivors. They all
have normalized alpha=(0,6,1). Thus the new local theorem, not repetition of
the old finite tests, supplies the decisive missing restriction.

With u=a_phi/a5 nonzero, the two natural29 values differ. The inherited unique
good trace correction2 forces the common descended beta29 to be zero. Together
with the justified beta71-zero condition, this leaves119808 coefficient/vector
pairs. The remaining actual good/bad tests at491,43,211,239 exclude every pair.
The ramified43 branch does not use an unramified43 test. Full stage counts and
all columns are in notes/CONDUCTOR_EXTENSION.md and verification/conductor.json.

The independent program uses another coefficient-field basis, direct seventh
symbols, exact cyclotomic norm products and explicit Cramer kernel enumeration.
It verifies all390 residue evaluations and agrees on complete survivor tuples,
not just the conclusion zero.

## 4. A larger conductor genuinely survives these tests

Adding617 produces TWO surviving necessary tuples:

    alpha=(+/-3w,4,1),     w^2=5 in the coefficient field,
    (s113,s463,s617,s883)=(6,0,5,3).

Their nonzero inertia support is113,617,883. They satisfy the nonzero unit
condition and every trace test used in this block. They are NOT asserted Frey
representations or integer solutions. These controls show exactly why the W
conductor theorem cannot be silently extended to arbitrary outside primes.

The old local49-torsion Frey families at197,883,1373,1667 remain valid. They do
not provide a single global natural Kummer vector and compatible opposite
extension, so the new global coefficient theorem does not invalidate them.

## 5. Scope of the arithmetic consequences

For every retained reducible representation,13 now divides C. With fully
trivial eta, beta is also fully locally zero at13, including at depths1 and2.
For the descended all-inert conductor class this latter value was already zero;
it is not counted as a new independent row in the enlarged sieve.

With U={97,197,293,491,587,883,1373,1471,1567,1667}, depth1 beta must ramify
outside U union{43,113,127,337,463,547}. The former COMPLETE H(C) subset U class
still has only depth1, but possible low-congruence beta support outside that
larger set remains unbounded. That entire class is not eliminated.

If the COMPLETE set E(C) of geometrically eligible divisors is contained in
U union{43,113,127,337,463,547}, the retained reducible branch is excluded at
any depth, by combining this block with the inherited higher-depth bounds.
No theorem bounds arbitrary E(C) to this finite set.

## 6. Verification and provenance

|New check|Exact coverage|
|---|---:|
|Admissible good pairs at83|6806|
|Primary degree1 / degree2 counts|83 /83|
|Independent direct degree1 / degree2 counts|6806 /6806|
|Independent smoothness checks|6806|
|Exact divisor transcript operations independently replayed|77|
|All nonzero F6889 field inverses|6888|
|Independent strict-W coefficient/vector pairs|119808|
|Independent direct twisted seventh-power evaluations|390|
|Independent cyclotomic norms|6|

Separate control enumerations retain all three u=0 W survivors and both617
survivors. The production programs require only Python's standard library.
Final verification reruns all five new result files in a clean scratch copy,
compares full JSON data, tests malformed certificates and checks the exact
predecessor bytes and named nested source hashes. The final extracted-ZIP run
and archive audit are external records, not self-referential payload claims.

The first predecessor replay was contaminated by our exploratory bytecode
writes and failed its corruption-test expectation, despite matching its
mathematical outputs. A clean extraction with bytecode writes disabled passed.
Both execution records are preserved. An attempted direct retrieval of Cantor's
original paper returned403; the exact algorithm statements were instead checked
in Galbraith's author-hosted corrected book. No failed retrieval or run is
counted as a proof. See DEVELOPMENT_FAILURES.md for the complete record.

## 7. What remains

Good13 is closed under the retained assumptions. Bad13 with nonzero unit
coefficient remains. The next concrete targets are the two113/617/883 tuples,
or a genuinely support-uniform relation using the newly forced13 local data.
An additional ramified prime changes all Frobenius values and cannot be omitted.

General depth1, general depth2 and higher support, independent upstream proof
review, CM nonboundary points, higher Hilbert levels, the complete signature
and full Beal remain separate obligations.

### Final-wrapper correction

The first extracted full replay also exposed a status-parser mismatch: Block62
returned code0 and PASS_DECLARED_CHECKS, but the new wrapper accepted only PASS.
The mathematical jobs had succeeded. The exact status check was corrected,
the failed report and draft-archive hash preserved, and the package rebuilt
for a fresh full replay. The final external execution record governs acceptance.
