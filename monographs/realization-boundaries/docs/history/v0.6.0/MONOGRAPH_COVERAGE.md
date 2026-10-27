# Monograph-to-Lean coverage — v0.6.0

The 45 original numbered statements are preserved. A status refers to the exact printed contract, not a percentage of completion. The publication itself has not been edited.

**Newly COMPLETE:** 6.2 (all roots and their number), 6.3 (all integer quotients).

| Statement | Title | Status |
|---|---|---|
| 1.5 | Countable-code bound | PENDING |
| 1.8 | Reachability obstruction | PENDING |
| 2.1 | The torsion subgroup of the product | COMPLETE |
| 2.2 | Diagonal endomorphisms of the direct sum | COMPLETE |
| 2.3 | An infinite seed obstruction | COMPLETE |
| 2.4 | Topological cyclicity | COMPLETE |
| 2.5 | Profinite completion of the direct sum | COMPLETE |
| 2.6 | Unique division in the ambient quotient | COMPLETE_ALGEBRAIC |
| 3.1 | Subgroup and isomorphism classification | PENDING |
| 3.2 | Finite observations leave continuum many possibilities | PENDING |
| 3.3 | The prime-spectrum criterion | PENDING |
| 3.4 | (untitled) | PENDING |
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
| 6.2 | All roots and their number | COMPLETE |
| 6.3 | All integer quotients | COMPLETE |
| 6.4 | Common profinite completion | COMPLETE |
| 7.1 | Tail signature | COMPLETE |
| 7.2 | Unmarked isomorphism classification | COMPLETE |
| 7.3 | Marked classification | COMPLETE |
| 7.5 | Complete homomorphism description | COMPLETE |
| 7.6 | Torsion-image obstruction | COMPLETE |
| 7.7 | Endomorphism ring | COMPLETE |
| 7.8 | Automorphisms | COMPLETE |
| 7.9 | Seed-rank separation | COMPLETE |
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

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.

## 1.8 — Reachability obstruction

The general graph-reachability theorem is still pending. This checkpoint proves a reusable closed invariant-subgroup/coordinate-kernel certificate and the diagonal applications; it does not identify this special case with full graph reachability.

No formal declaration is claimed for this printed statement.

## 2.1 — The torsion subgroup of the product

The original finite-support subgroup is torsion, dense and proper in the actual unrestricted product.

Declarations: `RealizationBoundaries.torsion_iff_finiteSupport`, `RealizationBoundaries.finiteSupport_dense`, `RealizationBoundaries.finiteSupport_ne_top`

## 2.2 — Diagonal endomorphisms of the direct sum

The actual finite-support group D has endomorphism ring isomorphic to the full prime-coordinate product. All endomorphisms are derived to be diagonal, and zero-coordinate preservation is proved. Seed-rank cardinalities remain separate.

Declarations: `RealizationBoundaries.finiteSupportEndomorphismRingEquiv`, `RealizationBoundaries.finiteSupportDiagonalRing_bijective`, `RealizationBoundaries.finiteSupport_endomorphism_coordinate`, `RealizationBoundaries.finiteSupport_endomorphism_preserves_zero`

## 2.3 — An infinite seed obstruction

Exact least cardinal aleph_0 for full-endomorphism algebraic generation. The closure in the actual induced topology has its own closed-coordinate obstruction and separately proved rank. The upper witness uses the checked countability of the actual group, not finite truncations.

Declarations: `RealizationBoundaries.finiteSupport_seed_certificate`, `RealizationBoundaries.finiteSupport_no_finite_endomorphism_seeds`, `RealizationBoundaries.finiteSupport_no_finite_topological_seeds`, `RealizationBoundaries.finiteSupport_endomorphismSeedRank`, `RealizationBoundaries.finiteSupport_topologicalEndomorphismSeedRank`

## 2.4 — Topological cyclicity

An actual integer matches every finite prime-coordinate pattern by the finite Chinese remainder theorem. This proves density of the ordinary cyclic subgroup of the all-one vector in the genuine product topology. A nontrivial Hausdorff lower bound excludes rank zero, establishing exact ordinary topological rank one.

