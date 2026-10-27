# Proof ledger — v0.24

Evidence: exact Lean statements, with formal hypotheses retained. See RESULT.json for the fresh replay evidence.

## SyzygyCompatibleTarget

Image equals the dual-syzygy annihilator; exact correction criterion; corestricted surjectivity; incompatible-error certificate.

- `def` `Komorebi.StrongArtin.SyzygyCompatibleTarget.compatibleTarget`
- `theorem` `Komorebi.StrongArtin.SyzygyCompatibleTarget.mem_compatibleTarget`
- `theorem` `Komorebi.StrongArtin.SyzygyCompatibleTarget.range_eq_compatibleTarget_dualKernel`
- `theorem` `Komorebi.StrongArtin.SyzygyCompatibleTarget.range_eq_compatibleTarget_of_dualKernel_eq`
- `theorem` `Komorebi.StrongArtin.SyzygyCompatibleTarget.correction_exists_iff_compatible`
- `def` `Komorebi.StrongArtin.SyzygyCompatibleTarget.toCompatibleTarget`
- `theorem` `Komorebi.StrongArtin.SyzygyCompatibleTarget.toCompatibleTarget_surjective`
- `theorem` `Komorebi.StrongArtin.SyzygyCompatibleTarget.no_correction_of_syzygy_witness`

## SyzygyAugmentedImage

The actual v0.16 augmented map has dual kernel equal to the selected raw kernel, and therefore the prescribed compatible image.

- `theorem` `Komorebi.StrongArtin.SyzygyAugmentedImage.mem_augmented_dualKernel_iff`
- `theorem` `Komorebi.StrongArtin.SyzygyAugmentedImage.augmented_dualKernel_eq_syzygies`
- `theorem` `Komorebi.StrongArtin.SyzygyAugmentedImage.augmented_range_eq_compatibleTarget`
- `theorem` `Komorebi.StrongArtin.SyzygyAugmentedImage.auxiliary_correction_exists_iff`

## SplitTargetFiltration

An integral retraction reflects power divisibility. Compatible ambient values can be divided within the compatible target.

- `structure` `Komorebi.StrongArtin.SplitTargetFiltration.Retraction`
- `theorem` `Komorebi.StrongArtin.SplitTargetFiltration.Retraction.project_coe`
- `theorem` `Komorebi.StrongArtin.SplitTargetFiltration.Retraction.powDivisible_iff`
- `theorem` `Komorebi.StrongArtin.SplitTargetFiltration.Retraction.project_eq_zero_iff`
- `theorem` `Komorebi.StrongArtin.SplitTargetFiltration.Retraction.exists_compatible_divisor`

## SplitCompatibleHensel

Projected Taylor gain, exact ambient root, approximation tower, and the exact relation-kernel specialization under explicit splitting and compatibility.

- `theorem` `Komorebi.StrongArtin.SplitCompatibleHensel.projected_variableRemainder`
- `theorem` `Komorebi.StrongArtin.SplitCompatibleHensel.projected_remainder_raises_one`
- `theorem` `Komorebi.StrongArtin.SplitCompatibleHensel.exists_exact_solution_in_split_compatible_target`
- `theorem` `Komorebi.StrongArtin.SplitCompatibleHensel.exists_split_compatible_approximation_tower`
- `theorem` `Komorebi.StrongArtin.SplitCompatibleHensel.exists_exact_solution_of_split_relation_kernel`

## SyzygyBoundaryExamples

Exact nonlinear and nonsplit-filtration counterexamples, including proof that 2R in Z/4Z has no retraction.

- `def` `Komorebi.StrongArtin.SyzygyBoundaryExamples.redundantSystem`
- `def` `Komorebi.StrongArtin.SyzygyBoundaryExamples.redundantJacobian`
- `theorem` `Komorebi.StrongArtin.SyzygyBoundaryExamples.redundantSystem_exact_syzygy`
- `theorem` `Komorebi.StrongArtin.SyzygyBoundaryExamples.redundantSystem_taylor`
- `theorem` `Komorebi.StrongArtin.SyzygyBoundaryExamples.redundantJacobian_zero`
- `theorem` `Komorebi.StrongArtin.SyzygyBoundaryExamples.nonlinear_error_escapes_residual_target`
- `theorem` `Komorebi.StrongArtin.SyzygyBoundaryExamples.nonlinear_remainder_escapes_residual_target`
- `def` `Komorebi.StrongArtin.SyzygyBoundaryExamples.twoTorsion`
- `def` `Komorebi.StrongArtin.SyzygyBoundaryExamples.twoInTarget`
- `theorem` `Komorebi.StrongArtin.SyzygyBoundaryExamples.two_is_ambient_divisible`
- `theorem` `Komorebi.StrongArtin.SyzygyBoundaryExamples.two_not_internally_divisible`
- `theorem` `Komorebi.StrongArtin.SyzygyBoundaryExamples.twoTorsion_has_no_retraction`

## IntrinsicCompatibleTarget

Direct use of v0.23: extend raw evaluations, compute the full relation-map kernel, and identify the transpose image with the syzygy annihilator.

- `def` `Komorebi.StrongArtin.IntrinsicCompatibleTarget.ambientRelationSyzygies`
- `def` `Komorebi.StrongArtin.IntrinsicCompatibleTarget.extendedRawEvaluation`
- `theorem` `Komorebi.StrongArtin.IntrinsicCompatibleTarget.extendedRawEvaluation_coe`
- `def` `Komorebi.StrongArtin.IntrinsicCompatibleTarget.relationMapWithAuxiliaries`
- `theorem` `Komorebi.StrongArtin.IntrinsicCompatibleTarget.ker_relationMapWithAuxiliaries`
- `theorem` `Komorebi.StrongArtin.IntrinsicCompatibleTarget.range_augmentedTranspose_eq_compatible`
- `theorem` `Komorebi.StrongArtin.IntrinsicCompatibleTarget.exists_intrinsic_auxiliaries_with_exact_compatible_image`

## MovingRedundancyReduction

Invertible triangular elimination of known exact variable-dependent redundant equations; derivative block identity; transport of nonlinear Hensel solutions.

- `def` `Komorebi.StrongArtin.MovingRedundancyReduction.straighten`
- `def` `Komorebi.StrongArtin.MovingRedundancyReduction.redundantGraph`
- `theorem` `Komorebi.StrongArtin.MovingRedundancyReduction.straighten_redundantGraph`
- `theorem` `Komorebi.StrongArtin.MovingRedundancyReduction.redundantGraph_eq_zero_iff`
- `theorem` `Komorebi.StrongArtin.MovingRedundancyReduction.straighten_derivative_blocks`
- `theorem` `Komorebi.StrongArtin.MovingRedundancyReduction.ker_graph_derivative`
- `theorem` `Komorebi.StrongArtin.MovingRedundancyReduction.exists_exact_solution_with_moving_redundancy`

## Mathematical novelty boundary

The annihilator identity is standard algebraic duality already available in Mathlib. The Hensel result composes the verified v0.19 mechanism with a precise split-target comparison. This release does not establish historical novelty of these algebraic statements or an unconditional new Langlands case.
