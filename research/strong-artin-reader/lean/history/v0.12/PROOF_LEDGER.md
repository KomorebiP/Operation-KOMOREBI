# v0.12 proof ledger

All entries below are checked in Lean 4.34.0-rc2 with the pinned mathlib revision and warnings as errors.

## New module: `CyclicTransverseObstruction.lean`

- `blockJacobian`
- `exists_block_correction_iff_exists_cyclic`
- `exists_block_correction_iff_cyclic_residual_zero`
- `blockJacobian_surjective_iff_cyclic_surjective`
- `obstructionClass`
- `obstructionClass_eq_zero_iff_mem_range`
- `obstructionClass_eq_zero_iff_exists_correction`
- `cyclicCokerProjection`
- `cyclicCokerProjection_surjective`
- `ker_cyclicCokerProjection_eq_range_blockJacobian`
- `blockObstruction_eq_zero_iff_cyclicObstruction_eq_zero`
- `quotientPrime_blockObstruction_eq_zero_iff_cyclicResidual_zero`
- `blockCokerEquivCyclicCoker`
- `blockCokerEquivCyclicOutputOfZero`
- `finrank_blockCoker_eq_finrank_cyclicCoker`
- `finrank_blockCoker_eq_one_of_scalar_cyclic`
- `derivative_defectPolynomial_zmod_eq_zero`

Representative axiom audits are restricted to the ordinary Lean/Mathlib foundations `propext`, `Classical.choice`, and `Quot.sound` (some theorems use a subset).

## New module: `ProjectorProbeSurjectivity.lean`

- `probeEvalMap`
- `probeEvalMap_injective_of_separates`
- `dual_probeMap_surjective_of_separates`
- `every_dual_functional_factors_through_probes`
- `dual_probeMap_surjective_of_joint_kernel_zero`
- `quotientProbe`
- `quotientProbe_separates_of_kernel_le_defect`
- `dual_quotientProbe_surjective_of_kernel_le_defect`
- `every_transverse_dual_factors_through_probes`

## New module: `CyclicRelativeProbeObstruction.lean`

- `transverseProbeCorrectionMap`
- `transverseProbeCorrectionMap_surjective`
- `full_obstruction_eq_zero_iff_cyclic_residual_zero_of_transverse_probes`
- `full_obstruction_finrank_eq_one_of_transverse_probes`
