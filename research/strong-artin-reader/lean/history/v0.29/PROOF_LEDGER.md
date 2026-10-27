# Proof ledger — v0.29

Evidence: Lean-check status is recorded in RESULT.json. These statements concern explicit continuous inhomogeneous cochain quotients and actual square-zero representation lifts. No arithmetic vanishing or Strong Artin result is claimed.

## ContinuousGaugeCoboundaries.lean

Construct actual continuous degree-zero boundaries, global/local H1 quotient modules, and the descended restriction map.

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localGaugeCoboundary` (source line 13)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localGaugeCoboundary_apply` (source line 43)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.globalGaugeCoboundary` (source line 48)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.restrict_globalGaugeCoboundary` (source line 75)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.Datum.GaugeGlobalH1` (source line 82)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.Datum.GaugeLocalH1` (source line 86)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.gaugeRestrictionH1` (source line 90)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.gaugeRestrictionH1_mk` (source line 101)

## ContinuousLocalGaugeComplex.lean

Add the local zero-cochains to the degree-two boundary; compute vanishing and the surjective strict-to-gauge quotient map.

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localGaugePair` (source line 14)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localGaugeDifferential` (source line 31)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.Datum.LocalGaugeH2` (source line 37)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localGaugeClass` (source line 41)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localGaugeClass_zero_iff` (source line 46)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.strict_boundary_is_gauge_boundary` (source line 70)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.strictToGaugeH2` (source line 79)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.strictToGaugeH2_surjective` (source line 89)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.strict_zero_implies_gauge_zero` (source line 96)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localGaugeClass_eq_of_boundary` (source line 107)

## KernelGaugeCorrection.lean

Prove exact kernel-unit conjugation formulas and recover a continuous correcting primitive from any actual lift.

- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.kernelUnit_add` (source line 10)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.every_residual_one_unit_is_kernelUnit` (source line 17)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.kernel_conjugation_correctedLift` (source line 24)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.kernel_conjugation_at_local_iff` (source line 38)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuous_lift_has_correcting_primitive` (source line 51)

## ContinuousGaugeLiftCriterion.lean

Construct the distinguished class from actual local lifts and prove the necessary-and-sufficient continuous representation lifting criterion, including the section-free form.

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localConjugacyObstruction` (source line 14)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localConjugacyObstruction_zero_iff` (source line 20)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuous_local_conjugacy_lifts_iff` (source line 49)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.local_conjugacy_zero_implies_absolute_zero` (source line 75)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.strict_prescription_zero_implies_local_conjugacy_zero` (source line 84)
- `theorem Komorebi.StrongArtin.SquareZeroH2.continuous_local_conjugacy_lifts_iff_constructed_class_zero` (source line 102)

## LocalGaugeInvariance.lean

Prove equality of classes when prescribed local lifts are changed by arbitrary conjugators reducing to one.

- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localCorrection_kernel_conjugate` (source line 10)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localConjugacyObstruction_eq_of_kernel_conjugate` (source line 30)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localConjugacyObstruction_eq_of_residual_one_conjugate` (source line 55)

## ContinuousH1GluingObstruction.lean

Construct the cokernel on actual continuous H1 quotients, compute its zero criterion, prove primitive independence, and connect it to actual liftability.

- `abbrev Komorebi.StrongArtin.SquareZeroH2.Datum.LocalH1GluingCokernel` (source line 13)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.h1GluingProjection` (source line 17)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.h1GluingProjection_zero_iff` (source line 23)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.h1GluingProjection_restrict` (source line 51)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.h1GluingObstruction` (source line 58)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localGauge_zero_iff_h1Gluing_zero` (source line 65)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.h1GluingObstruction_independent_primitive` (source line 96)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localGauge_zero_of_surjective_h1_restriction` (source line 117)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.local_conjugacy_lifts_iff_h1_gluing_zero` (source line 128)

## LocalGaugeExactSequence.lean

Construct the injection from the H1 localization cokernel into the local-gauge degree-two group and prove its image equals the absolute-forgetful kernel.

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.zeroGlobalLocalPair` (source line 13)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localCocycleToGaugeH2` (source line 19)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localCocycleToGaugeH2_zero_iff` (source line 25)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localH1ToGaugeH2` (source line 38)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.h1GluingToGaugeH2` (source line 47)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.h1GluingToGaugeH2_projection` (source line 57)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.h1GluingProjection_surjective` (source line 63)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.h1GluingToGaugeH2_injective` (source line 69)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.gaugePairToAbsolute` (source line 79)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.gaugeForgetAbsolute` (source line 85)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.gaugeForgetAbsolute_localCocycle` (source line 95)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.h1Gluing_image_eq_absolute_kernel` (source line 101)

## LocalGaugeObstructionExamples.lean

Prove nonzero gauge obstruction for the Z/4 character triple; prove nonzero strict but zero gauge obstruction for the GL2(Z/9) matrix prescriptions.

- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.gaugeClass` (source line 21)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.gauge_obstruction_nonzero` (source line 25)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.absolute_zero_does_not_force_local_gauge_zero` (source line 34)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.actual_h1_localization_cokernel_class_nonzero` (source line 38)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.gaugeTestLoc` (source line 72)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.gaugeTestPrescribed` (source line 73)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.gaugeTestRho` (source line 74)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.matrixReduction_surjective` (source line 76)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.matrixReduction_squareZero` (source line 79)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.gaugeDatum` (source line 83)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.gaugeDatum_continuous` (source line 86)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.gaugeTestPrescribed_residue` (source line 90)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.strictGaugeTestClass` (source line 96)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.gaugeTestClass` (source line 101)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.strict_gauge_test_class_nonzero` (source line 106)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.gauge_test_class_zero` (source line 115)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.strict_nonzero_but_gauge_zero` (source line 128)

## Declaration scope

43 theorem declarations, 23 definitions, 4 abbreviations, 8 new source modules and 881 additive source lines. There are 70 explicitly named constants in the axiom audit. The 16 anonymous local instances supply discrete topologies only for finite examples. The general theorem does not discretize the source.

20 unchanged direct dependencies are replayed from source. Their bytes are checked against the exact v0.28 archive. The pinned Mathlib compiled cache is reused. This is self-review plus Lean checking, not an independent specialist review, a second kernel implementation, or a replay of all historical branches.
