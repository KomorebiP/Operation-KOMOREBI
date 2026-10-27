# Proof ledger — v0.32

Evidence is the completed direct source replay and AxiomAudit; see RESULT.json.

## OperatorNormPolynomial.lean

- `def Komorebi.StrongArtin.NonsemisimpleNorm.normPolynomial` (line 14)
- `def Komorebi.StrongArtin.NonsemisimpleNorm.operatorNorm` (line 17)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.normPolynomial_mul_X_sub_one` (line 20)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.aeval_normPolynomial` (line 24)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.operatorNorm_zero` (line 28)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.operatorNorm_succ` (line 31)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.normPolynomial_primePower` (line 36)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.operatorNorm_primePower` (line 45)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.operatorNorm_prime` (line 51)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.normPolynomial_mixed_degree` (line 57)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.operatorNorm_mixed_degree` (line 74)

## NilpotentPolynomialImage.lean

- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.end_unit_bijective` (line 10)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.aeval_isUnit_of_primary` (line 23)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.aeval_range_ker_of_root_factor` (line 42)

## PrimaryBlockNorm.lean

- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.normPolynomial_eval` (line 12)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.normPolynomial_eval_one` (line 16)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.normPolynomial_eval_zero_of_root` (line 20)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.normPolynomial_eval_ne_zero` (line 26)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.normPolynomial_simple_root_factor` (line 36)
- `def Komorebi.StrongArtin.NonsemisimpleNorm.resonanceExponent` (line 56)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.normPolynomial_exact_root_factor` (line 60)
- `theorem Komorebi.StrongArtin.NonsemisimpleNorm.primary_norm_range_ker` (line 85)

## NonsemisimpleFrobeniusLifting.lean

- `structure Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates` (line 13)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates.conjugate_pow_coordinates` (line 22)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates.norm_coordinates` (line 32)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates.prescribed_power_iff_operator_image` (line 41)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates.prescribed_primePower_iff` (line 54)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates.prescribed_primary_power_iff` (line 62)
- `theorem Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates.prescribed_primePower_gauge_iff` (line 74)

## GeneralDualMatrixNorm.lean

- `abbrev Komorebi.StrongArtin.SquareZeroH2.GeneralDualMatrix.D` (line 11)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.GeneralDualMatrix.Dual` (line 12)
- `def Komorebi.StrongArtin.SquareZeroH2.GeneralDualMatrix.coordinates` (line 14)
- `def Komorebi.StrongArtin.SquareZeroH2.GeneralDualMatrix.upperFrobenius` (line 27)
- `def Komorebi.StrongArtin.SquareZeroH2.GeneralDualMatrix.conjugationOperator` (line 30)
- `theorem Komorebi.StrongArtin.SquareZeroH2.GeneralDualMatrix.conjugation_coordinates` (line 35)
- `def Komorebi.StrongArtin.SquareZeroH2.GeneralDualMatrix.linearModel` (line 50)
- `theorem Komorebi.StrongArtin.SquareZeroH2.GeneralDualMatrix.matrix_prescribed_primePower_iff` (line 57)

## UnipotentNormExamples.lean

- `abbrev Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.k` (line 11)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.n` (line 12)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.Mat` (line 13)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.D` (line 14)
- `def Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.F` (line 16)
- `def Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.upper` (line 22)
- `def Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.lower` (line 23)
- `def Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.diagonalError` (line 24)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.T` (line 25)
- `theorem Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.nilpotent_square_apply` (line 28)
- `theorem Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.nilpotent_cube_zero` (line 39)
- `theorem Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.nilpotent_square_nonzero` (line 49)
- `theorem Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.norm_three_apply` (line 56)
- `theorem Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.norm_image_iff` (line 60)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.upperF` (line 70)
- `def Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.target` (line 72)
- `theorem Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.target_residue` (line 75)
- `theorem Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.target_mismatch` (line 80)
- `theorem Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.actual_unipotent_cube_lift_iff` (line 87)
- `theorem Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.nonzero_upper_mismatch_lifts` (line 97)
- `theorem Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples.diagonal_mismatch_does_not_lift` (line 103)

## Scope

37 theorems, 12 definitions, 8 abbreviations, 1 structure, 497 additive source lines.
58 explicitly named constants are audited; generated structure projections are not separately counted.
21 unchanged project dependencies are not new. The pinned Mathlib cache is reused.
