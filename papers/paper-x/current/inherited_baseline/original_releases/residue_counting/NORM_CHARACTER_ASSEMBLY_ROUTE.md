# Actual norm-character count: completed proof route

Target declaration:

`PaperX.NormResidueLattice.exists_classNormSum_bound_of_unit`

Location: `lean/PaperX/NormResidueCharacterCounting.lean`.

## Exact input and conclusion

The theorem takes a number field K of degree d, an ordinary ideal class C, a nonzero integral ideal J with [J]=C⁻¹, a positive integer m, a map χ:ZMod(m)→ℂ preserving multiplication, 0, and 1, an actual unit u in O_K/mO_K with χ(N̄(u))≠1, and χ(N(J))≠0. It derives a constant B≥0 such that the actual sum of χ(N(I) mod m) over nonzero integral ideals I with [I]=C and N(I)≤X has norm at most B X^(1−1/d), for every X≥1.

No quantitative counting hypothesis remains. There is no assumption that the map J/mJ→O_K/mO_K is surjective, and no supplied finite-mean assumption. The explicit arithmetic witness and representative conditions remain premises.

## Checked composition

1. `NormSignGeometry` and `NormSignResidueCounting` restrict the actual fundamental-cone atlas to both norm signs and give uniform counts on the actual ideal quotient.
2. `NormResidueLatticeMap` descends the unique represented integer to the actual residue ring and applies its determinant norm. It asserts no density on an arbitrary codomain.
3. `NormResidueWeightedCounting` and `NormResidueUnitCounting` obtain both zero means from the actual quotient-unit permutation, then bound the recombined signed count.
4. `NormSignPartition` and `NormResidueGeneratorSum` prove that recombination is exactly one finite sum over actual cone points, weighted by absolute principal-ideal norms.
5. `NormResidueGeneratorAttachment` uses an explicit equivalence with bounded generators. Casting the two natural-number norms to the reals proves they agree with the same mixed norm, so every norm weight is preserved.
6. `NormResidueCharacterCounting` changes the positive dilation to the generator norm threshold Y via t=Y^(1/d).
7. `IdealNormWeightedAttachment` retains the exact roots-of-unity factor and χ(N(J)). `IdealNormCharacterBound` transfers the derived generator estimate to the actual ideal sum using χ(N(J))≠0.

Both sign portions are recombined before the full torsion factor. The exponent argument uses 1−1/d≥0 and remains valid for degree one. Constants need not be uniform over K, J, m, or χ.

## Verification

The final author check is `privatechecks/character_assembly_b_NormResidueCharacterCounting.json`: strict compiler exit code 0. Its initial attempt required activation of the already-derived finite quotient enumeration in an intermediate identity. That correction changes no arithmetic or counting hypothesis.

The complete new block has 34 modules and 156 theorem/lemma declarations, plus definitions, abbreviations, and instances. The manifest lists 211 explicitly named declarations. The independent audit and final source/object hashes are recorded separately in `verification.json` and the retained audit records. All 221 predecessor source/object pairs are frozen.

## Remaining arithmetic work

The final theorem does not prove its residue-unit witness for every intended character, select a suitable inverse-class representative for every application, treat all characters without a witness by arithmetic descent, prove measurability of this norm-character sum and attach it to the Mellin framework, establish the actual Euler-product identity, or prove the required prescribed-Frobenius prime-series divergence. The compiled Mellin consumers in this block concern ordinary class characters. Those are the remaining Claim 9.1 dependencies, along with final manuscript separation assembly. The source ledger remains 17 checked / 3 partial.
