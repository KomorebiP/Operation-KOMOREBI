# Monograph-to-Lean coverage — v0.4.0

All 45 original numbered statements are retained. Status is a theorem-specific claim, not a percentage. New complete entries are 2.2, 7.5, 7.7, 7.8 and 9.4. The printed monograph is unchanged.

| Book statement | Title | Formal status |
|---|---|---|
| 1.5 | Countable-code bound | PENDING |
| 1.8 | Reachability obstruction | PENDING |
| 2.1 | The torsion subgroup of the product | COMPLETE |
| 2.2 | Diagonal endomorphisms of the direct sum | COMPLETE |
| 2.3 | An infinite seed obstruction | PENDING |
| 2.4 | Topological cyclicity | PENDING |
| 2.5 | Profinite completion of the direct sum | COMPLETE |
| 2.6 | Unique division in the ambient quotient | COMPLETE_ALGEBRAIC |
| 3.1 | Subgroup and isomorphism classification | PENDING |
| 3.2 | Finite observations leave continuum many possibilities | PENDING |
| 3.3 | The prime-spectrum criterion | PENDING |
| 3.4 |  | PENDING |
| 3.5 | Unary selector classification | PENDING |
| 4.2 | Pure-preimage correspondence | COMPLETE |
| 4.3 | Ambient root criterion | COMPLETE |
| 4.4 | One finite-quotient system for every preimage | COMPLETE |
| 4.5 | Finite-target equivalence | COMPLETE |
| 4.6 | Structure of an ambient preimage | PARTIAL |
| 5.1 | Unique normal form | COMPLETE |
| 5.2 | A finite support bound | COMPLETE |
| 5.3 | Explicit group law | COMPLETE |
| 5.4 | One cocycle value reads one coordinate | PENDING |
| 5.5 | Finitely generated subgroups | PENDING |
| 6.1 | Root or obstruction | CORE_COMPLETE |
| 6.2 | All roots and their number | PENDING |
| 6.3 | All integer quotients | PARTIAL |
| 6.4 | Common profinite completion | COMPLETE |
| 7.1 | Tail signature | COMPLETE |
| 7.2 | Unmarked isomorphism classification | COMPLETE |
| 7.3 | Marked classification | COMPLETE |
| 7.5 | Complete homomorphism description | COMPLETE |
| 7.6 | Torsion-image obstruction | COMPLETE |
| 7.7 | Endomorphism ring | COMPLETE |
| 7.8 | Automorphisms | COMPLETE |
| 7.9 | Seed-rank separation | PENDING |
| 8.1 | Uniform construction relative to the selector | PENDING |
| 8.2 | Uniform marked decoding | PENDING |
| 8.3 | Exact oracle criterion | PENDING |
| 8.4 | Degree variation with fixed observations | PENDING |
| 9.1 | No decoder from the unmarked finite-quotient system | PARTIAL |
| 9.2 | A proper map invisible after completion | COMPLETE |
| 9.3 | Faithfulness and failure of fullness | PARTIAL |
| 9.4 | Reflection within the paired-prime family | COMPLETE |
| 10.1 | Escape within one profinite-completion class | PENDING |
| 10.2 | Admissible expansion | PENDING |

## 1.5 — Countable-code bound

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/01_contracts.tex`, line 35; printed page 2.

## 1.8 — Reachability obstruction

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/01_contracts.tex`, line 63; printed page 3.

## 2.1 — The torsion subgroup of the product

**COMPLETE**. The original finite-support subgroup is torsion, dense and proper in the actual unrestricted product.

- `RealizationBoundaries.torsion_iff_finiteSupport`
- `RealizationBoundaries.finiteSupport_dense`
- `RealizationBoundaries.finiteSupport_ne_top`

Book source: `manuscript/chapters/02_ambient.tex`, line 35; printed page 5.

## 2.2 — Diagonal endomorphisms of the direct sum

**COMPLETE**. The actual finite-support group D has endomorphism ring isomorphic to the full prime-coordinate product. All endomorphisms are derived to be diagonal, and zero-coordinate preservation is proved. Seed-rank cardinalities remain separate.

- `RealizationBoundaries.finiteSupportEndomorphismRingEquiv`
- `RealizationBoundaries.finiteSupportDiagonalRing_bijective`
- `RealizationBoundaries.finiteSupport_endomorphism_coordinate`
- `RealizationBoundaries.finiteSupport_endomorphism_preserves_zero`

