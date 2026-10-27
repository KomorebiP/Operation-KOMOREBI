# Proof ledger — v0.33

Evidence: source replay and axiom audit in RESULT.json. All statements are at the scopes spelled out in RESEARCH_BOUNDARY.md. No arithmetic vanishing or novelty is claimed.

## SimultaneousPowerFiltration.lean

- `def Komorebi.StrongArtin.SimultaneousNorm.PowerFamilySolvable` (source line 12)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.pow_difference_apply` (source line 14)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.pow_succ_apply` (source line 18)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.powerFamily_iff_pivot` (source line 24)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.powerFamily_individually` (source line 48)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.not_powerFamily_of_pivot_difference` (source line 55)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.powerFamily_empty` (source line 64)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.exists_least_exponent` (source line 69)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.powerFamily_iff_pivot_pairs` (source line 81)

## SimultaneousOperatorNorm.lean

- `def Komorebi.StrongArtin.SimultaneousNorm.LocalizationSolvable` (source line 10)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.operatorNorm_mul_one_sub` (source line 14)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.norm_gauge_factor` (source line 18)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.localization_iff_factored` (source line 25)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.localization_iff_individual_of_one_sub_surjective` (source line 33)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.primePower_localization_iff` (source line 46)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.primePower_localization_iff_pivot` (source line 66)

## SimultaneousPrimaryNorm.lean

- `theorem Komorebi.StrongArtin.SimultaneousNorm.one_sub_surjective_of_primary_ne_one` (source line 12)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.simultaneous_primary_ne_one_iff` (source line 21)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.unipotent_norm_unit` (source line 33)
- `def Komorebi.StrongArtin.SimultaneousNorm.unipotentNormalizer` (source line 42)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.unipotentNormalizer_val` (source line 45)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.mixed_norm_factor_left` (source line 51)
- `def Komorebi.StrongArtin.SimultaneousNorm.normalizedUnipotentErrors` (source line 61)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.unipotent_localization_iff_powerFamily` (source line 66)
- `theorem Komorebi.StrongArtin.SimultaneousNorm.unipotent_localization_iff_pivot` (source line 102)

## SimultaneousFrobeniusCriterion.lean

- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates.matchingClass_zero_iff_linear_localization` (source line 14)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates.simultaneous_matching_iff_linear_localization` (source line 39)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates.primePower_matchingClass_zero_iff_pivot` (source line 49)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates.unipotent_matchingClass_zero_iff_pivot` (source line 63)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates.primary_ne_one_matchingClass_zero_iff` (source line 79)

## ContinuousSimultaneousNormCapstone.lean

- `theorem Komorebi.StrongArtin.Procyclic.continuous_primePower_gauge_zero_iff_pivot` (source line 13)
- `theorem Komorebi.StrongArtin.Procyclic.continuous_unipotent_gauge_zero_iff_pivot` (source line 39)

## SimultaneousUnipotentExamples.lean

- `def Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.exponent` (source line 11)
- `def Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.degree` (source line 13)
- `theorem Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.least_degree` (source line 14)
- `theorem Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.linear_family_iff` (source line 19)
- `def Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.familyTarget` (source line 44)
- `theorem Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.familyTarget_residue` (source line 47)
- `theorem Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.familyTarget_mismatch` (source line 53)
- `theorem Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.actual_family_class_zero_iff` (source line 62)
- `def Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.incompatibleErrors` (source line 71)
- `def Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.compatibleErrors` (source line 73)
- `theorem Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.incompatible_each_prescription_lifts` (source line 74)
- `theorem Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.incompatible_matching_class_nonzero` (source line 85)
- `theorem Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.incompatible_no_shared_frobenius` (source line 94)
- `theorem Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.compatible_matching_class_zero` (source line 101)
- `theorem Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples.compatible_shared_frobenius_exists` (source line 107)

## Counts

6 source modules, 38 theorem declarations, 9 definitions, 573 source lines. All 47 explicitly named constants receive axiom reports. The 38 unchanged direct dependencies are not new. The pinned Mathlib cache is reused.