Declarations: `RealizationBoundaries.finite_coordinate_interpolation`, `RealizationBoundaries.ambient_cyclic_dense`, `RealizationBoundaries.ambient_topological_generator`, `RealizationBoundaries.ambient_ordinaryTopologicalRank`

## 2.5 — Profinite completion of the direct sum

Topological additive equivalence from Mathlib's actual all-finite-quotients completion of D to P, respecting the canonical map.

Declarations: `RealizationBoundaries.finiteSupportCompletionEquiv`, `RealizationBoundaries.finiteSupportCompletionEquiv_eta`

## 2.6 — Unique division in the ambient quotient

Actual quotient and derived rational module; no nonzero divisible embedding in P.

Declarations: `RealizationBoundaries.tail_nsmul_bijective`, `RealizationBoundaries.tail_rational_module_unique`, `RealizationBoundaries.hom_zero_of_divisible`, `RealizationBoundaries.not_injective_hom_of_divisible`

## 3.1 — Subgroup and isomorphism classification

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.

## 3.2 — Finite observations leave continuum many possibilities

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.

## 3.3 — The prime-spectrum criterion

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.

## 3.4 — (untitled)

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.

## 3.5 — Unary selector classification

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.

## 4.2 — Pure-preimage correspondence

Both directions, both inverse laws and order reflection are checked. Purity is root lifting in P; inclusion of D is explicit.

Declarations: `RealizationBoundaries.IsPure`, `RealizationBoundaries.pure_root_closed`, `RealizationBoundaries.rationalImage`, `RealizationBoundaries.purePreimageOrderIso`, `RealizationBoundaries.exists_unique_rational_preimage`

## 4.3 — Ambient root criterion

Both directions for every positive multiplier and every actual preimage.

Declarations: `RealizationBoundaries.ambient_root_iff`, `RealizationBoundaries.preimage_root_iff`

## 4.4 — One finite-quotient system for every preimage

Canonical integer quotients, coordinate transitions, finite-target cofinal kernels and the actual profinite completion are checked.

Declarations: `RealizationBoundaries.integerQuotientEquiv`, `RealizationBoundaries.integerQuotientEquiv_mk`, `RealizationBoundaries.coordinateRestriction_map`, `RealizationBoundaries.finite_target_coordinate_kernel`, `RealizationBoundaries.profiniteCompletionEquiv`, `RealizationBoundaries.profiniteCompletionEquiv_eta`

## 4.5 — Finite-target equivalence

An equivalence between Hom(H_W,F) and Hom(D,F) for every finite additive-group target. Its forward map is the literal restriction, and naturality under target homomorphisms is proved.

Declarations: `RealizationBoundaries.finiteSupportRestrictionEquiv`, `RealizationBoundaries.finiteSupportRestrictionEquiv_apply`, `RealizationBoundaries.finiteSupportRestrictionEquiv_natural`

## 4.6 — Structure of an ambient preimage

Torsion, quotient, reducedness via absence of divisible embeddings, residual finiteness, nonsplitting and Countable(H_W) iff Countable(W) are checked. The printed reformulation in terms of finite or countably infinite rational dimension is still pending.

Declarations: `RealizationBoundaries.preimage_torsion_iff`, `RealizationBoundaries.preimageQuotientEquiv`, `RealizationBoundaries.rational_hom_zero`, `RealizationBoundaries.preimage_residuallyFinite`, `RealizationBoundaries.preimage_countable_iff`, `RealizationBoundaries.no_section_of_nontrivial`

## 5.1 — Unique normal form

Existence, uniqueness, the selector-independent Q x D domain and countable infinitude of every paired group are now checked.

Declarations: `RealizationBoundaries.normalForm_exists`, `RealizationBoundaries.normalForm_unique`, `RealizationBoundaries.normalFormEquiv`, `RealizationBoundaries.paired_countably_infinite`, `RealizationBoundaries.NormalForm.pairEquiv`, `RealizationBoundaries.pairedNormalFormEquiv`

## 5.2 — A finite support bound

The actual infinite-coordinate defect is supported on denominator primes.

Declarations: `RealizationBoundaries.sectionDefect_support`, `RealizationBoundaries.sectionDefect_finite`

## 5.3 — Explicit group law

Separate twisted group type, all additive group laws, and actual additive equivalence to the preimage.

