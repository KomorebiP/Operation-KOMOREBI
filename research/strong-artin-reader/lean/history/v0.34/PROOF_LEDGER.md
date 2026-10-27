# Proof ledger — v0.34

Evidence is the fresh compiler/axiom replay in RESULT.json. All hypotheses remain as written. Counts include helpers and examples.

## ZModSquareZeroLayer.lean

- `abbrev Komorebi.StrongArtin.MixedCharacteristic.Upper` (source line 12)
- `abbrev Komorebi.StrongArtin.MixedCharacteristic.Lower` (source line 14)
- `def Komorebi.StrongArtin.MixedCharacteristic.reduction` (source line 15)
- `def Komorebi.StrongArtin.MixedCharacteristic.residue` (source line 18)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.reduction_surjective` (source line 21)
- `def Komorebi.StrongArtin.MixedCharacteristic.layerIntegerMap` (source line 24)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.layerIntegerMap_period` (source line 29)
- `def Komorebi.StrongArtin.MixedCharacteristic.layerEmbedding` (source line 34)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.layerEmbedding_intCast` (source line 37)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.reduction_layerEmbedding` (source line 41)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.layerEmbedding_injective` (source line 46)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.mem_kernel_iff_layerEmbedding` (source line 58)
- `abbrev Komorebi.StrongArtin.MixedCharacteristic.Layer` (source line 70)
- `def Komorebi.StrongArtin.MixedCharacteristic.layerEquiv` (source line 72)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.layerEquiv_val` (source line 83)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.mul_layerEmbedding` (source line 86)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.layerEmbedding_mul` (source line 95)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.residue_layerEmbedding` (source line 99)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.reduction_squareZero` (source line 105)

## MixedCharacteristicMatrixKernel.lean

- `def Komorebi.StrongArtin.MixedCharacteristic.matrixDatum` (source line 11)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.matrix_reduction_surjective` (source line 19)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.lift_lower_frobenius` (source line 23)
- `def Komorebi.StrongArtin.MixedCharacteristic.matrixLayerEmbedding` (source line 29)
- `def Komorebi.StrongArtin.MixedCharacteristic.matrixKernelEmbedding` (source line 34)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.matrixKernelEmbedding_bijective` (source line 39)
- `def Komorebi.StrongArtin.MixedCharacteristic.matrixKernelEquiv` (source line 54)
- `def Komorebi.StrongArtin.MixedCharacteristic.kernelCoordinates` (source line 59)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.coordinates_embedding` (source line 63)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.embedding_coordinates` (source line 67)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.matrix_mul_layerEmbedding` (source line 73)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.matrix_layerEmbedding_mul` (source line 84)
- `def Komorebi.StrongArtin.MixedCharacteristic.residualFrobenius` (source line 92)
- `def Komorebi.StrongArtin.MixedCharacteristic.residualAdjoint` (source line 95)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.conjugate_embedding` (source line 102)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.conjugation_coordinates` (source line 111)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.residualAdjoint_eq_of_residualFrobenius_eq` (source line 119)

## MixedCharacteristicExplicitCoordinates.lean

- `theorem Komorebi.StrongArtin.MixedCharacteristic.layerEmbedding_natCast` (source line 8)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.layerEmbedding_from_val` (source line 12)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.layerEmbedding_value` (source line 18)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.layerEquiv_inverse_division` (source line 24)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.kernelCoordinates_division` (source line 33)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.no_additive_layer_retraction` (source line 44)

## MixedCharacteristicFrobenius.lean

- `def Komorebi.StrongArtin.MixedCharacteristic.linearModel` (source line 11)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.kernel_norm_coordinates` (source line 17)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.prescribed_power_iff` (source line 24)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.prescribed_primePower_iff` (source line 32)
- `def Komorebi.StrongArtin.MixedCharacteristic.primePowerLayerModel` (source line 40)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.primePower_layer_prescribed_root_iff` (source line 49)

## MixedCharacteristicSimultaneous.lean

- `theorem Komorebi.StrongArtin.MixedCharacteristic.matchingClass_zero_iff_localization` (source line 11)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.simultaneous_matching_iff_localization` (source line 20)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.primePower_matchingClass_zero_iff_pivot` (source line 33)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.primePower_layer_simultaneous_criterion` (source line 45)

## MixedCharacteristicNormExamples.lean

- `abbrev Komorebi.StrongArtin.MixedCharacteristic.Examples.k` (source line 9)
- `abbrev Komorebi.StrongArtin.MixedCharacteristic.Examples.n` (source line 10)
- `abbrev Komorebi.StrongArtin.MixedCharacteristic.Examples.Mat` (source line 11)
- `abbrev Komorebi.StrongArtin.MixedCharacteristic.Examples.UpperMat` (source line 12)
- `abbrev Komorebi.StrongArtin.MixedCharacteristic.Examples.D` (source line 13)
- `abbrev Komorebi.StrongArtin.MixedCharacteristic.Examples.E` (source line 14)
- `abbrev Komorebi.StrongArtin.MixedCharacteristic.Examples.embed` (source line 15)
- `def Komorebi.StrongArtin.MixedCharacteristic.Examples.F` (source line 16)
- `def Komorebi.StrongArtin.MixedCharacteristic.Examples.baseF` (source line 22)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.residual_F` (source line 28)
- `abbrev Komorebi.StrongArtin.MixedCharacteristic.Examples.T` (source line 32)
- `def Komorebi.StrongArtin.MixedCharacteristic.Examples.upper` (source line 34)
- `def Komorebi.StrongArtin.MixedCharacteristic.Examples.lower` (source line 36)
- `def Komorebi.StrongArtin.MixedCharacteristic.Examples.diagonalError` (source line 37)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.nilpotent_square_apply` (source line 38)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.nilpotent_cube_zero` (source line 49)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.norm_three_apply` (source line 58)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.norm_image_iff` (source line 62)
- `def Komorebi.StrongArtin.MixedCharacteristic.Examples.target` (source line 72)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.target_residue` (source line 74)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.target_mismatch` (source line 78)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.actual_cube_lift_iff` (source line 84)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.nonzero_mismatch_lifts` (source line 92)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.diagonal_mismatch_does_not_lift` (source line 96)
- `def Komorebi.StrongArtin.MixedCharacteristic.Examples.orderThreeLift` (source line 103)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.orderThreeLift_residue` (source line 110)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.orderThreeLift_cube` (source line 112)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.provisional_cube_not_one` (source line 114)

## MixedCharacteristicFamilyExamples.lean

- `def Komorebi.StrongArtin.MixedCharacteristic.Examples.familyDegree` (source line 7)
- `def Komorebi.StrongArtin.MixedCharacteristic.Examples.incompatibleTarget` (source line 9)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.incompatibleTarget_residue` (source line 11)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.each_incompatible_prescription_lifts` (source line 15)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.incompatible_no_shared_frobenius` (source line 21)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.incompatible_matching_class_nonzero` (source line 33)
- `def Komorebi.StrongArtin.MixedCharacteristic.Examples.compatibleTarget` (source line 40)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.compatibleTarget_residue` (source line 42)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.compatible_shared_frobenius` (source line 46)
- `theorem Komorebi.StrongArtin.MixedCharacteristic.Examples.compatible_matching_class_zero` (source line 54)

## Counts
7 new modules; {'abbrev': 11, 'def': 24, 'theorem': 55}; 603 source lines; 90 named constants audited. 37 unchanged direct dependencies are not new.