Book source: `manuscript/chapters/02_ambient.tex`, line 48; printed page 6.

## 2.3 — An infinite seed obstruction

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/02_ambient.tex`, line 60; printed page 6.

## 2.4 — Topological cyclicity

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/02_ambient.tex`, line 70; printed page 6.

## 2.5 — Profinite completion of the direct sum

**COMPLETE**. Topological additive equivalence from Mathlib's actual all-finite-quotients completion of D to P, respecting the canonical map.

- `RealizationBoundaries.finiteSupportCompletionEquiv`
- `RealizationBoundaries.finiteSupportCompletionEquiv_eta`

Book source: `manuscript/chapters/02_ambient.tex`, line 90; printed page 7.

## 2.6 — Unique division in the ambient quotient

**COMPLETE_ALGEBRAIC**. Actual quotient and derived rational module; no nonzero divisible embedding in P.

- `RealizationBoundaries.tail_nsmul_bijective`
- `RealizationBoundaries.tail_rational_module_unique`
- `RealizationBoundaries.hom_zero_of_divisible`
- `RealizationBoundaries.not_injective_hom_of_divisible`

Book source: `manuscript/chapters/02_ambient.tex`, line 102; printed page 8.

## 3.1 — Subgroup and isomorphism classification

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/03_spectrum.tex`, line 12; printed page 9.

## 3.2 — Finite observations leave continuum many possibilities

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/03_spectrum.tex`, line 33; printed page 10.

## 3.3 — The prime-spectrum criterion

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/03_spectrum.tex`, line 44; printed page 10.

## 3.4 — 

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/03_spectrum.tex`, line 72; printed page 11.

## 3.5 — Unary selector classification

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/03_spectrum.tex`, line 86; printed page 11.

## 4.2 — Pure-preimage correspondence

**COMPLETE**. Both directions, both inverse laws and order reflection are checked. Purity is root lifting in P; inclusion of D is explicit.

- `RealizationBoundaries.IsPure`
- `RealizationBoundaries.pure_root_closed`
- `RealizationBoundaries.rationalImage`
- `RealizationBoundaries.purePreimageOrderIso`
- `RealizationBoundaries.exists_unique_rational_preimage`

Book source: `manuscript/chapters/04_purity.tex`, line 23; printed page 13.

## 4.3 — Ambient root criterion

**COMPLETE**. Both directions for every positive multiplier and every actual preimage.

- `RealizationBoundaries.ambient_root_iff`
- `RealizationBoundaries.preimage_root_iff`

Book source: `manuscript/chapters/04_purity.tex`, line 41; printed page 14.

## 4.4 — One finite-quotient system for every preimage

**COMPLETE**. Canonical integer quotients, coordinate transitions, finite-target cofinal kernels and the actual profinite completion are checked.

- `RealizationBoundaries.integerQuotientEquiv`
- `RealizationBoundaries.integerQuotientEquiv_mk`
- `RealizationBoundaries.coordinateRestriction_map`
- `RealizationBoundaries.finite_target_coordinate_kernel`
- `RealizationBoundaries.profiniteCompletionEquiv`
- `RealizationBoundaries.profiniteCompletionEquiv_eta`

Book source: `manuscript/chapters/04_purity.tex`, line 54; printed page 14.

## 4.5 — Finite-target equivalence

**COMPLETE**. An equivalence between Hom(H_W,F) and Hom(D,F) for every finite additive-group target. Its forward map is the literal restriction, and naturality under target homomorphisms is proved.

- `RealizationBoundaries.finiteSupportRestrictionEquiv`
- `RealizationBoundaries.finiteSupportRestrictionEquiv_apply`
- `RealizationBoundaries.finiteSupportRestrictionEquiv_natural`

Book source: `manuscript/chapters/04_purity.tex`, line 72; printed page 15.

## 4.6 — Structure of an ambient preimage

**PARTIAL**. Torsion, quotient, reducedness via absence of divisible embeddings, residual finiteness, nonsplitting and Countable(H_W) iff Countable(W) are checked. The printed reformulation in terms of finite or countably infinite rational dimension is still pending.

- `RealizationBoundaries.preimage_torsion_iff`
- `RealizationBoundaries.preimageQuotientEquiv`
- `RealizationBoundaries.rational_hom_zero`
- `RealizationBoundaries.preimage_residuallyFinite`
- `RealizationBoundaries.preimage_countable_iff`
- `RealizationBoundaries.no_section_of_nontrivial`

Book source: `manuscript/chapters/04_purity.tex`, line 87; printed page 15.

## 5.1 — Unique normal form

**COMPLETE**. Existence, uniqueness, the selector-independent Q x D domain and countable infinitude of every paired group are now checked.

- `RealizationBoundaries.normalForm_exists`
- `RealizationBoundaries.normalForm_unique`
- `RealizationBoundaries.normalFormEquiv`
- `RealizationBoundaries.paired_countably_infinite`
- `RealizationBoundaries.NormalForm.pairEquiv`
- `RealizationBoundaries.pairedNormalFormEquiv`

Book source: `manuscript/chapters/05_construction.tex`, line 44; printed page 18.

## 5.2 — A finite support bound

**COMPLETE**. The actual infinite-coordinate defect is supported on denominator primes.

- `RealizationBoundaries.sectionDefect_support`
- `RealizationBoundaries.sectionDefect_finite`

Book source: `manuscript/chapters/05_construction.tex`, line 64; printed page 18.

## 5.3 — Explicit group law

**COMPLETE**. Separate twisted group type, all additive group laws, and actual additive equivalence to the preimage.

- `RealizationBoundaries.cocycle_identity`
- `RealizationBoundaries.normalAdd_assoc`
- `RealizationBoundaries.normalAdd_comm`
- `RealizationBoundaries.normalAdd_zero`
- `RealizationBoundaries.normalAdd_inverse`
- `RealizationBoundaries.NormalForm.realizationEquiv`

Book source: `manuscript/chapters/05_construction.tex`, line 76; printed page 19.

## 5.4 — One cocycle value reads one coordinate

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/05_construction.tex`, line 96; printed page 19.

