# Proof ledger — v0.30

Evidence: all declarations below compiled in the fresh direct replay, with warnings as errors. All 68 explicitly named constants received axiom reports. This is a formalization of the stated local algebraic/profinite results, not an automorphy theorem.

## FrobeniusRestrictionNorm.lean

- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.kernelUnit_zero` (source line 9)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.kernelUnit_injective` (source line 14)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.unit_commute_kernelUnit` (source line 21)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.frobeniusNorm` (source line 28)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.frobeniusNorm_zero` (source line 31)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.frobeniusNorm_succ` (source line 34)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.kernel_perturbed_power` (source line 38)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.conjugate_kernel_perturbed_power` (source line 55)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.unitMismatch` (source line 74)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.unitMismatch_spec` (source line 77)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.local_power_lifting_iff_norm_image` (source line 84)

## ProfiniteCyclicGenerator.lean

- `abbrev Komorebi.StrongArtin.Procyclic.Integers` (source line 10)
- `abbrev Komorebi.StrongArtin.Procyclic.Zhat` (source line 11)
- `def Komorebi.StrongArtin.Procyclic.integerMap` (source line 13)
- `def Komorebi.StrongArtin.Procyclic.frobenius` (source line 16)
- `theorem Komorebi.StrongArtin.Procyclic.integerMap_one` (source line 18)
- `theorem Komorebi.StrongArtin.Procyclic.integerMap_dense` (source line 20)
- `def Komorebi.StrongArtin.Procyclic.integerPowers` (source line 24)
- `theorem Komorebi.StrongArtin.Procyclic.integerPowers_generator` (source line 29)
- `theorem Komorebi.StrongArtin.Procyclic.integerHom_ext` (source line 33)
- `def Komorebi.StrongArtin.Procyclic.fromFrobenius` (source line 43)
- `theorem Komorebi.StrongArtin.Procyclic.fromFrobenius_integer` (source line 46)
- `theorem Komorebi.StrongArtin.Procyclic.fromFrobenius_frobenius` (source line 51)
- `theorem Komorebi.StrongArtin.Procyclic.hom_ext` (source line 56)
- `def Komorebi.StrongArtin.Procyclic.frobeniusEquiv` (source line 66)

## ProcyclicFrobeniusLifting.lean

- `theorem Komorebi.StrongArtin.Procyclic.fromFrobenius_naturality` (source line 7)
- `theorem Komorebi.StrongArtin.Procyclic.exists_unique_lift_with_frobenius` (source line 13)
- `theorem Komorebi.StrongArtin.Procyclic.exists_lift_of_surjective` (source line 24)
- `def Komorebi.StrongArtin.Procyclic.degreeMap` (source line 32)
- `theorem Komorebi.StrongArtin.Procyclic.degreeMap_frobenius` (source line 35)
- `theorem Komorebi.StrongArtin.Procyclic.degreeMap_one` (source line 38)
- `theorem Komorebi.StrongArtin.Procyclic.restrict_degreeMap` (source line 42)
- `theorem Komorebi.StrongArtin.Procyclic.conjugacy_iff_frobenius` (source line 48)
- `theorem Komorebi.StrongArtin.Procyclic.local_family_lifts_iff_frobenius_power_system` (source line 61)

## UnramifiedSquareZeroLifting.lean

- `def Komorebi.StrongArtin.Procyclic.unitReduction` (source line 14)
- `theorem Komorebi.StrongArtin.Procyclic.unitReduction_val` (source line 19)
- `theorem Komorebi.StrongArtin.Procyclic.unitReduction_surjective` (source line 23)
- `theorem Komorebi.StrongArtin.Procyclic.procyclic_representation_lifts` (source line 31)
- `theorem Komorebi.StrongArtin.Procyclic.procyclic_continuous_obstruction_zero` (source line 40)
- `theorem Komorebi.StrongArtin.Procyclic.unramified_pullback_lifts` (source line 54)
- `theorem Komorebi.StrongArtin.Procyclic.procyclic_matrix_representation_lifts` (source line 72)

## UnramifiedQuotientDescent.lean

- `theorem Komorebi.StrongArtin.Procyclic.factor_through_procyclic_of_kernel_trivial` (source line 11)
- `theorem Komorebi.StrongArtin.Procyclic.unramified_lift_preserving_inertia` (source line 33)

## UnramifiedGaugeObstruction.lean

- `theorem Komorebi.StrongArtin.Procyclic.local_gauge_obstruction_zero_iff_frobenius_system` (source line 14)
- `theorem Komorebi.StrongArtin.Procyclic.inertia_preserving_lift_in_obstruction_form` (source line 58)

## FrobeniusLocalizationCokernel.lean

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.frobeniusLocalization` (source line 10)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.frobeniusLocalization_apply` (source line 18)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.Datum.FrobeniusLocalizationCokernel` (source line 23)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.frobeniusMatchingClass` (source line 26)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.simultaneous_frobenius_matching_iff_class_zero` (source line 32)
- `theorem Komorebi.StrongArtin.Procyclic.gauge_obstruction_zero_iff_explicit_norm_class_zero` (source line 76)

## UnramifiedObstructionExamples.lean

- `def Komorebi.StrongArtin.Procyclic.Examples.toC3` (source line 16)
- `def Komorebi.StrongArtin.Procyclic.Examples.oldCharacter` (source line 19)
- `def Komorebi.StrongArtin.Procyclic.Examples.inflatedCharacter` (source line 22)
- `def Komorebi.StrongArtin.Procyclic.Examples.upperFrobenius` (source line 24)
- `def Komorebi.StrongArtin.Procyclic.Examples.liftedCharacter` (source line 26)
- `theorem Komorebi.StrongArtin.Procyclic.Examples.inflated_frobenius_value` (source line 29)
- `theorem Komorebi.StrongArtin.Procyclic.Examples.lifted_frobenius_value` (source line 35)
- `theorem Komorebi.StrongArtin.Procyclic.Examples.inflated_character_lifts` (source line 40)
- `theorem Komorebi.StrongArtin.Procyclic.Examples.inflated_continuous_obstruction_zero` (source line 48)
- `theorem Komorebi.StrongArtin.Procyclic.Examples.no_lift_through_original_C3` (source line 56)
- `theorem Komorebi.StrongArtin.Procyclic.Examples.upper_cube_is_ten` (source line 71)
- `theorem Komorebi.StrongArtin.Procyclic.Examples.upper_ninth_power_is_one` (source line 73)
- `theorem Komorebi.StrongArtin.Procyclic.Examples.residual_degree_three_trivial` (source line 76)
- `theorem Komorebi.StrongArtin.Procyclic.Examples.trivial_local_prescription_residue` (source line 86)
- `def Komorebi.StrongArtin.Procyclic.Examples.prescribedTrivialGaugeClass` (source line 92)
- `theorem Komorebi.StrongArtin.Procyclic.Examples.prescribed_degree_three_gauge_obstruction_nonzero` (source line 102)
- `theorem Komorebi.StrongArtin.Procyclic.Examples.prescribed_degree_three_norm_class_nonzero` (source line 117)

## Count and scope

48 theorem declarations, 17 definitions, 3 abbreviations, 8 source modules, 696 source lines. No new structures. Six local anonymous topology instances occur only for finite example types. No imported declaration or auto-generated constructor is counted as new.

22 unchanged direct dependencies are recompiled. The parent is retained byte-for-byte. One counterexample source is drawn unchanged from the nested v0.26 ancestor and authenticated along its exact archive chain.

Allowed axiom dependencies: `propext`, `Classical.choice`, `Quot.sound`. The pinned Mathlib compiled cache is reused.
