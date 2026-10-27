# Beal research — Block64
## Common-polynomial Frobenius compatibility and a complete conductor exclusion

Version6.4.0. 20 September2026.

The two Block63 tuples with alpha=(+/-3w,4,1) and beta support113/617/883 are now
excluded by the ACTUAL Frobenius at281, considering both good and bad reduction.
The stronger bounded theorem excludes every depth-one opposite extension with
complete ramification in

    W64={43,113,127,197,337,463,547,617,883,953,1373,1667}.

A second advance requires the two products at split primes to belong to one
Frobenius polynomial of the same actual reduction, rather than selecting roots
independently from different curves. With743 added, however, two necessary-system
tuples remain, now supported at547/743. They are preserved, not claimed solutions.

All arithmetic conclusions remain conditional on TARGET_CONTRACT.md's explicit
inherited Frey, Kummer, lattice, cohomology and class-group hypotheses. No new
Lean compilation or independent mathematical review is claimed. This does not
complete the reducible branch, the full signature, or Beal.

## 1. The actual281 test closes the previous two tuples

The complete necessary good locus has11240 parameter pairs. Exact counts leave
80 pairs with the required full residual Frobenius polynomial. Their two
actual twisted polynomials are

    T^4-25T^3+657T^2-7025T+78961,
    T^4+17T^3+573T^2+4777T+78961.

Each represents40 admissible pairs. Their possible rank2 trace corrections,
with w^2=5 in the COEFFICIENT residue field, are

    G281={3w,-3w,4+3w,4-3w}.

The new cyclotomic generator pi281=-2-2zeta-zeta^2-2zeta^3+zeta^5 has norm281.
Its compatible primitive residue root is59. The two natural Kummer rows at281
are(1,3,6),(6,3,6). The correctly twisted opposite row on113,617,883 is(3,4,1).
The old inertia vector(6,5,3) therefore gives beta281=6. Its products with the
two natural values are3+4w and3-4w, neither in G281 and neither zero.

Good281 requires membership in G281. Bad281 requires product0 by the exact
toric trace. Both fail. No assumption that281 must be good is inserted, and
no general theorem that281 divides C is asserted. See notes/PRIME281.md.

## 2. The full expanded conductor also fails

The extra617 and953 columns are both included in every Frobenius evaluation.
All conductor primes are inert in K and1 mod7, so the inherited descent of
beta AS A chi^-1 COHOMOLOGY CLASS applies. The global natural class is
normalized once as(u,r,1), with u,r nonzero. Natural local-zero conditions
reduce r to six possible F7 ratios, without asserting general coefficient descent.

The forced71 condition and the nonzero-unit argument at29 give two justified
linear rows. They leave345600 coefficient/character pairs. The old tests
at491,43 where unramified,211,239 leave16 tuples: fourteen in the new953 branch
and the two617 tuples. The281 test rejects every one. The sixteen intermediate
candidates remain in the certificate.

The primary affine solver and the independent Cramer-kernel/bitset solver
agree on all stages and complete tuple lists. At the allowed ramified43 branch,
the43 Frobenius test is OMITTED, not improperly applied. Additional C divisors
unramified in beta are unrestricted. See notes/CONDUCTOR_EXCLUSION.md.

## 3. A stricter comparison of the SAME split reduction

Conjugation gives delta'=6+3phi=phi^2(9-3phi). Thus the two twisted reductions
at a split rational prime, for the same rational(A,B), are isomorphic. Their
full quartic polynomials agree. If the two predicted products are p_plus and
p_minus, good reduction therefore requires ONE actual polynomial whose rank2
correction set contains both products.

The old union-of-all-corrections test allowed one product from a polynomial
at one residue pair and the other from a different polynomial. That weaker
system was a safe overapproximation for exclusions, but retained avoidable
false possibilities. The new criterion removes them without assuming a
semilinear global Tate-lattice comparison.

For a descended opposite class with common value b and natural rows(l,c,d),
(-l,c,d), the products are b(c*r+d+/-l*u). If l,u,b are nonzero, the necessary
coefficient-conjugacy relation is equivalent to

    b(c*r+d) in F7,                     (b*u)^7=-b*u.

