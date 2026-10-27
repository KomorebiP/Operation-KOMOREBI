# Monograph coverage — v0.3.0

All 45 numbered entries are retained. COMPLETE means the printed mathematical claim is covered by the indicated formal declarations. Partial entries retain the exact missing clauses. Source theorem counts are not percentages of monograph completion.

| Entry | Result | Coverage |
|---|---|---|
| 1.5 | Countable-code bound | PENDING |
| 1.8 | Reachability obstruction | PENDING |
| 2.1 | The torsion subgroup of the product | COMPLETE |
| 2.2 | Diagonal endomorphisms of the direct sum | PENDING |
| 2.3 | An infinite seed obstruction | PENDING |
| 2.4 | Topological cyclicity | PENDING |
| 2.5 | Profinite completion of the direct sum | COMPLETE |
| 2.6 | Unique division in the ambient quotient | COMPLETE_ALGEBRAIC |
| 3.1 | Subgroup and isomorphism classification | PENDING |
| 3.2 | Finite observations leave continuum many possibilities | PENDING |
| 3.3 | The prime-spectrum criterion | PENDING |
| 3.4 | (untitled corollary) | PENDING |
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
| 7.5 | Complete homomorphism description | PENDING |
| 7.6 | Torsion-image obstruction | COMPLETE |
| 7.7 | Endomorphism ring | PENDING |
| 7.8 | Automorphisms | PENDING |
| 7.9 | Seed-rank separation | PENDING |
| 8.1 | Uniform construction relative to the selector | PENDING |
| 8.2 | Uniform marked decoding | PENDING |
| 8.3 | Exact oracle criterion | PENDING |
| 8.4 | Degree variation with fixed observations | PENDING |
| 9.1 | No decoder from the unmarked finite-quotient system | PARTIAL |
| 9.2 | A proper map invisible after completion | COMPLETE |
| 9.3 | Faithfulness and failure of fullness | PARTIAL |
| 9.4 | Reflection within the paired-prime family | PENDING |
| 10.1 | Escape within one profinite-completion class | PENDING |
| 10.2 | Admissible expansion | PENDING |

## New and revised mappings

### 7.1 — Tail signature

Every nontorsion element of the actual selector group has the eventual prime-root signature. The exception set explicitly includes primes dividing the numerator absolute value, denominator primes, and the finite correction support. No all-prime conclusion is substituted.

- `RealizationBoundaries.tailExceptions_finite`
- `RealizationBoundaries.normalForm_coordinate_ne_zero_iff`
- `RealizationBoundaries.selector_tail_signature`

### 7.2 — Unmarked isomorphism classification

Both directions of the unmarked classification are checked. Finite bit disagreement gives literal ambient subgroup equality, a point-preserving AddEquiv, and the exact rational-section finite-correction coordinate transport respecting twisted addition. The conclusion is finite disagreement, not literal selector equality.

- `RealizationBoundaries.pairedGroup_isomorphic_iff`
- `RealizationBoundaries.pairedGroup_eq_of_finite_disagreement`
- `RealizationBoundaries.pairedEquivOfFiniteDisagreement_val`
- `RealizationBoundaries.normalFormTransportEquiv_apply`
- `RealizationBoundaries.normalFormTransport_add`

### 7.3 — Marked classification

An additive equivalence carrying the specified indicator to the other specified indicator exists exactly when every selector bit agrees. A one-bit toggle gives the same unmarked group but no such marked isomorphism.

- `RealizationBoundaries.selectors_equal_of_markedEquiv`
- `RealizationBoundaries.pairedGroup_marked_isomorphic_iff`
- `RealizationBoundaries.toggleBit_not_marked_isomorphic`

### 7.6 — Torsion-image obstruction

Arbitrary additive homomorphisms, with no continuity or diagonality hypothesis, have torsion image when selectors disagree infinitely. Every map factors uniquely through the actual D, and injective or surjective maps exist exactly at finite disagreement. A nonzero coordinate map is proved in the positive suite, guarding against a false zero-image conclusion.

- `RealizationBoundaries.finite_disagreement_of_nontorsion_image`
- `RealizationBoundaries.hom_image_finiteSupport`
- `RealizationBoundaries.hom_image_torsion`
- `RealizationBoundaries.torsionFactor_commutes`
- `RealizationBoundaries.torsionFactor_unique`
- `RealizationBoundaries.no_injective_hom_of_infinite_disagreement`
- `RealizationBoundaries.no_surjective_hom_of_infinite_disagreement`
- `RealizationBoundaries.pairedGroup_embeds_iff`
- `RealizationBoundaries.pairedGroup_surjects_iff`

### 9.1 — No decoder from the unmarked finite-quotient system

The two-object counterexample and an explicit no-reconstruction contract for arbitrary group assignments invariant under isomorphism of the canonical profinite completions are checked. No computability assumption is imposed. The book phrases its input as a pro-object of finite quotient systems; a separately formalized pro-object decoder interface and the identification of that exact interface with the completion contract remain unimplemented. Cofinal coordinate quotients and natural finite-target comparisons are checked in the prior tranche.

- `RealizationBoundaries.completion_object_counterexample`
- `RealizationBoundaries.no_completion_invariant_reconstruction`

### 9.3 — Faithfulness and failure of fullness

The actual canonical completion comparison has no homomorphism lift respecting eta when selectors disagree infinitely, giving an explicit nonfullness witness. The prior proper D inclusion is retained. A bundled categorical proof of faithfulness for all residually finite groups and the full functor-level combined statement are not yet supplied.

- `RealizationBoundaries.no_lift_of_commonCompletionEquiv`
- `RealizationBoundaries.finiteSupportToPairedCompletion_eta`
- `RealizationBoundaries.finiteSupport_inclusion_not_surjective`

