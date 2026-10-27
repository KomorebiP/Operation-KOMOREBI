# Theorem index — v0.2.0

156 explicit named theorem declarations across 20 modules.

The count includes structural and auxiliary lemmas. It does not count definitions, generated declarations, imported theorems, or novel research results. Every listed theorem is requested in `checks/AxiomAudit.lean`.

## Towers

- `KomorebiSpace.Tower.PreHom.ext` — [Towers.lean, line 31](../KomorebiSpace/Towers.lean#L31)
- `KomorebiSpace.Tower.PreHom.id_comp` — [Towers.lean, line 43](../KomorebiSpace/Towers.lean#L43)
- `KomorebiSpace.Tower.PreHom.comp_id` — [Towers.lean, line 45](../KomorebiSpace/Towers.lean#L45)
- `KomorebiSpace.Tower.PreHom.comp_assoc` — [Towers.lean, line 47](../KomorebiSpace/Towers.lean#L47)
- `KomorebiSpace.Tower.PreHom.exact_id` — [Towers.lean, line 51](../KomorebiSpace/Towers.lean#L51)
- `KomorebiSpace.Tower.PreHom.exact_comp` — [Towers.lean, line 54](../KomorebiSpace/Towers.lean#L54)
- `KomorebiSpace.Tower.PreHom.exact_iff_defect_zero` — [Towers.lean, line 67](../KomorebiSpace/Towers.lean#L67)
- `KomorebiSpace.Tower.PreHom.defect_id` — [Towers.lean, line 71](../KomorebiSpace/Towers.lean#L71)
- `KomorebiSpace.Tower.PreHom.defect_comp` — [Towers.lean, line 75](../KomorebiSpace/Towers.lean#L75)
- `KomorebiSpace.Tower.PreHom.exact_zero` — [Towers.lean, line 84](../KomorebiSpace/Towers.lean#L84)
- `KomorebiSpace.Tower.PreHom.defect_zero` — [Towers.lean, line 87](../KomorebiSpace/Towers.lean#L87)
- `KomorebiSpace.Tower.ExactHom.ext` — [Towers.lean, line 100](../KomorebiSpace/Towers.lean#L100)

## Squares

- `KomorebiSpace.Squares.zero_iff` — [Squares.lean, line 16](../KomorebiSpace/Squares.lean#L16)
- `KomorebiSpace.Squares.horizontal` — [Squares.lean, line 21](../KomorebiSpace/Squares.lean#L21)
- `KomorebiSpace.Squares.vertical` — [Squares.lean, line 30](../KomorebiSpace/Squares.lean#L30)
- `KomorebiSpace.Squares.horizontal_flat` — [Squares.lean, line 38](../KomorebiSpace/Squares.lean#L38)
- `KomorebiSpace.Squares.vertical_flat` — [Squares.lean, line 45](../KomorebiSpace/Squares.lean#L45)

## Realization

- `KomorebiSpace.Resolution.Point.ext` — [Realization.lean, line 28](../KomorebiSpace/Realization.lean#L28)
- `KomorebiSpace.Resolution.Map.onLimit_apply` — [Realization.lean, line 61](../KomorebiSpace/Realization.lean#L61)
- `KomorebiSpace.Resolution.Map.onLimit_id` — [Realization.lean, line 64](../KomorebiSpace/Realization.lean#L64)
- `KomorebiSpace.Resolution.Map.onLimit_comp` — [Realization.lean, line 66](../KomorebiSpace/Realization.lean#L66)
- `KomorebiSpace.Resolution.Map.onLimit_unique` — [Realization.lean, line 70](../KomorebiSpace/Realization.lean#L70)
- `KomorebiSpace.Resolution.Cone.lift_coordinate` — [Realization.lean, line 87](../KomorebiSpace/Realization.lean#L87)
- `KomorebiSpace.Resolution.Cone.lift_unique` — [Realization.lean, line 90](../KomorebiSpace/Realization.lean#L90)
- `KomorebiSpace.Resolution.Cone.exists_unique_lift` — [Realization.lean, line 95](../KomorebiSpace/Realization.lean#L95)
- `KomorebiSpace.Resolution.realize_coordinate` — [Realization.lean, line 106](../KomorebiSpace/Realization.lean#L106)

## Cofinal

- `KomorebiSpace.Resolution.pickIndex_spec` — [Cofinal.lean, line 31](../KomorebiSpace/Cofinal.lean#L31)
- `KomorebiSpace.Resolution.recoveredCoordinate_eq` — [Cofinal.lean, line 40](../KomorebiSpace/Cofinal.lean#L40)
- `KomorebiSpace.Resolution.extend_sample` — [Cofinal.lean, line 76](../KomorebiSpace/Cofinal.lean#L76)
- `KomorebiSpace.Resolution.sample_extend` — [Cofinal.lean, line 83](../KomorebiSpace/Cofinal.lean#L83)
- `KomorebiSpace.Resolution.sample_injective` — [Cofinal.lean, line 102](../KomorebiSpace/Cofinal.lean#L102)
- `KomorebiSpace.Resolution.double_monotone` — [Cofinal.lean, line 106](../KomorebiSpace/Cofinal.lean#L106)
- `KomorebiSpace.Resolution.double_unbounded` — [Cofinal.lean, line 109](../KomorebiSpace/Cofinal.lean#L109)

## Correction

- `KomorebiSpace.CorrectionProblem.obstruction_zero_iff` — [Correction.lean, line 34](../KomorebiSpace/Correction.lean#L34)
- `KomorebiSpace.CorrectionProblem.flatten_iff` — [Correction.lean, line 42](../KomorebiSpace/Correction.lean#L42)
- `KomorebiSpace.CorrectionProblem.obstruction_invariant` — [Correction.lean, line 56](../KomorebiSpace/Correction.lean#L56)
- `KomorebiSpace.CorrectionProblem.nonzero_certificate` — [Correction.lean, line 64](../KomorebiSpace/Correction.lean#L64)
- `KomorebiSpace.CorrectionProblem.unrestricted_correction` — [Correction.lean, line 75](../KomorebiSpace/Correction.lean#L75)
- `KomorebiSpace.CorrectionProblem.rigid_one_obstructed` — [Correction.lean, line 82](../KomorebiSpace/Correction.lean#L82)

## TowerCorrection

- `KomorebiSpace.TowerCorrection.differential_apply` — [TowerCorrection.lean, line 36](../KomorebiSpace/TowerCorrection.lean#L36)
- `KomorebiSpace.TowerCorrection.exact_iff_differential_zero` — [TowerCorrection.lean, line 39](../KomorebiSpace/TowerCorrection.lean#L39)
- `KomorebiSpace.TowerCorrection.obstruction_zero_iff_exact` — [TowerCorrection.lean, line 56](../KomorebiSpace/TowerCorrection.lean#L56)
- `KomorebiSpace.TowerCorrection.obstruction_zero_iff_exactHom` — [TowerCorrection.lean, line 69](../KomorebiSpace/TowerCorrection.lean#L69)

## Cohomology

- `KomorebiSpace.ObstructionComplex.class_zero_iff` — [Cohomology.lean, line 38](../KomorebiSpace/Cohomology.lean#L38)
- `KomorebiSpace.ObstructionComplex.flatten_iff` — [Cohomology.lean, line 49](../KomorebiSpace/Cohomology.lean#L49)
- `KomorebiSpace.ObstructionComplex.correction_invariant` — [Cohomology.lean, line 62](../KomorebiSpace/Cohomology.lean#L62)
- `KomorebiSpace.ObstructionComplex.primary_defect_class_zero` — [Cohomology.lean, line 72](../KomorebiSpace/Cohomology.lean#L72)
- `KomorebiSpace.ObstructionComplex.obstruction_certificate` — [Cohomology.lean, line 76](../KomorebiSpace/Cohomology.lean#L76)
- `KomorebiSpace.Differential.anticommuting_sum_square_zero` — [Cohomology.lean, line 91](../KomorebiSpace/Cohomology.lean#L91)

## Exactification

- `KomorebiSpace.Exactification.residual_zero_of_limit` — [Exactification.lean, line 23](../KomorebiSpace/Exactification.lean#L23)
- `KomorebiSpace.Exactification.summable_exactification` — [Exactification.lean, line 36](../KomorebiSpace/Exactification.lean#L36)
- `KomorebiSpace.Exactification.productRate_nonneg` — [Exactification.lean, line 53](../KomorebiSpace/Exactification.lean#L53)
- `KomorebiSpace.Exactification.variable_decay` — [Exactification.lean, line 61](../KomorebiSpace/Exactification.lean#L61)
- `KomorebiSpace.Exactification.variable_exactification` — [Exactification.lean, line 75](../KomorebiSpace/Exactification.lean#L75)
- `KomorebiSpace.Exactification.geometric_decay` — [Exactification.lean, line 98](../KomorebiSpace/Exactification.lean#L98)
- `KomorebiSpace.Exactification.geometric_limit_bound` — [Exactification.lean, line 111](../KomorebiSpace/Exactification.lean#L111)
- `KomorebiSpace.Exactification.geometric_exactification` — [Exactification.lean, line 136](../KomorebiSpace/Exactification.lean#L136)
- `KomorebiSpace.PathIndependence.limits_equal_of_distance_vanishes` — [Exactification.lean, line 163](../KomorebiSpace/Exactification.lean#L163)
- `KomorebiSpace.PathIndependence.limits_equal_of_budget` — [Exactification.lean, line 168](../KomorebiSpace/Exactification.lean#L168)

## WeightedGeometry

- `KomorebiSpace.TransportCost.distance_le_cost` — [WeightedGeometry.lean, line 29](../KomorebiSpace/WeightedGeometry.lean#L29)
- `KomorebiSpace.TransportCost.distance_self` — [WeightedGeometry.lean, line 32](../KomorebiSpace/WeightedGeometry.lean#L32)
- `KomorebiSpace.TransportCost.distance_triangle` — [WeightedGeometry.lean, line 36](../KomorebiSpace/WeightedGeometry.lean#L36)
- `KomorebiSpace.TransportCost.zero_cost_distance` — [WeightedGeometry.lean, line 42](../KomorebiSpace/WeightedGeometry.lean#L42)
- `KomorebiSpace.TransportCost.collapse_of_zero_arrows` — [WeightedGeometry.lean, line 47](../KomorebiSpace/WeightedGeometry.lean#L47)
- `KomorebiSpace.TransportCost.symDistance_self` — [WeightedGeometry.lean, line 54](../KomorebiSpace/WeightedGeometry.lean#L54)
- `KomorebiSpace.TransportCost.symDistance_comm` — [WeightedGeometry.lean, line 57](../KomorebiSpace/WeightedGeometry.lean#L57)
- `KomorebiSpace.TransportCost.symDistance_triangle` — [WeightedGeometry.lean, line 60](../KomorebiSpace/WeightedGeometry.lean#L60)

## NormedDefects

- `KomorebiSpace.NormedDefects.horizontal` — [NormedDefects.lean, line 25](../KomorebiSpace/NormedDefects.lean#L25)
- `KomorebiSpace.NormedDefects.compression_shell` — [NormedDefects.lean, line 31](../KomorebiSpace/NormedDefects.lean#L31)
- `KomorebiSpace.NormedDefects.transported_telescope` — [NormedDefects.lean, line 39](../KomorebiSpace/NormedDefects.lean#L39)
- `KomorebiSpace.NormedDefects.horizontal_norm` — [NormedDefects.lean, line 52](../KomorebiSpace/NormedDefects.lean#L52)
- `KomorebiSpace.NormedDefects.horizontal_contractive` — [NormedDefects.lean, line 58](../KomorebiSpace/NormedDefects.lean#L58)
- `KomorebiSpace.NormedDefects.whiskered_norm` — [NormedDefects.lean, line 70](../KomorebiSpace/NormedDefects.lean#L70)
- `KomorebiSpace.NormedDefects.transported_stokes_bound` — [NormedDefects.lean, line 80](../KomorebiSpace/NormedDefects.lean#L80)

## ObstructionFloor

- `KomorebiSpace.ObstructionFloor.nonnegative` — [ObstructionFloor.lean, line 23](../KomorebiSpace/ObstructionFloor.lean#L23)
- `KomorebiSpace.ObstructionFloor.lower_bound` — [ObstructionFloor.lean, line 25](../KomorebiSpace/ObstructionFloor.lean#L25)
- `KomorebiSpace.ObstructionFloor.zero_iff_closure` — [ObstructionFloor.lean, line 29](../KomorebiSpace/ObstructionFloor.lean#L29)
- `KomorebiSpace.ObstructionFloor.zero_iff_mem_of_closed` — [ObstructionFloor.lean, line 33](../KomorebiSpace/ObstructionFloor.lean#L33)
- `KomorebiSpace.ObstructionFloor.persistent_obstruction` — [ObstructionFloor.lean, line 39](../KomorebiSpace/ObstructionFloor.lean#L39)

## Profiles

- `KomorebiSpace.Profiles.schedule_tendsto_atTop` — [Profiles.lean, line 21](../KomorebiSpace/Profiles.lean#L21)
- `KomorebiSpace.Profiles.vanish_of_sample` — [Profiles.lean, line 28](../KomorebiSpace/Profiles.lean#L28)
- `KomorebiSpace.Profiles.cofinal_vanish_iff` — [Profiles.lean, line 41](../KomorebiSpace/Profiles.lean#L41)
- `KomorebiSpace.Profiles.alternating_even` — [Profiles.lean, line 52](../KomorebiSpace/Profiles.lean#L52)
- `KomorebiSpace.Profiles.alternating_odd` — [Profiles.lean, line 56](../KomorebiSpace/Profiles.lean#L56)
- `KomorebiSpace.Profiles.sampled_alternating_vanishes` — [Profiles.lean, line 59](../KomorebiSpace/Profiles.lean#L59)
- `KomorebiSpace.Profiles.alternating_does_not_vanish` — [Profiles.lean, line 64](../KomorebiSpace/Profiles.lean#L64)

## ProjectiveExample

- `KomorebiSpace.ProjectiveExample.phase_zero_left` — [ProjectiveExample.lean, line 21](../KomorebiSpace/ProjectiveExample.lean#L21)
- `KomorebiSpace.ProjectiveExample.phase_zero_right` — [ProjectiveExample.lean, line 22](../KomorebiSpace/ProjectiveExample.lean#L22)
- `KomorebiSpace.ProjectiveExample.cocycle` — [ProjectiveExample.lean, line 24](../KomorebiSpace/ProjectiveExample.lean#L24)
- `KomorebiSpace.ProjectiveExample.coboundary_symmetric` — [ProjectiveExample.lean, line 31](../KomorebiSpace/ProjectiveExample.lean#L31)
- `KomorebiSpace.ProjectiveExample.phase_asymmetric` — [ProjectiveExample.lean, line 36](../KomorebiSpace/ProjectiveExample.lean#L36)
- `KomorebiSpace.ProjectiveExample.no_scalar_flattening` — [ProjectiveExample.lean, line 39](../KomorebiSpace/ProjectiveExample.lean#L39)

## LinearExactification

- `KomorebiSpace.LinearExactification.semantic_limit` — [LinearExactification.lean, line 31](../KomorebiSpace/LinearExactification.lean#L31)
- `KomorebiSpace.LinearExactification.summable_semantic_exactification` — [LinearExactification.lean, line 42](../KomorebiSpace/LinearExactification.lean#L42)
- `KomorebiSpace.LinearExactification.geometric_semantic_exactification` — [LinearExactification.lean, line 54](../KomorebiSpace/LinearExactification.lean#L54)
- `KomorebiSpace.LinearExactification.controlled_obstruction_vanishes` — [LinearExactification.lean, line 67](../KomorebiSpace/LinearExactification.lean#L67)

## BanachTowers

- `KomorebiSpace.BanachTower.candidates_complete` — [BanachTowers.lean, line 43](../KomorebiSpace/BanachTowers.lean#L43)
- `KomorebiSpace.BanachTower.rawDefect_bound` — [BanachTowers.lean, line 48](../KomorebiSpace/BanachTowers.lean#L48)
- `KomorebiSpace.BanachTower.rawDefect_mem` — [BanachTowers.lean, line 64](../KomorebiSpace/BanachTowers.lean#L64)
- `KomorebiSpace.BanachTower.differentialLinear_bound` — [BanachTowers.lean, line 87](../KomorebiSpace/BanachTowers.lean#L87)
- `KomorebiSpace.BanachTower.differential_apply` — [BanachTowers.lean, line 97](../KomorebiSpace/BanachTowers.lean#L97)
- `KomorebiSpace.BanachTower.differential_bound` — [BanachTowers.lean, line 101](../KomorebiSpace/BanachTowers.lean#L101)
- `KomorebiSpace.BanachTower.differential_opNorm` — [BanachTowers.lean, line 105](../KomorebiSpace/BanachTowers.lean#L105)
- `KomorebiSpace.BanachTower.evaluation_apply` — [BanachTowers.lean, line 113](../KomorebiSpace/BanachTowers.lean#L113)
- `KomorebiSpace.BanachTower.evaluation_bound` — [BanachTowers.lean, line 116](../KomorebiSpace/BanachTowers.lean#L116)
- `KomorebiSpace.BanachTower.exact_iff_differential_zero` — [BanachTowers.lean, line 123](../KomorebiSpace/BanachTowers.lean#L123)
- `KomorebiSpace.BanachTower.exact_iff_algebraic` — [BanachTowers.lean, line 142](../KomorebiSpace/BanachTowers.lean#L142)
- `KomorebiSpace.BanachTower.onLimit_coordinate` — [BanachTowers.lean, line 168](../KomorebiSpace/BanachTowers.lean#L168)
- `KomorebiSpace.BanachTower.onLimit_unique` — [BanachTowers.lean, line 171](../KomorebiSpace/BanachTowers.lean#L171)

## RepairDynamics

- `KomorebiSpace.RepairDynamics.orbit_zero` — [RepairDynamics.lean, line 32](../KomorebiSpace/RepairDynamics.lean#L32)
- `KomorebiSpace.RepairDynamics.orbit_succ` — [RepairDynamics.lean, line 35](../KomorebiSpace/RepairDynamics.lean#L35)
- `KomorebiSpace.RepairDynamics.step_residual` — [RepairDynamics.lean, line 38](../KomorebiSpace/RepairDynamics.lean#L38)
- `KomorebiSpace.RepairDynamics.step_semantics` — [RepairDynamics.lean, line 41](../KomorebiSpace/RepairDynamics.lean#L41)
- `KomorebiSpace.RepairDynamics.step_movement` — [RepairDynamics.lean, line 45](../KomorebiSpace/RepairDynamics.lean#L45)
- `KomorebiSpace.RepairDynamics.orbit_semantics` — [RepairDynamics.lean, line 51](../KomorebiSpace/RepairDynamics.lean#L51)
- `KomorebiSpace.RepairDynamics.step_fixes_exact` — [RepairDynamics.lean, line 57](../KomorebiSpace/RepairDynamics.lean#L57)
- `KomorebiSpace.RepairDynamics.orbit_fixes_exact` — [RepairDynamics.lean, line 61](../KomorebiSpace/RepairDynamics.lean#L61)
- `KomorebiSpace.RepairDynamics.exactification_from_correction_operator` — [RepairDynamics.lean, line 70](../KomorebiSpace/RepairDynamics.lean#L70)
- `KomorebiSpace.RepairDynamics.repair_exists` — [RepairDynamics.lean, line 88](../KomorebiSpace/RepairDynamics.lean#L88)
- `KomorebiSpace.RepairDynamics.obstruction_vanishes` — [RepairDynamics.lean, line 99](../KomorebiSpace/RepairDynamics.lean#L99)
- `KomorebiSpace.RepairDynamics.unique_repair` — [RepairDynamics.lean, line 109](../KomorebiSpace/RepairDynamics.lean#L109)

## RepairProjection

- `KomorebiSpace.RepairDynamics.orbit_add` — [RepairProjection.lean, line 33](../KomorebiSpace/RepairProjection.lean#L33)
- `KomorebiSpace.RepairDynamics.orbit_smul` — [RepairProjection.lean, line 41](../KomorebiSpace/RepairProjection.lean#L41)
- `KomorebiSpace.RepairDynamics.Scheme.limit_spec` — [RepairProjection.lean, line 55](../KomorebiSpace/RepairProjection.lean#L55)
- `KomorebiSpace.RepairDynamics.Scheme.tendsto_limit` — [RepairProjection.lean, line 63](../KomorebiSpace/RepairProjection.lean#L63)
- `KomorebiSpace.RepairDynamics.Scheme.limit_exact` — [RepairProjection.lean, line 66](../KomorebiSpace/RepairProjection.lean#L66)
- `KomorebiSpace.RepairDynamics.Scheme.limit_semantics` — [RepairProjection.lean, line 68](../KomorebiSpace/RepairProjection.lean#L68)
- `KomorebiSpace.RepairDynamics.Scheme.limit_error` — [RepairProjection.lean, line 71](../KomorebiSpace/RepairProjection.lean#L71)
- `KomorebiSpace.RepairDynamics.Scheme.limit_fixes_exact` — [RepairProjection.lean, line 76](../KomorebiSpace/RepairProjection.lean#L76)
- `KomorebiSpace.RepairDynamics.Scheme.limit_add` — [RepairProjection.lean, line 83](../KomorebiSpace/RepairProjection.lean#L83)
- `KomorebiSpace.RepairDynamics.Scheme.limit_smul` — [RepairProjection.lean, line 89](../KomorebiSpace/RepairProjection.lean#L89)
- `KomorebiSpace.RepairDynamics.Scheme.stabilityConstant_nonneg` — [RepairProjection.lean, line 104](../KomorebiSpace/RepairProjection.lean#L104)
- `KomorebiSpace.RepairDynamics.Scheme.limit_bound` — [RepairProjection.lean, line 109](../KomorebiSpace/RepairProjection.lean#L109)
- `KomorebiSpace.RepairDynamics.Scheme.projection_apply` — [RepairProjection.lean, line 126](../KomorebiSpace/RepairProjection.lean#L126)
- `KomorebiSpace.RepairDynamics.Scheme.projection_bound` — [RepairProjection.lean, line 128](../KomorebiSpace/RepairProjection.lean#L128)
- `KomorebiSpace.RepairDynamics.Scheme.projection_idempotent` — [RepairProjection.lean, line 132](../KomorebiSpace/RepairProjection.lean#L132)
- `KomorebiSpace.RepairDynamics.Scheme.projection_image_iff` — [RepairProjection.lean, line 136](../KomorebiSpace/RepairProjection.lean#L136)
- `KomorebiSpace.RepairDynamics.Scheme.exact_residual_splitting` — [RepairProjection.lean, line 144](../KomorebiSpace/RepairProjection.lean#L144)
- `KomorebiSpace.RepairDynamics.Scheme.scheme_independent` — [RepairProjection.lean, line 154](../KomorebiSpace/RepairProjection.lean#L154)

## BanachTowerExactification

- `KomorebiSpace.BanachTower.geometric_exactification` — [BanachTowerExactification.lean, line 24](../KomorebiSpace/BanachTowerExactification.lean#L24)
- `KomorebiSpace.BanachTower.coordinate_dist_le` — [BanachTowerExactification.lean, line 38](../KomorebiSpace/BanachTowerExactification.lean#L38)
- `KomorebiSpace.BanachTower.nonzero_of_protected_level` — [BanachTowerExactification.lean, line 44](../KomorebiSpace/BanachTowerExactification.lean#L44)
- `KomorebiSpace.BanachTower.repair_by_operator` — [BanachTowerExactification.lean, line 52](../KomorebiSpace/BanachTowerExactification.lean#L52)
- `KomorebiSpace.BanachTower.repair_and_realize` — [BanachTowerExactification.lean, line 71](../KomorebiSpace/BanachTowerExactification.lean#L71)
- `KomorebiSpace.BanachTower.unique_repair_of_separation` — [BanachTowerExactification.lean, line 95](../KomorebiSpace/BanachTowerExactification.lean#L95)
- `KomorebiSpace.BanachTower.projection_exact_preserving_idempotent` — [BanachTowerExactification.lean, line 115](../KomorebiSpace/BanachTowerExactification.lean#L115)
- `KomorebiSpace.BanachTower.projection_stability_bound` — [BanachTowerExactification.lean, line 126](../KomorebiSpace/BanachTowerExactification.lean#L126)

## ConstantTower

- `KomorebiSpace.BanachTower.constantCandidate_apply` — [ConstantTower.lean, line 33](../KomorebiSpace/ConstantTower.lean#L33)
- `KomorebiSpace.BanachTower.constantCandidate_exact` — [ConstantTower.lean, line 36](../KomorebiSpace/ConstantTower.lean#L36)
- `KomorebiSpace.BanachTower.constant_exact_iff` — [ConstantTower.lean, line 43](../KomorebiSpace/ConstantTower.lean#L43)
- `KomorebiSpace.BanachTower.constant_unique_repair` — [ConstantTower.lean, line 62](../KomorebiSpace/ConstantTower.lean#L62)
- `KomorebiSpace.BanachTower.constant_realization` — [ConstantTower.lean, line 88](../KomorebiSpace/ConstantTower.lean#L88)

## RepairExamples

- `KomorebiSpace.RepairExamples.split_step` — [RepairExamples.lean, line 32](../KomorebiSpace/RepairExamples.lean#L32)
- `KomorebiSpace.RepairExamples.split_projection` — [RepairExamples.lean, line 40](../KomorebiSpace/RepairExamples.lean#L40)
- `KomorebiSpace.RepairExamples.split_nonzero` — [RepairExamples.lean, line 47](../KomorebiSpace/RepairExamples.lean#L47)
- `KomorebiSpace.RepairExamples.semantics_alone_not_unique` — [RepairExamples.lean, line 54](../KomorebiSpace/RepairExamples.lean#L54)