Declarations: `RealizationBoundaries.cocycle_identity`, `RealizationBoundaries.normalAdd_assoc`, `RealizationBoundaries.normalAdd_comm`, `RealizationBoundaries.normalAdd_zero`, `RealizationBoundaries.normalAdd_inverse`, `RealizationBoundaries.NormalForm.realizationEquiv`

## 5.4 — One cocycle value reads one coordinate

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.

## 5.5 — Finitely generated subgroups

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.

## 6.1 — Root or obstruction

Exact root equivalence, nonexistence certificates, and a coordinatewise specified normalized root with uniqueness under zero-divisor-coordinate normalization are checked. The specific rational-plus-finite normal-form solver, its explicit denominator/support bound, implementation and algorithmic cost have not been proved by extraction. This remains CORE_COMPLETE rather than a full algorithm-verification claim.

Declarations: `RealizationBoundaries.ambient_root_iff`, `RealizationBoundaries.preimage_root_iff`, `RealizationBoundaries.prime_obstruction`, `RealizationBoundaries.coordinateDivide_root`, `RealizationBoundaries.normalizedRoot`, `RealizationBoundaries.normalizedRoot_coordinate`, `RealizationBoundaries.normalizedRoot_exceptional_zero`, `RealizationBoundaries.normalizedRoot_unique`

## 6.2 — All roots and their number

Actual fibers and integer-torsion kernels are constructed for every rational preimage H_W. Translation by a supplied root gives the exact coset parametrization. An explicit additive equivalence identifies the kernel with the divisor-coordinate product, and the positive-multiplier fiber is proved finite with radical cardinality when nonempty and zero when obstructed. Prime powers and multiplier one are retained; multiplier zero is separately proved infinite at zero.

Declarations: `RealizationBoundaries.RootFiber`, `RealizationBoundaries.rootKernelEquiv`, `RealizationBoundaries.rootFiberTranslation`, `RealizationBoundaries.rootFiber_coset_iff`, `RealizationBoundaries.rootFiberEquiv`, `RealizationBoundaries.rootFiberEquiv_symm_apply`, `RealizationBoundaries.rootFiber_finite`, `RealizationBoundaries.rootKernel_card`, `RealizationBoundaries.rootFiber_card_of_solvable`, `RealizationBoundaries.rootFiber_card`, `RealizationBoundaries.prime_power_root_count`

## 6.3 — All integer quotients

The actual quotient by m H_W is additively equivalent to ZMod(rad m), with the representative formula and quotient transitions commuting with canonical residue reduction. The multiples equal the radical multiples as literal subgroups. Every finite quotient is cyclic and squarefree, every finite cyclic squarefree target is achieved by an actual surjection, and its kernel is the literal target-order multiple subgroup.

Declarations: `RealizationBoundaries.integerQuotientEquiv`, `RealizationBoundaries.divisorCrtEquiv`, `RealizationBoundaries.cyclicIntegerQuotientEquiv`, `RealizationBoundaries.cyclicIntegerQuotientEquiv_mk`, `RealizationBoundaries.quotientRestriction`, `RealizationBoundaries.integerQuotientEquiv_restriction`, `RealizationBoundaries.cyclicIntegerQuotientEquiv_restriction`, `RealizationBoundaries.multiples_eq_radical`, `RealizationBoundaries.finite_quotient_exists_iff`, `RealizationBoundaries.finite_surjection_ker`

## 6.4 — Common profinite completion

Every paired group has the actual canonical profinite completion P. Its induced product topology equals the full topology induced from the limit of all finite quotients.

Declarations: `RealizationBoundaries.pairedCompletionEquiv`, `RealizationBoundaries.profiniteCompletionEquiv_eta`, `RealizationBoundaries.completion_eta_isEmbedding`, `RealizationBoundaries.fullProfiniteTopology_eq`

## 7.1 — Tail signature

Every nontorsion element of the actual selector group has the eventual prime-root signature. The exception set explicitly includes primes dividing the numerator absolute value, denominator primes, and the finite correction support. No all-prime conclusion is substituted.

Declarations: `RealizationBoundaries.tailExceptions_finite`, `RealizationBoundaries.normalForm_coordinate_ne_zero_iff`, `RealizationBoundaries.selector_tail_signature`

