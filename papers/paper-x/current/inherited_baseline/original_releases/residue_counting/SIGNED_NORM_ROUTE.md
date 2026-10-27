# Signed norm, sign partition, and actual generator sums

All five modules below have passed strict Lean compilation and are frozen.
Together they contain 28 theorem declarations and two definitions. Source and
object hashes are in `privatechecks/signed_norm_final_verification.json`.

| Module | Theorems | Definitions | Compiler result |
|---|---:|---:|---|
| NormSignFormula | 5 | 0 | Local attempt 3, exit 0 |
| NormSignArithmetic | 6 | 0 | Local attempt 3, exit 0 |
| NormSignDilation | 7 | 0 | Root coordinator_b, exit 0 |
| NormSignPartition | 7 | 1 | Local attempt 2, exit 0 |
| NormResidueGeneratorSum | 3 | 1 | Local attempt 1, exit 0 |

## Arithmetic sign

For every number field K and x in K, `NormSignFormula.lean` proves

    cast_R(norm_Q(x)) = product_real sigma(x) * product_complex |sigma(x)|^2.

The complex product is strictly positive when x is nonzero. The proof groups
all embeddings into complex-conjugation fibers. A real place contributes its
single real embedding. A nonreal place contributes a conjugate pair, whose
product is the squared complex norm. The source retains Xavier Roblot's Apache
2.0 notice for the adapted Mathlib fiber argument.

`NormSignArithmetic.lean` identifies strict positivity and strict negativity of
the rational field norm with those of `NormSignGeometry.realProduct`. Mathlib's
integral/rational norm comparison then gives the same equivalences for the
actual norm on the ring of integers. Membership in the actual positive or
negative unit cone forces the corresponding strict integral norm sign;
nonvanishing is derived from cone membership.

The nonzero hypotheses on the general sign equivalences are necessary: in a
totally imaginary field the real-coordinate product is the empty product 1,
whereas the field norm of zero is zero.

`NormSignDilation.lean` transports those sign conclusions through every positive
real dilation and the actual Euclidean mixed-space coordinates. It proves the
real-product scaling formula, derives nonvanishing from the dilated cone, and
identifies the integral norm sign for actual counted algebraic integers.

## Exact point and weight attachment

`NormSignPartition.lean` proves that the two Euclidean sign regions are a
disjoint union of the ordinary unit cone. For every positive dilation it builds
an explicit equivalence from all actual lattice points to the sum of the
positive and negative point types. Its inverse preserves the underlying
lattice points. The corresponding exact sum decomposition holds for any
complex weight on the lattice. Boundedness and discreteness supply finite
point types; no finite point list or selected enumeration is assumed.

`NormResidueGeneratorSum.lean` proves that each computed residue weight equals
the absolute principal norm weight of the unique algebraic integer underlying
the lattice point. It identifies each sign-restricted residue sum with its
actual point sum, then recombines the two into

    normWeightedCount = finsum over actual cone lattice points x of
      chi(absNorm(span{integerRepresentative(x)}) modulo m).

The final theorem is `NormResidueLattice.normWeightedCount_eq_generatorPointSum`.
It holds for an arbitrary function chi on ZMod m and every positive real
dilation. The modulus-subideal and finite residue-domain inputs remain explicit.
There is no zero-mean assumption in this exact identity and no roots-of-unity
multiplicity is suppressed. Torsion attachment and character cancellation are
handled by separate modules.

In particular, absolute norms and signed norms are never silently identified
modulo m. The positive portion uses the signed norm polynomial, and the negative
portion uses its negative; the signs are derived from the actual embeddings.

## Verification history

Formula attempt 1 failed because a rewrite replaced the place on both sides of
the fiber equation. Restricting the rewrite to the left side fixed it. Attempt
2 incorrectly applied a generic map-ne-zero lemma; ring-hom injectivity fixed
it. Formula attempt 3 passed strictly.

Arithmetic attempt 1 used an unavailable negative-product lemma and triggered
two strict simplification warnings. Attempt 2 needed the realProduct definition
unfolded before its inequality tactic could recognize the same product. Both
issues were corrected in attempt 3, which passed strictly.

Partition attempt 1 reached all declarations but failed on two omitted explicit
set/point arguments in the inverse-scalar membership lemma and on three strict
style warnings for local Fintype instances. The arguments were supplied and
`letI` was replaced by `let`; attempt 2 passed strictly. GeneratorSum passed on
its first attempt.

The local axiom query for Formula and Arithmetic completed successfully (exit
0), listing only propext, Classical.choice, and Quot.sound on all 11 declarations.
During runtime contention the root requested cancellation, but the process had
already exited before cancellation was attempted; no process was terminated.
This race is recorded in `privatechecks/norm_sign_axioms_cancellation_race.json`.
No additional local axiom jobs were started. The independent release audit
covers all five modules and is recorded separately.