## 5.5 — Finitely generated subgroups

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/05_construction.tex`, line 123; printed page 20.

## 6.1 — Root or obstruction

**CORE_COMPLETE**. Exact root equivalence and coordinate root/nonexistence certificates. The finite Python normal-form solver and its algorithmic cost are not verified extractions.

- `RealizationBoundaries.ambient_root_iff`
- `RealizationBoundaries.preimage_root_iff`
- `RealizationBoundaries.prime_obstruction`

Book source: `manuscript/chapters/06_roots.tex`, line 14; printed page 21.

## 6.2 — All roots and their number

**PENDING**. Coset enumeration and radical cardinality are not yet formalized.


Book source: `manuscript/chapters/06_roots.tex`, line 40; printed page 22.

## 6.3 — All integer quotients

**PARTIAL**. Product of prime coordinates and transition maps proved. The explicit CRT equivalence with C_rad(m) remains.

- `RealizationBoundaries.integerQuotientEquiv`
- `RealizationBoundaries.coordinateRestriction_map`
- `RealizationBoundaries.multiples_eq_of_same_prime_divisors`

Book source: `manuscript/chapters/06_roots.tex`, line 55; printed page 22.

## 6.4 — Common profinite completion

**COMPLETE**. Every paired group has the actual canonical profinite completion P. Its induced product topology equals the full topology induced from the limit of all finite quotients.

- `RealizationBoundaries.pairedCompletionEquiv`
- `RealizationBoundaries.profiniteCompletionEquiv_eta`
- `RealizationBoundaries.completion_eta_isEmbedding`
- `RealizationBoundaries.fullProfiniteTopology_eq`

Book source: `manuscript/chapters/06_roots.tex`, line 96; printed page 23.

## 7.1 — Tail signature

**COMPLETE**. Every nontorsion element of the actual selector group has the eventual prime-root signature. The exception set explicitly includes primes dividing the numerator absolute value, denominator primes, and the finite correction support. No all-prime conclusion is substituted.

- `RealizationBoundaries.tailExceptions_finite`
- `RealizationBoundaries.normalForm_coordinate_ne_zero_iff`
- `RealizationBoundaries.selector_tail_signature`

Book source: `manuscript/chapters/07_classification.tex`, line 8; printed page 25.

## 7.2 — Unmarked isomorphism classification

**COMPLETE**. Both directions of the unmarked classification are checked. Finite bit disagreement gives literal ambient subgroup equality, a point-preserving AddEquiv, and the exact rational-section finite-correction coordinate transport respecting twisted addition. The conclusion is finite disagreement, not literal selector equality.

- `RealizationBoundaries.pairedGroup_isomorphic_iff`
- `RealizationBoundaries.pairedGroup_eq_of_finite_disagreement`
- `RealizationBoundaries.pairedEquivOfFiniteDisagreement_val`
- `RealizationBoundaries.normalFormTransportEquiv_apply`
- `RealizationBoundaries.normalFormTransport_add`

Book source: `manuscript/chapters/07_classification.tex`, line 22; printed page 25.

## 7.3 — Marked classification

**COMPLETE**. An additive equivalence carrying the specified indicator to the other specified indicator exists exactly when every selector bit agrees. A one-bit toggle gives the same unmarked group but no such marked isomorphism.

- `RealizationBoundaries.selectors_equal_of_markedEquiv`
- `RealizationBoundaries.pairedGroup_marked_isomorphic_iff`
- `RealizationBoundaries.toggleBit_not_marked_isomorphic`

Book source: `manuscript/chapters/07_classification.tex`, line 43; printed page 26.

## 7.5 — Complete homomorphism description

**COMPLETE**. Every actual additive homomorphism is proved diagonal without continuity or diagonal hypotheses. The exact converse, finite-defect condition, automatic continuity, and its full-completion coordinate action are checked. The diagonal formula holds for all rational preimages H_W, not only paired selector groups.

- `RealizationBoundaries.hom_coordinate_formula`
- `RealizationBoundaries.homDiagonal_unique`
- `RealizationBoundaries.diagonalHomEquiv`
- `RealizationBoundaries.diagonalTail`
- `RealizationBoundaries.diagonalAdmissible_selector_iff`
- `RealizationBoundaries.diagonalAdmissible_iff_finite_defect`
- `RealizationBoundaries.selectorHomEquiv`
- `RealizationBoundaries.preimage_hom_continuous`
- `RealizationBoundaries.completionHom_coordinates`

Book source: `manuscript/chapters/07_classification.tex`, line 58; printed page 26.

## 7.6 — Torsion-image obstruction

**COMPLETE**. Arbitrary additive homomorphisms, with no continuity or diagonality hypothesis, have torsion image when selectors disagree infinitely. Every map factors uniquely through the actual D, and injective or surjective maps exist exactly at finite disagreement. A nonzero coordinate map is proved in the positive suite, guarding against a false zero-image conclusion.

- `RealizationBoundaries.finite_disagreement_of_nontorsion_image`
- `RealizationBoundaries.hom_image_finiteSupport`
- `RealizationBoundaries.hom_image_torsion`
- `RealizationBoundaries.torsionFactor_commutes`
- `RealizationBoundaries.torsionFactor_unique`
- `RealizationBoundaries.no_injective_hom_of_infinite_disagreement`
- `RealizationBoundaries.no_surjective_hom_of_infinite_disagreement`
- `RealizationBoundaries.pairedGroup_embeds_iff`
- `RealizationBoundaries.pairedGroup_surjects_iff`

Book source: `manuscript/chapters/07_classification.tex`, line 78; printed page 27.

## 7.7 — Endomorphism ring

**COMPLETE**. The actual endomorphism ring is identified as the admissible diagonal subring, with the eventual-rational selected-coordinate characterization. Infinite selector support makes the rational quotient scalar unique. Ring laws, surjectivity and the exact zero-scalar kernel are proved. Denominator primes remain in the permitted finite exceptional set. The chosen lifts are not claimed to form a homomorphic section.

- `RealizationBoundaries.endomorphismRingEquiv`
- `RealizationBoundaries.diagonalEndRing_mem_iff`
- `RealizationBoundaries.diagonalSlope_unique`
- `RealizationBoundaries.diagonalSlope_eq_of_finite_defect`
- `RealizationBoundaries.quotientScalar`
- `RealizationBoundaries.quotientScalar_surjective`
- `RealizationBoundaries.quotientScalar_eq_zero_iff`
- `RealizationBoundaries.endomorphismQuotientScalar`
- `RealizationBoundaries.endomorphismQuotientScalar_surjective`

Book source: `manuscript/chapters/07_classification.tex`, line 94; printed page 27.

## 7.8 — Automorphisms

**COMPLETE**. The automorphism criterion requires every prime-coordinate scalar to be nonzero. The inverse multiplier is proved to preserve the original rank-one groups, the quotient scalar is proved nonzero, and the actual inverse formula is checked. Product invertibility is not assumed to imply invertibility on arbitrary rational-subspace preimages.

- `RealizationBoundaries.hom_injective_iff_diagonal_nonzero`
- `RealizationBoundaries.diagonalSlope_ne_zero`
- `RealizationBoundaries.inverseDiagonal_admissible`
- `RealizationBoundaries.selectorEquivOfNonzeroDiagonal`
- `RealizationBoundaries.selectorEquiv_inverse_coordinate`
- `RealizationBoundaries.selector_endomorphism_automorphism_iff`
- `RealizationBoundaries.selector_hom_bijective_iff`

Book source: `manuscript/chapters/07_classification.tex`, line 111; printed page 28.

## 7.9 — Seed-rank separation

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/07_classification.tex`, line 120; printed page 28.