This is a conductor-independent local lemma under the stated descent and good,
unramified test hypotheses. It does not force u itself into a prescribed line
without additional control of b. See notes/COMMON_POLYNOMIAL.md.

## 4. The stronger method still has genuine survivors

For complete allowed conductor W64 union{743}, independent choices leave6 tuples.
The common-polynomial test removes4 mixed-polynomial tuples but retains exactly

    alpha=(w,6,1) or(-w,6,1),        (s547,s743)=(5,1).

All other inertia coordinates vanish. Their opposite values at
(71,29,491,43,211,239,281) are(0,0,1,3,3,4,0), with the factor2 included when
passing the43 value to K. These two tuples satisfy the declared stronger
necessary system. They are NOT globally realized Frey representations, integer
solutions, or a proof of compatibility with every actual period unit or fixed
prime condition. The local positive Frey families from earlier blocks remain valid.

At13, the new forced local-zero condition is already automatic after the
stipulated descent: gamma(Frob13^2)=(1-1)gamma(Frob13)=0. Treating it as a new
independent equation would overstate progress. This failed route and the743
survivors are documented in notes/SURVIVORS_AND_13.md.

## 5. Arithmetic scope

Let U be the retained ten-prime set, and V64=U union{43,113,127,337,463,547,617,953}.
Every actual depth-one beta must now ramify outside V64. Under COMPLETE H(C)
subset U, the inherited n1 conclusion still holds, so that outside support
must have h1, multiplicity prime to7, and the actual phi and75A seventh-power
conditions. Unbounded outside low-congruence support remains open.

There is also the enlarged all-depth statement: if the COMPLETE geometrically
eligible divisor set E(C) lies in V64, no retained reducible representation
exists. Its proof uses the new n1 theorem and the explicitly inherited
higher-depth/highest-layer exclusions. It is NOT a bound on arbitrary E(C)
or a proof of the entire H(C) subset U class. See notes/ARITHMETIC_CONSEQUENCES.md.

## 6. Verification and provenance

The original Block63 verifier and its declared nested chain passed before
editing, in128.654021799 seconds. Its ZIP is retained byte for byte.

|New check|Exact declared coverage|
|---|---:|
|Good281 equation pairs|11240 in both implementations|
|Degree-one / degree-two curve-class counts|285 /41 in each implementation|
|Independent smoothness gcds|11240|
|Residual good281 pairs|80, in two curve orbits|
|Complete expanded conductor pairs after two rows|345600 in both implementations|
|Larger743 conductor pairs covered|5877504 per solver mode|
|Direct independent twisted residue symbols|540|
|Independent integral cyclotomic norms|7|
|Paired-product coefficient triples|117649|

The independent counter uses a different field basis, explicit square-root
multiplicities and a different curve canonicalization. The independent character
checker uses inverse cyclotomic roots, direct seventh-power symbols, a different
coefficient field, and Cramer kernels. Neither imports primary arithmetic code.
The algebra identities have one executable check plus their written proof.

Production uses Python's standard library. New expected JSON outputs are
regenerated in scratch and compared in full. Negative controls reject altered
counts, a changed281 row, an invented survivor, a false common-polynomial pair,
and modified payload content. All payload hashes and13 named inherited source
hashes are checked. Final extracted-ZIP replay, timing and integrity results
are recorded externally, avoiding self-referential checksum assertions.

One initial session-based launch failed before process creation; the standard
subprocess replay passed. A source-path typo was corrected before arithmetic.
No timeout was used as a mathematical exclusion. Source pages were successfully
opened and rendered. No new Lean compilation or independent proof review occurred.

## 7. Next target

The old617 tuples and W64 are no longer open cases. The concrete surviving
tuples now have natural vector(+/-w,6,1) and beta support547/743. An actual
constraint must be added to exclude them, or a support-uniform argument must
address further conductors. Additional ramification can change every Frobenius
value and cannot be silently omitted. The whole reducible branch, arbitrary
depths and supports, CM/higher Hilbert levels, full signature and full Beal
remain separate obligations.