## 7.2 — Unmarked isomorphism classification

Both directions of the unmarked classification are checked. Finite bit disagreement gives literal ambient subgroup equality, a point-preserving AddEquiv, and the exact rational-section finite-correction coordinate transport respecting twisted addition. The conclusion is finite disagreement, not literal selector equality.

Declarations: `RealizationBoundaries.pairedGroup_isomorphic_iff`, `RealizationBoundaries.pairedGroup_eq_of_finite_disagreement`, `RealizationBoundaries.pairedEquivOfFiniteDisagreement_val`, `RealizationBoundaries.normalFormTransportEquiv_apply`, `RealizationBoundaries.normalFormTransport_add`

## 7.3 — Marked classification

An additive equivalence carrying the specified indicator to the other specified indicator exists exactly when every selector bit agrees. A one-bit toggle gives the same unmarked group but no such marked isomorphism.

Declarations: `RealizationBoundaries.selectors_equal_of_markedEquiv`, `RealizationBoundaries.pairedGroup_marked_isomorphic_iff`, `RealizationBoundaries.toggleBit_not_marked_isomorphic`

## 7.5 — Complete homomorphism description

Every actual additive homomorphism is proved diagonal without continuity or diagonal hypotheses. The exact converse, finite-defect condition, automatic continuity, and its full-completion coordinate action are checked. The diagonal formula holds for all rational preimages H_W, not only paired selector groups.

Declarations: `RealizationBoundaries.hom_coordinate_formula`, `RealizationBoundaries.homDiagonal_unique`, `RealizationBoundaries.diagonalHomEquiv`, `RealizationBoundaries.diagonalTail`, `RealizationBoundaries.diagonalAdmissible_selector_iff`, `RealizationBoundaries.diagonalAdmissible_iff_finite_defect`, `RealizationBoundaries.selectorHomEquiv`, `RealizationBoundaries.preimage_hom_continuous`, `RealizationBoundaries.completionHom_coordinates`

## 7.6 — Torsion-image obstruction

Arbitrary additive homomorphisms, with no continuity or diagonality hypothesis, have torsion image when selectors disagree infinitely. Every map factors uniquely through the actual D, and injective or surjective maps exist exactly at finite disagreement. A nonzero coordinate map is proved in the positive suite, guarding against a false zero-image conclusion.

Declarations: `RealizationBoundaries.finite_disagreement_of_nontorsion_image`, `RealizationBoundaries.hom_image_finiteSupport`, `RealizationBoundaries.hom_image_torsion`, `RealizationBoundaries.torsionFactor_commutes`, `RealizationBoundaries.torsionFactor_unique`, `RealizationBoundaries.no_injective_hom_of_infinite_disagreement`, `RealizationBoundaries.no_surjective_hom_of_infinite_disagreement`, `RealizationBoundaries.pairedGroup_embeds_iff`, `RealizationBoundaries.pairedGroup_surjects_iff`

## 7.7 — Endomorphism ring

The actual endomorphism ring is identified as the admissible diagonal subring, with the eventual-rational selected-coordinate characterization. Infinite selector support makes the rational quotient scalar unique. Ring laws, surjectivity and the exact zero-scalar kernel are proved. Denominator primes remain in the permitted finite exceptional set. The chosen lifts are not claimed to form a homomorphic section.

Declarations: `RealizationBoundaries.endomorphismRingEquiv`, `RealizationBoundaries.diagonalEndRing_mem_iff`, `RealizationBoundaries.diagonalSlope_unique`, `RealizationBoundaries.diagonalSlope_eq_of_finite_defect`, `RealizationBoundaries.quotientScalar`, `RealizationBoundaries.quotientScalar_surjective`, `RealizationBoundaries.quotientScalar_eq_zero_iff`, `RealizationBoundaries.endomorphismQuotientScalar`, `RealizationBoundaries.endomorphismQuotientScalar_surjective`

## 7.8 — Automorphisms

The automorphism criterion requires every prime-coordinate scalar to be nonzero. The inverse multiplier is proved to preserve the original rank-one groups, the quotient scalar is proved nonzero, and the actual inverse formula is checked. Product invertibility is not assumed to imply invertibility on arbitrary rational-subspace preimages.