## 8.1 — Uniform construction relative to the selector

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/08_computability.tex`, line 15; printed page 29.

## 8.2 — Uniform marked decoding

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/08_computability.tex`, line 27; printed page 30.

## 8.3 — Exact oracle criterion

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/08_computability.tex`, line 47; printed page 30.

## 8.4 — Degree variation with fixed observations

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/08_computability.tex`, line 74; printed page 31.

## 9.1 — No decoder from the unmarked finite-quotient system

**PARTIAL**. The two-object counterexample and an explicit no-reconstruction contract for arbitrary group assignments invariant under isomorphism of the canonical profinite completions are checked. No computability assumption is imposed. The book phrases its input as a pro-object of finite quotient systems; a separately formalized pro-object decoder interface and the identification of that exact interface with the completion contract remain unimplemented. Cofinal coordinate quotients and natural finite-target comparisons are checked in the prior tranche.

- `RealizationBoundaries.completion_object_counterexample`
- `RealizationBoundaries.no_completion_invariant_reconstruction`

Book source: `manuscript/chapters/09_reconstruction.tex`, line 14; printed page 33.

## 9.2 — A proper map invisible after completion

**COMPLETE**. The literal inclusion D to G_a is not surjective. Its extension to their actual completions is a topological additive isomorphism, with equality on every canonical D point.

