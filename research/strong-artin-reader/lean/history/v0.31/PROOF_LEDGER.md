# Proof ledger — v0.31

All listed statements are checked as written. Arithmetic/global assertions remain outside the boundaries in RESEARCH_BOUNDARY.md.

## FrobeniusSingleRestriction.lean

- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.unitMismatch_kernel_perturbed` (source line 10)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.one_power_gauge_iff_strict` (source line 18)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.power_lifting_iff_norm_image` (source line 35)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.one_power_matching_iff_norm_image` (source line 54)

## FrobeniusSpectralNorm.lean

- `structure Komorebi.StrongArtin.SquareZeroH2.FrobeniusSpectralCoordinates` (source line 14)
- `def Komorebi.StrongArtin.SquareZeroH2.normWeight` (source line 22)
- `theorem Komorebi.StrongArtin.SquareZeroH2.normWeight_one` (source line 24)
- `theorem Komorebi.StrongArtin.SquareZeroH2.normWeight_of_ne_one` (source line 27)
- `theorem Komorebi.StrongArtin.SquareZeroH2.normWeight_zero_iff` (source line 32)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusSpectralCoordinates.conjugate_pow_coordinates` (source line 45)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusSpectralCoordinates.norm_coordinates` (source line 54)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusSpectralCoordinates.norm_image_iff` (source line 67)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusSpectralCoordinates.prescribed_power_iff` (source line 86)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusSpectralCoordinates.prescribed_power_lifts_of_nonresonance` (source line 93)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusSpectralCoordinates.no_prescribed_power_of_resonant_mismatch` (source line 102)

## PrimeDegreeFrobeniusNorm.lean

- `theorem Komorebi.StrongArtin.SquareZeroH2.normWeight_prime_eq` (source line 10)
- `theorem Komorebi.StrongArtin.SquareZeroH2.normWeight_prime_zero_iff` (source line 23)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusSpectralCoordinates.prime_norm_image_iff` (source line 34)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusSpectralCoordinates.prescribed_prime_power_iff` (source line 41)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusSpectralCoordinates.prescribed_prime_gauge_iff` (source line 49)

## DiagonalMatrixNormModel.lean

- `abbrev Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.Dual` (source line 10)
- `def Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.reduction` (source line 12)
- `theorem Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.reduction_squareZero` (source line 14)
- `def Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.datum` (source line 25)
- `def Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.kernelCoordinates` (source line 34)
- `def Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.scalarUnit` (source line 46)
- `def Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.diagonalFrobenius` (source line 50)
- `theorem Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.diagonal_conjugation_coordinates` (source line 56)
- `def Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.spectralModel` (source line 72)
- `theorem Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.matrix_prescribed_power_iff` (source line 79)
- `theorem Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.eigenvalue_ratio_one_iff` (source line 91)
- `theorem Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.matrix_prescribed_prime_power_iff` (source line 98)
- `theorem Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.matrix_prescribed_power_lifts_of_no_new_collisions` (source line 111)
- `theorem Komorebi.StrongArtin.SquareZeroH2.DiagonalModel.exists_prescribed_prime_power_obstruction` (source line 133)

## SimultaneousSpectralRestriction.lean

- `theorem Komorebi.StrongArtin.SquareZeroH2.normWeight_mul_one_sub` (source line 10)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusSpectralCoordinates.localization_coordinates` (source line 21)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusSpectralCoordinates.simultaneous_norm_image_iff` (source line 37)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusSpectralCoordinates.matchingClass_zero_iff` (source line 86)

## ProcyclicSpectralNormCapstone.lean

- `theorem Komorebi.StrongArtin.Procyclic.continuous_gauge_obstruction_zero_iff_spectral_compatibility` (source line 11)
- `theorem Komorebi.StrongArtin.Procyclic.continuous_prescribed_degree_lift_of_nonresonance` (source line 35)

## FrobeniusNormResonanceExamples.lean

- `abbrev Komorebi.StrongArtin.SquareZeroH2.NormExamples.k` (source line 12)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.NormExamples.n` (source line 13)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.NormExamples.D` (source line 14)
- `def Komorebi.StrongArtin.SquareZeroH2.NormExamples.lambda` (source line 16)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.NormExamples.F` (source line 17)
- `def Komorebi.StrongArtin.SquareZeroH2.NormExamples.offDiagonal` (source line 19)
- `def Komorebi.StrongArtin.SquareZeroH2.NormExamples.target` (source line 22)
- `theorem Komorebi.StrongArtin.SquareZeroH2.NormExamples.target_residue` (source line 25)
- `theorem Komorebi.StrongArtin.SquareZeroH2.NormExamples.target_mismatch` (source line 30)
- `theorem Komorebi.StrongArtin.SquareZeroH2.NormExamples.degree_unit_does_not_prevent_resonant_obstruction` (source line 35)
- `theorem Komorebi.StrongArtin.SquareZeroH2.NormExamples.characteristic_three_offDiagonal_cube_lifts` (source line 47)
- `theorem Komorebi.StrongArtin.SquareZeroH2.NormExamples.every_compatible_fifth_power_lifts` (source line 56)
- `def Komorebi.StrongArtin.SquareZeroH2.NormExamples.repeatedLambda` (source line 62)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.NormExamples.repeatedF` (source line 63)
- `theorem Komorebi.StrongArtin.SquareZeroH2.NormExamples.trace_zero_does_not_suffice_for_prime_power_lifting` (source line 66)
- `def Komorebi.StrongArtin.SquareZeroH2.NormExamples.familyDegree` (source line 80)
- `def Komorebi.StrongArtin.SquareZeroH2.NormExamples.diagonalError` (source line 81)
- `def Komorebi.StrongArtin.SquareZeroH2.NormExamples.familyError` (source line 83)
- `def Komorebi.StrongArtin.SquareZeroH2.NormExamples.familyTarget` (source line 84)
- `theorem Komorebi.StrongArtin.SquareZeroH2.NormExamples.family_residue` (source line 86)
- `theorem Komorebi.StrongArtin.SquareZeroH2.NormExamples.each_family_prescription_lifts` (source line 90)
- `theorem Komorebi.StrongArtin.SquareZeroH2.NormExamples.shared_family_matching_class_nonzero` (source line 97)
- `theorem Komorebi.StrongArtin.SquareZeroH2.NormExamples.individual_lifts_do_not_imply_simultaneous_local_gauge_matching` (source line 114)

## Scope

41 theorems, 15 definitions, 6 abbreviations, 1 structure, 668 lines. All 63 explicitly named constants receive axiom reports; constructor-generated fields are not separately counted. The 28 direct dependencies are not new. No novelty or global automorphy claim.