Declarations: `RealizationBoundaries.hom_injective_iff_diagonal_nonzero`, `RealizationBoundaries.diagonalSlope_ne_zero`, `RealizationBoundaries.inverseDiagonal_admissible`, `RealizationBoundaries.selectorEquivOfNonzeroDiagonal`, `RealizationBoundaries.selectorEquiv_inverse_coordinate`, `RealizationBoundaries.selector_endomorphism_automorphism_iff`, `RealizationBoundaries.selector_hom_bijective_iff`

## 7.9 — Seed-rank separation

For every binary selector: exact algebraic full-endomorphism rank aleph_0, no finite topological operator family, and exact ordinary topological rank aleph_0 in the original group. The actual canonical completion has a named topological generator and ordinary topological rank one. These contracts are defined separately and proved together in the final bundled theorem.

Declarations: `RealizationBoundaries.selector_outside_support_finite`, `RealizationBoundaries.paired_seed_certificate`, `RealizationBoundaries.paired_endomorphismSeedRank`, `RealizationBoundaries.paired_topologicalEndomorphismSeedRank`, `RealizationBoundaries.paired_ordinaryTopologicalRank`, `RealizationBoundaries.completionGenerator_generates`, `RealizationBoundaries.canonicalCompletion_ordinaryTopologicalRank`, `RealizationBoundaries.paired_seed_rank_separation`

## 8.1 — Uniform construction relative to the selector

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.

## 8.2 — Uniform marked decoding

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.

## 8.3 — Exact oracle criterion

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.

## 8.4 — Degree variation with fixed observations

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.

## 9.1 — No decoder from the unmarked finite-quotient system

The two-object counterexample and an explicit no-reconstruction contract for arbitrary group assignments invariant under isomorphism of the canonical profinite completions are checked. No computability assumption is imposed. The book phrases its input as a pro-object of finite quotient systems; a separately formalized pro-object decoder interface and the identification of that exact interface with the completion contract remain unimplemented. Cofinal coordinate quotients and natural finite-target comparisons are checked in the prior tranche.

Declarations: `RealizationBoundaries.completion_object_counterexample`, `RealizationBoundaries.no_completion_invariant_reconstruction`

## 9.2 — A proper map invisible after completion

The literal inclusion D to G_a is not surjective. Its extension to their actual completions is a topological additive isomorphism, with equality on every canonical D point.

Declarations: `RealizationBoundaries.finiteSupport_inclusion_not_surjective`, `RealizationBoundaries.finiteSupportToPairedCompletion`, `RealizationBoundaries.finiteSupportToPairedCompletion_eta`

## 9.3 — Faithfulness and failure of fullness

The proper-inclusion witness and paired-family failure of lifting are checked. The new completionHom is faithful on all rational-preimage homomorphism sets and respects composition. The global category of all residually finite groups and a packaged categorical fullness statement remain outside formal scope; the registry therefore remains PARTIAL.

Declarations: `RealizationBoundaries.no_lift_of_commonCompletionEquiv`, `RealizationBoundaries.finiteSupportToPairedCompletion_eta`, `RealizationBoundaries.finiteSupport_inclusion_not_surjective`, `RealizationBoundaries.completionHom_injective`, `RealizationBoundaries.completionHom_comp`, `RealizationBoundaries.completionHom_unique`

## 9.4 — Reflection within the paired-prime family

For a supplied homomorphism between paired-prime groups, its actual induced map on canonical profinite completions is a continuous additive isomorphism exactly when the supplied original map is an additive isomorphism. The extension is constructed and identified by its eta equation and uniqueness, not by an assumed diagonal formula or an unavailable additive functor API. This does not reconstruct an unknown source from its completion.

Declarations: `RealizationBoundaries.completionHom`, `RealizationBoundaries.completionHom_eta`, `RealizationBoundaries.completionHom_unique`, `RealizationBoundaries.completionHom_comp`, `RealizationBoundaries.completionHom_isomorphism_iff`, `RealizationBoundaries.selector_completion_reflection`, `RealizationBoundaries.paired_completion_reflects_isomorphisms`

## 10.1 — Escape within one profinite-completion class

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.

## 10.2 — Admissible expansion

Not formalized in this tranche.

No formal declaration is claimed for this printed statement.
