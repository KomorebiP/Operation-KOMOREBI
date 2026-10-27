# Structural closure return

Base checkpoint: checked Realization Boundaries Lean v0.6.0. The parent publication is unchanged.

Owner: structural agent. Write scope: `RealizationBoundaries/StructuralClosure.lean` and this note.

## Completed original contracts

- **4.6**: `preimage_countable_iff_rational_rank` proves countability of the actual preimage iff its rational quotient has rank at most aleph_0. `preimage_countable_iff_dimension_finite_or_countably_infinite` gives the exact finite-or-countably-infinite cardinal-rank formulation, including the zero subspace. The proof uses the actual basis coefficient Finsupp equivalence and the prior checked preimage/quotient countability equivalence.
- **5.4**: `cocycle_reads_coordinate` proves the printed equality in actual `finiteSupport`; the right side is the negative singleton cut of the selector indicator, exactly minus the selected coefficient times the prime seed. `cocycle_coordinate_nonzero_iff` recovers the selector bit from the cocycle's actual p coordinate. The proof preserves the zero-denominator branch, proves reduced prime denominators from coprimality, and uses the checked support theorem to exclude every other coordinate.
- **5.5**: `paired_fg_subgroup_classification` proves for every actual finitely generated subgroup L of G_a an actual additive equivalence either L ≃ ZMod m or L ≃ Z × ZMod m, for a positive squarefree m. It includes m = 1. There is also the more general infinite-selector theorem `fg_selector_subgroup_classification`.

## Mechanism of 5.5

1. Restrict the actual rational normal-form coordinate to L.
2. Use `RationalFG`'s independently compiled common-denominator lattice result to show its image is cyclic.
3. If the rational image is zero, L is torsion and finitely generated, hence finite.
4. Otherwise identify the rational image with Z, choose an actual lift of 1, and construct the split equivalence explicitly. The kernel is finitely generated as a retract of L and is torsion by the exact rational-kernel criterion, hence finite.
5. Any actual finite subgroup of an arbitrary preimage embeds into the kernel of multiplication by its own cardinality. The checked kernel-coordinate and CRT equivalences make it cyclic. Cardinal comparison forces its cardinality to equal its prime radical, hence to be squarefree.

The general finitely generated abelian-group theorem is used only for the standard result that a finitely generated torsion abelian group is finite. The actual local split and cyclic squarefree kernel are established here.

## Verification

Latest development compile: `verification/development/StructuralClosure_015.json`, exit code 0, warnings treated as errors, autoImplicit false, source hash matches below. All declarations are proof terms; no sorry/admit/axiom/unsafe production tokens were introduced. Root must integrate the two new module imports (RationalFG before StructuralClosure), run the full audit/kernel replay and add independent positive/rejection contracts before acceptance.

Earlier failed development compilations are retained. Failures were Lean namespace/API/transparency issues, unavailable inferred instances, numeral/cast normalization, and warning-as-error style checks. They were corrected rather than admitted. The final source compiles cleanly.

## Input and output SHA-256

```json
{
  "RealizationBoundaries/StructuralClosure.lean": "a2c13f3f067f25a94e17baae02dbe2ce4b38149a32be58887f4eac9f975fdeae",
  "RealizationBoundaries/RationalFG.lean": "e4e8b760d90286f1e43f73e8bf1a2bb041120a8f0fd752ed9f0aa07b0b0163aa",
  "RealizationBoundaries/Countability.lean": "8082ae4a6ac619e6681f29a146a0369e208fe5d94ddf0c1630fe5864a55be412",
  "RealizationBoundaries/Cocycle.lean": "a1f15a06278486bc9874dd1b0cd7153776c948cef97cf16c9ded4c103bd0e038",
  "RealizationBoundaries/Sections.lean": "59f264c6fb1ad6acea65047f285e6931be0d0424afaf5ed5a78f8d04caa79584",
  "RealizationBoundaries/RootFibers.lean": "954f87c272977c9ba4601d91b2d89dc25713e67b2e052127c4e6b12962833221",
  "RealizationBoundaries/CyclicQuotients.lean": "87be7c8a3a5add749249449cff06215383c2739e5a132f41e667ea80a99c79c8",
  "RealizationBoundaries/CyclicFiniteTargets.lean": "5cdb28fa54a11b4d8bb908420e61ed57d5d4e93e99acc0848143f720e2cf0294",
  "publication/Realization_Boundaries_Final.pdf": "a33739eec9f11a1c8c6e94c30301963d9ed1386ea2ede04041bbaa644b046ecc",
  "parent_archive": "032f61f0e176f0f3abfeb3615b8936ebd9edb7c3f9a07b6b8ad25877ec7aef70"
}
```

## Declaration names

- `rational_countable_iff_basis_countable`
- `preimage_countable_iff_basis_countable`
- `preimage_countable_iff_rational_rank`
- `preimage_countable_iff_dimension_finite_or_countably_infinite`
- `rational_prime_fraction_den`
- `rationalSection_prime_fraction_zero`
- `cocycle_reads_coordinate`
- `cocycle_coordinate_nonzero_iff`
- `finiteSubgroupKernelEmbedding`
- `finiteSubgroupKernelEmbedding_injective`
- `finite_preimage_subgroup_cyclic`
- `finite_preimage_subgroup_squarefree`
- `finite_preimage_subgroup_classification`
- `selectorRational`
- `selectorRational_eq_zero_iff`
- `integerSplitMap`
- `integerSplitMap_bijective`
- `integerSplitEquiv`
- `integerSplitKernel_fg`
- `finite_embedded_preimage_classification`
- `fg_selector_integer_kernel_finite`
- `fg_selector_subgroup_integer_classification`
- `fg_selector_subgroup_finite_of_rational_zero`
- `fg_selector_subgroup_classification`
- `paired_fg_subgroup_classification`

## Independent mathematical read review

The subgroup-spectrum agent separately reviewed the final 4.6, 5.4, and 5.5 contracts and the decomposition mechanism. They found no correctness or calibration concern: the integer quotient split, FG retraction, torsion-kernel finiteness, and cyclic squarefree finite factor match the printed result, including C1. This is a read review, not a substitute for the integrated compiler/axiom audit.
