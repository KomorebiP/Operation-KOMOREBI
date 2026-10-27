# Proof ledger — v0.27

Evidence: all statements listed below are Lean-checked as written in the fresh direct replay. No new Strong Artin or arithmetic local-condition theorem is asserted.

## ContinuousSquareZeroData.lean

Actual continuity of the induced action, defect, change cochain and corrected lift; construct sections from discrete residual values, not by a discontinuous pointwise normalization on the source.

- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuous_kernel_action` (source line 17)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuous_normalizedDefect` (source line 23)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuous_liftDifference` (source line 34)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuous_correctedLift` (source line 43)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuous_liftFromPrimitive` (source line 48)
- `def Komorebi.StrongArtin.SquareZeroH2.normalizedUnitSection` (source line 59)
- `theorem Komorebi.StrongArtin.SquareZeroH2.normalizedUnitSection_one` (source line 66)
- `theorem Komorebi.StrongArtin.SquareZeroH2.normalizedUnitSection_residue` (source line 73)
- `def Komorebi.StrongArtin.SquareZeroH2.continuousSectionDatum` (source line 82)
- `theorem Komorebi.StrongArtin.SquareZeroH2.continuousSectionDatum_continuous_lift` (source line 92)

## ContinuousObstructionCochains.lean

Build explicit continuous inhomogeneous C1, Z2, differential, H2 quotient and distinguished class; zero iff a continuous primitive exists; change-of-continuous-section independence.

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.continuousOneCochains` (source line 13)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.continuousTwoCocycles` (source line 20)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.continuousDifferential` (source line 27)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.Datum.ContinuousH2` (source line 53)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.continuousDefectOf` (source line 56)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.continuousObstructionOf` (source line 60)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.continuousObstruction` (source line 64)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuousObstruction_zero_iff` (source line 67)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuousObstructionOf_eq` (source line 89)

## ContinuousRepresentationLifting.lean

Original representation has a continuous lift iff its constructed continuous class is zero. Compare vanishing with ordinary H2 in the correct direction and with equivalence only for discrete source.

- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuous_representation_lifts_iff` (source line 11)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuous_zero_implies_ordinary_zero` (source line 34)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuous_zero_iff_ordinary_zero_of_discrete_source` (source line 41)
- `theorem Komorebi.StrongArtin.SquareZeroH2.continuous_lifts_iff_constructed_obstruction_zero` (source line 59)

## ContinuousFixedRestriction.lean

Continuous degree-two kernel-of-restriction quotient; strict fixed-subgroup lift iff its class vanishes; relative zero implies absolute zero.

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.continuousRelativeOneCochains` (source line 14)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.continuousRelativeTwoCocycles` (source line 23)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.continuousRelativeDifferential` (source line 35)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.Datum.ContinuousRelativeH2` (source line 45)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.continuousRelativeDefect` (source line 48)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.continuousRelativeObstruction` (source line 57)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuousRelativeObstruction_zero_iff` (source line 61)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuous_fixed_restriction_lifts_iff` (source line 81)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuous_relative_zero_implies_absolute_zero` (source line 114)

## ClopenPrescribedSection.lean

Construct a continuous provisional section matching a given continuous subgroup representation on a clopen subgroup, and prove the resulting section-free relative lifting criterion.

- `def Komorebi.StrongArtin.SquareZeroH2.prescribedSection` (source line 14)
- `theorem Komorebi.StrongArtin.SquareZeroH2.prescribedSection_on_subgroup` (source line 22)
- `theorem Komorebi.StrongArtin.SquareZeroH2.prescribedSection_continuous` (source line 30)
- `def Komorebi.StrongArtin.SquareZeroH2.prescribedContinuousDatum` (source line 56)
- `theorem Komorebi.StrongArtin.SquareZeroH2.prescribedContinuousDatum_subgroup_multiplicative` (source line 76)
- `theorem Komorebi.StrongArtin.SquareZeroH2.continuous_prescribed_subgroup_lifts_iff` (source line 100)

## FiniteTwoCocycleAveraging.lean

Sum the actual two-cocycle equation; divide by the group order to construct a primitive. Also construct H1 primitives for subgroup adjustment.

