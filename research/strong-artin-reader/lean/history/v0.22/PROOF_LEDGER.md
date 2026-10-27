# Proof ledger — Strong Artin Lean v0.22

## Evidence label

Every theorem listed below is **Lean-checked as written** under the pinned Lean/mathlib environment. The results concern finite presentations, the naive cotangent complex, relation syzygies, and conditional comparison with a declared arithmetic Selmer obstruction space. No arithmetic Selmer comparison is asserted to exist.

## `PresentationObstructionExactSequence.lean`

Definitions:

- `relationDifferentialMap`
- `presentationObstructionDual`
- `toH1Cotangent`
- `relationSyzygies`
- `obstructionDualEquivH1_of_relationIndependent`

Checked theorems:

1. `cotangentComplex_comp_hom₁`
2. `toH1Cotangent_apply_val`
3. `toH1Cotangent_surjective`
4. `mem_relationSyzygies_iff_hom₁_eq_zero`
5. `toH1Cotangent_injective_of_relationIndependent`
6. `exact_syzygy_to_obstruction_to_h1`

### Mechanism

Mathlib's commutative square between relation differentials and the cotangent complex shows that a relation vector in the displayed Jacobian kernel maps to cotangent H1. Surjectivity of the conormal relation map gives surjectivity onto H1. The kernel is, by definition and direct computation, the conormal redundancy among the chosen relations.

## `PresentationJacobianCoordinates.lean`

Definitions:

- `relationJacobianEntry`
- `relationJacobianMatrix`

Checked theorems:

7. `relationDifferentialMap_single_apply`
8. `relationDifferentialMap_apply`
9. `mem_presentationObstructionDual_iff_jacobianTranspose`
10. `cotangentComplex_hom₁_coordinates`
11. `cotangentComplex_relation_coordinate`
12. `mem_presentationObstructionDual_iff_cotangentComplex_eq_zero`

### Mechanism

The conormal differential of each polynomial relation is expanded in the differential basis. Its coefficients are the evaluated partial derivatives. Linearity then gives the finite-support transpose-Jacobian formula for an arbitrary relation vector.

## `PresentationObstructionRank.lean`

Checked theorems:

13. `lift_rank_presentationObstructionDual`
14. `lift_rank_eq_of_relationIndependent`

### Mechanism

Rank-nullity is applied to the canonical surjection from the raw presentation kernel to cotangent H1. Universe lifts are retained explicitly because the relation and generator index types need not inhabit the same universe.

## `PresentationIntrinsicObstructionCapstone.lean`

Checked theorems:

15. `relationIndependent_of_toH1Cotangent_injective`
16. `toH1Cotangent_injective_iff_relationIndependent`
17. `relationSyzygies_eq_bot_iff_relationIndependent`
18. `intrinsic_obstruction_criterion`

### Mechanism

If the canonical map is injective, any conormal relation dependence gives an element of the raw kernel mapping to zero, hence must vanish. Conversely, injectivity of the conormal relation map makes the canonical H1 map injective. Together with its already-proved surjectivity, this gives the precise criterion for an intrinsic presentation obstruction.

## `RedundantRelationSyzygy.lean`

Checked theorems:

19. `relationSyzygies_ne_bot_iff_not_relationIndependent`
20. `duplicate_conormal_relations_give_nontrivial_syzygy`
21. `duplicate_conormal_relations_prevent_canonical_injectivity`

### Mechanism

Two distinct relation basis vectors with equal conormal images violate injectivity of the conormal relation map. The capstone criterion then forces a nonzero syzygy and failure of canonical identification with cotangent H1.

## `SelmerPresentationComparison.lean`

Structure:

- `Datum`

Definitions:

- `Datum.presentationToSelmer`
- `Datum.presentationObstructionEquivSelmer`

Checked theorems:

22. `Datum.presentationToSelmer_apply`
23. `Datum.presentationToSelmer_surjective`
24. `Datum.ker_presentationToSelmer`
25. `Datum.exact_syzygy_to_presentation_to_selmer`
26. `Datum.presentationToSelmer_injective_iff_relationIndependent`
27. `Datum.presentationObstructionEquivSelmer_apply`
28. `Datum.functional_vanishes_on_relationSyzygies`
29. `Datum.no_complete_arithmetic_detection_of_nonzero_syzygies`

### Mechanism

An externally supplied equivalence between cotangent H1 and the arithmetic Selmer obstruction space transports the canonical exact sequence. Any arithmetic functional factors through Selmer and therefore vanishes on relation syzygies. This proves that redundant presentation directions cannot be killed by genuine arithmetic auxiliary probes.

## Declaration and axiom audit

- theorem declarations: **29**;
- definitions: **8**;
- abbreviations: **1**;
- structures: **1**;
- instances: **0**;
- `sorry`: **0**;
- `admit`: **0**;
- custom `axiom`: **0**;
- custom `opaque`: **0**.

Axiom reports are confined to:

- `propext`;
- `Classical.choice`;
- `Quot.sound`.