- `RealizationBoundaries.finiteSupport_inclusion_not_surjective`
- `RealizationBoundaries.finiteSupportToPairedCompletion`
- `RealizationBoundaries.finiteSupportToPairedCompletion_eta`

Book source: `manuscript/chapters/09_reconstruction.tex`, line 43; printed page 34.

## 9.3 — Faithfulness and failure of fullness

**PARTIAL**. The proper-inclusion witness and paired-family failure of lifting are checked. The new completionHom is faithful on all rational-preimage homomorphism sets and respects composition. The global category of all residually finite groups and a packaged categorical fullness statement remain outside formal scope; the registry therefore remains PARTIAL.

- `RealizationBoundaries.no_lift_of_commonCompletionEquiv`
- `RealizationBoundaries.finiteSupportToPairedCompletion_eta`
- `RealizationBoundaries.finiteSupport_inclusion_not_surjective`
- `RealizationBoundaries.completionHom_injective`
- `RealizationBoundaries.completionHom_comp`
- `RealizationBoundaries.completionHom_unique`

Book source: `manuscript/chapters/09_reconstruction.tex`, line 55; printed page 35.

## 9.4 — Reflection within the paired-prime family

**COMPLETE**. For a supplied homomorphism between paired-prime groups, its actual induced map on canonical profinite completions is a continuous additive isomorphism exactly when the supplied original map is an additive isomorphism. The extension is constructed and identified by its eta equation and uniqueness, not by an assumed diagonal formula or an unavailable additive functor API. This does not reconstruct an unknown source from its completion.

- `RealizationBoundaries.completionHom`
- `RealizationBoundaries.completionHom_eta`
- `RealizationBoundaries.completionHom_unique`
- `RealizationBoundaries.completionHom_comp`
- `RealizationBoundaries.completionHom_isomorphism_iff`
- `RealizationBoundaries.selector_completion_reflection`
- `RealizationBoundaries.paired_completion_reflects_isomorphisms`

Book source: `manuscript/chapters/09_reconstruction.tex`, line 66; printed page 35.

## 10.1 — Escape within one profinite-completion class

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/10_grammar.tex`, line 26; printed page 37.

## 10.2 — Admissible expansion

**PENDING**. Not formalized in this tranche.


Book source: `manuscript/chapters/10_grammar.tex`, line 54; printed page 39.