- `theorem Komorebi.StrongArtin.FiniteCohomologyAveraging.twoCocycle_sum_identity` (source line 14)
- `theorem Komorebi.StrongArtin.FiniteCohomologyAveraging.exists_twoCocycle_primitive` (source line 27)
- `theorem Komorebi.StrongArtin.FiniteCohomologyAveraging.exists_oneCocycle_primitive` (source line 41)

## FiniteQuotientObstructionVanishing.lean

A coefficient-ring group-order unit acts invertibly on the actual kernel. Prove distinguished H2 vanishing and a continuous lift through the same finite quotient; specialize to matrices.

- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.kernel_nsmul_bijective_of_isUnit` (source line 16)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.obstruction_zero_of_groupOrder_isUnit` (source line 37)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.representation_lifts_of_groupOrder_isUnit` (source line 45)
- `theorem Komorebi.StrongArtin.SquareZeroH2.continuous_representation_lifts_through_finite_quotient` (source line 54)
- `theorem Komorebi.StrongArtin.SquareZeroH2.continuous_matrix_representation_lifts_through_finite_quotient` (source line 68)

## FiniteRelativeObstructionVanishing.lean

Adjust the averaged absolute primitive using H1 averaging on the subgroup so that the correction vanishes there exactly. Prove actual relative vanishing under order hypotheses.

- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.relative_primitive_of_groupOrders_isUnit` (source line 13)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.relativeObstruction_zero_of_groupOrders_isUnit` (source line 50)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.fixed_restriction_lifts_of_groupOrders_isUnit` (source line 57)

## ContinuousFiniteImageCapstone.lean

Choose the actual residual image as quotient and preserve exact kernel. Construct sections for open subgroups. Preserve a finite-subgroup prescription when it factors through the given quotient.

- `theorem Komorebi.StrongArtin.SquareZeroH2.continuous_lift_of_finite_residual_image_order_isUnit` (source line 14)
- `theorem Komorebi.StrongArtin.SquareZeroH2.continuous_obstruction_zero_of_finite_residual_image_order_isUnit` (source line 46)
- `theorem Komorebi.StrongArtin.SquareZeroH2.open_subgroup_prescription_has_continuous_section` (source line 58)
- `theorem Komorebi.StrongArtin.SquareZeroH2.continuous_finite_quotient_lift_preserving_subgroup` (source line 79)

## CompactSourceLifting.lean

Prove finite image from compactness plus discreteness, then construct a continuous same-kernel lift under the actual image-order condition.

- `theorem Komorebi.StrongArtin.SquareZeroH2.continuous_discrete_representation_finite_range` (source line 13)
- `theorem Komorebi.StrongArtin.SquareZeroH2.compact_source_lift_of_image_order_isUnit` (source line 20)

## ContinuousObstructionExamples.lean

Kernel-checked positive and negative controls, including a provably nondiscrete compact source; all C2 rank-two representations mod 3 lift mod 9; inherited obstruction failures persist in continuous theory.

- `abbrev Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.Q` (source line 14)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.ProductSource` (source line 15)
- `def Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.quotientLabel` (source line 17)
- `theorem Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.quotientLabel_continuous` (source line 22)
- `def Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.q` (source line 24)
- `theorem Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.q_surjective` (source line 26)
- `theorem Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.q_squareZero` (source line 28)
- `def Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.signRepresentation` (source line 30)
- `theorem Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.quotient_order_isUnit` (source line 35)
- `theorem Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.infinite_product_source_has_continuous_lift` (source line 41)
- `theorem Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.all_C2_matrix_representations_lift` (source line 49)
- `theorem Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.continuous_absolute_obstruction_nonzero` (source line 61)
- `theorem Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.continuous_absolute_zero_but_fixed_subgroup_nonzero` (source line 67)
- `theorem Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.productSource_compact` (source line 81)
- `theorem Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.productSource_not_discrete` (source line 83)
- `theorem Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.product_residual_representation_continuous` (source line 89)
- `theorem Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples.product_continuous_obstruction_zero` (source line 93)

## Counts and evidence

50 theorem declarations, 18 definitions, 4 abbreviations, 2 local anonymous topology instances, 965 new source lines. All 72 explicitly named constants have axiom reports. Constructor-generated constants are not separately counted.

The direct replay recompiles 10 unchanged dependencies and 11 new modules, followed by AxiomAudit.lean. Allowed axioms: propext, Classical.choice, Quot.sound. Pinned Mathlib object cache reused. No all-historical replay or independent kernel claimed.
