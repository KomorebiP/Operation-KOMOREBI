# Proof ledger — v0.26

Evidence: all declarations listed below are checked as written in the fresh direct replay. Absolute H² uses Mathlib; the strict-relative degree-two quotient is explicitly defined. No arithmetic vanishing is claimed.

## SquareZeroKernelAction.lean

- `structure Komorebi.StrongArtin.SquareZeroH2.Datum`
- `abbrev Komorebi.StrongArtin.SquareZeroH2.Datum.Kernel`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.kernel_mul`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.same_residue_mul_kernel`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.kernel_mul_same_residue`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.inverse_same_residue`
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.conjugate`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.conjugate_val`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.conjugate_same_residue`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.conjugate_one`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.conjugate_mul`
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.action`
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.coefficientRep`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.action_val`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.action_eq_conjugate`

## RepresentationDefectTwoCocycle.lean

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.normalizedDefect`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.normalizedDefect_val`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.normalizedDefect_mul_lift`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.normalizedDefect_one_left`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.normalizedDefect_one_right`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.normalizedDefect_cocycle`
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.defectCocycle`
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.obstructionOf`
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.obstruction`

## RepresentationObstructionChoice.lean

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.liftDifference`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.liftDifference_mul`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.lift_eq_one_add_difference`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.normalizedDefect_change`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.obstructionOf_eq`

## RepresentationH2LiftingCriterion.lean

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.kernelUnit`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.kernelUnit_val`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.kernelUnit_residue`
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.correctedLift`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.correctedLift_val`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.correctedLift_residue`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.difference_corrected`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.normalizedDefect_corrected`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.obstruction_zero_iff_boundary`
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.liftFromPrimitive`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.liftFromPrimitive_apply`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.representation_lifts_iff_obstruction_zero`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.representation_lifts_of_H2_subsingleton`

## SurjectiveSquareZeroDatum.lean

- `theorem Komorebi.StrongArtin.SquareZeroH2.units_lift_across_square_zero`
- `def Komorebi.StrongArtin.SquareZeroH2.datumOfSurjective`
- `theorem Komorebi.StrongArtin.SquareZeroH2.lifts_iff_constructed_H2_class_zero`

## FixedRestrictionObstruction.lean

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.relativeOneCochains`
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.relativeTwoCocycles`
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.relativeDifferential`
- `abbrev Komorebi.StrongArtin.SquareZeroH2.Datum.RelativeH2`
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.relativeDefect`
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.relativeObstruction`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.relativeObstruction_zero_iff`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.fixed_restriction_lifts_iff_relativeObstruction_zero`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.relative_zero_implies_absolute_zero`

## MatrixSquareZeroObstruction.lean

- `theorem Komorebi.StrongArtin.SquareZeroH2.matrix_map_surjective`
- `theorem Komorebi.StrongArtin.SquareZeroH2.matrix_kernel_squareZero`
- `def Komorebi.StrongArtin.SquareZeroH2.matrixDatum`
- `theorem Komorebi.StrongArtin.SquareZeroH2.matrix_representation_lifts_iff_H2_zero`

## NonzeroRepresentationObstruction.lean

- `abbrev Komorebi.StrongArtin.SquareZeroH2.Example.G`
- `abbrev Komorebi.StrongArtin.SquareZeroH2.Example.A`
- `abbrev Komorebi.StrongArtin.SquareZeroH2.Example.B`
- `def Komorebi.StrongArtin.SquareZeroH2.Example.q`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Example.q_surjective`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Example.q_squareZero`
- `def Komorebi.StrongArtin.SquareZeroH2.Example.rho`
- `def Komorebi.StrongArtin.SquareZeroH2.Example.unitLifts`
- `def Komorebi.StrongArtin.SquareZeroH2.Example.datum`
- `def Komorebi.StrongArtin.SquareZeroH2.Example.generator`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Example.generator_order_relation`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Example.no_cube_one_above_four`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Example.no_representation_lift`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Example.obstruction_nonzero`
- `theorem Komorebi.StrongArtin.SquareZeroH2.Example.defect_at_wrap`

## RelativeObstructionNegativeControl.lean

- `abbrev Komorebi.StrongArtin.SquareZeroH2.RelativeExample.G`
- `abbrev Komorebi.StrongArtin.SquareZeroH2.RelativeExample.A`
- `abbrev Komorebi.StrongArtin.SquareZeroH2.RelativeExample.B`
- `def Komorebi.StrongArtin.SquareZeroH2.RelativeExample.q`
- `def Komorebi.StrongArtin.SquareZeroH2.RelativeExample.gen`
- `def Komorebi.StrongArtin.SquareZeroH2.RelativeExample.middle`
- `def Komorebi.StrongArtin.SquareZeroH2.RelativeExample.H`
- `def Komorebi.StrongArtin.SquareZeroH2.RelativeExample.chosen`
- `def Komorebi.StrongArtin.SquareZeroH2.RelativeExample.datum`
- `theorem Komorebi.StrongArtin.SquareZeroH2.RelativeExample.prescribed_subgroup_multiplicative`
- `theorem Komorebi.StrongArtin.SquareZeroH2.RelativeExample.every_unit_square_one`
- `theorem Komorebi.StrongArtin.SquareZeroH2.RelativeExample.absolute_obstruction_zero`
- `theorem Komorebi.StrongArtin.SquareZeroH2.RelativeExample.no_fixed_subgroup_lift`
- `theorem Komorebi.StrongArtin.SquareZeroH2.RelativeExample.relative_obstruction_nonzero`

## Scope of counts

49 theorem declarations, 29 definitions, 8 abbreviations, 1 structure, 783 additive source lines. The 87 named constants are individually printed in `audit/AxiomAudit.lean`. Constructor-generated constants are not counted separately. The single unchanged v0.25 dependency is not counted as new.

## Main proof obligations

The coefficient action is proved from the square-zero identity; the two-cocycle condition is proved from the actual multiplicativity defect; the obstruction class is proved invariant under replacement of unit lifts; vanishing produces a multiplicative lift of the original representation. The relative criterion requires a primitive zero on the subgroup. The examples prove that neither absolute nor relative vanishing can be omitted.
