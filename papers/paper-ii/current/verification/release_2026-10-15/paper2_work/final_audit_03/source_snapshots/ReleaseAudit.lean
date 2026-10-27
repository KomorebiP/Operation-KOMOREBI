import KomorebiVerification.PaperII.CommonRefinementConsumers
import KomorebiVerification.PaperII

section ReleaseAudit
open Lean Meta Elab Command
set_option maxHeartbeats 8000000
run_cmd do
  let env ← getEnv
  let targets : Array Name := #[
    `Komorebi.Foundation.LinearProjectorFamily.exactPacketCoordinates,
    `Komorebi.Foundation.LinearProjectorFamily.rangeAnalysis_rangeSynthesis,
    `Komorebi.Foundation.LinearProjectorFamily.rangeSynthesis_rangeAnalysis,
    `Komorebi.PaperII.LinearDefects.norm_power_defect_le,
    `Komorebi.PaperII.LinearDefects.norm_power_defect_le_raw,
    `Komorebi.PaperII.LinearDefects.power_defect_identity_all,
    `Komorebi.PaperII.LinearDefects.resolvent_defect_identity,
    `Komorebi.PaperII.NestedRefinement.Refines,
    `Komorebi.PaperII.NestedRefinement.Refines.child_decomposition_unique,
    `Komorebi.PaperII.NestedRefinement.Refines.coarse_comp_fine_eq_self,
    `Komorebi.PaperII.NestedRefinement.Refines.coarse_comp_fine_eq_zero,
    `Komorebi.PaperII.NestedRefinement.Refines.coarse_packet_reconstruction,
    `Komorebi.PaperII.NestedRefinement.Refines.coarsenCoordinates_component,
    `Komorebi.PaperII.NestedRefinement.Refines.fine_comp_coarse_eq_self,
    `Komorebi.PaperII.NestedRefinement.Refines.fine_comp_coarse_eq_zero,
    `Komorebi.PaperII.NestedRefinement.Refines.refineCoordinates_component,
    `Komorebi.PaperII.NestedRefinement.Refines.trans,
    `Komorebi.PaperII.NestedRefinement.children,
    `Komorebi.PaperII.NestedRefinement.coarsenCoordinates,
    `Komorebi.PaperII.NestedRefinement.coarsenCoordinates_refineCoordinates,
    `Komorebi.PaperII.NestedRefinement.coordinateOperator,
    `Komorebi.PaperII.NestedRefinement.coordinateOperator_comp,
    `Komorebi.PaperII.NestedRefinement.coordinateOperator_naturality,
    `Komorebi.PaperII.NestedRefinement.coordinateRefinementEquiv,
    `Komorebi.PaperII.NestedRefinement.coordinateRefinementEquiv_trans,
    `Komorebi.PaperII.NestedRefinement.finitePacket_decomposition_ext,
    `Komorebi.PaperII.NestedRefinement.finitePacket_decomposition_unique,
    `Komorebi.PaperII.NestedRefinement.mem_children,
    `Komorebi.PaperII.NestedRefinement.refineCoordinates,
    `Komorebi.PaperII.NestedRefinement.refineCoordinates_coarsenCoordinates,
    `Komorebi.PaperII.NestedRefinement.refineCoordinates_comp,
    `Komorebi.PaperII.NestedRefinement.refineCoordinates_self,
    `Komorebi.PaperII.NestedRefinement.transferBlock_refinement,
    `Komorebi.PaperII.NestedRefinement.transferBlock_refinement_and_reconstruction,
    `Komorebi.PaperII.NestedRefinement.transferBlock_refinement_between,
    `Komorebi.PaperII.ResultantSeparation.CongruentModLattice,
    `Komorebi.PaperII.ResultantSeparation.EvaluatedBezoutCertificate,
    `Komorebi.PaperII.ResultantSeparation.IsLatticeUnit,
    `Komorebi.PaperII.ResultantSeparation.IsSeparationWeight,
    `Komorebi.PaperII.ResultantSeparation.IsSeparationWeight.mono,
    `Komorebi.PaperII.ResultantSeparation.ScalarPreservesLattice,
    `Komorebi.PaperII.ResultantSeparation.pow_smul_separator_eq_unit_inv_smul_separatorNumerator,
    `Komorebi.PaperII.ResultantSeparation.projector_precision_delay,
    `Komorebi.PaperII.ResultantSeparation.scalar_mul_separator_of_ne_zero,
    `Komorebi.PaperII.ResultantSeparation.scalar_mul_separator_preservesLattice_of_ne_zero,
    `Komorebi.PaperII.ResultantSeparation.separationWeight,
    `Komorebi.PaperII.ResultantSeparation.separationWeight_clears,
    `Komorebi.PaperII.ResultantSeparation.separationWeight_le_of_clears,
    `Komorebi.PaperII.ResultantSeparation.separatorNumerator_apply_of_mem_ker_F_of_bezout,
    `Komorebi.PaperII.ResultantSeparation.separatorNumerator_eq_scalar_sub_of_bezout,
    `Komorebi.PaperII.ResultantSeparation.separatorNumerator_mul_self_of_bezout,
    `Komorebi.PaperII.ResultantSeparation.separator_apply_of_mem_ker_F_of_bezout,
    `Komorebi.PaperII.ResultantSeparation.separator_apply_of_mem_ker_G,
    `Komorebi.PaperII.ResultantSeparation.separator_hasFiniteSeparationWeight_of_eq_unit_mul_pow,
    `Komorebi.PaperII.ResultantSeparation.separator_idempotent_of_bezout,
    `Komorebi.PaperII.ResultantSeparation.separator_isSeparationWeight_of_unit_mul_pow_eq_of_inv_preserves,
    `Komorebi.PaperII.ResultantSeparation.separator_separationWeight_le_of_eq_unit_mul_pow,
    `Komorebi.PaperII.SmithDyadic.HasExactPLocalDenominatorWeight,
    `Komorebi.PaperII.SmithDyadic.SmithCardinalityCertificate,
    `Komorebi.PaperII.SmithDyadic.SmithSolvabilityCertificate,
    `Komorebi.PaperII.SmithDyadic.SmithZModAdmissible,
    `Komorebi.PaperII.SmithDyadic.negativeSignProjector_exact_pLocal_weight_zero_of_prime_ne_two,
    `Komorebi.PaperII.SmithDyadic.negativeSignProjector_idempotent,
    `Komorebi.PaperII.SmithDyadic.oddAdicVersusDyadicSignBehavior_trace,
    `Komorebi.PaperII.SmithDyadic.padicValNat_two_at_odd_prime,
    `Komorebi.PaperII.SmithDyadic.positiveSignProjector_exact_pLocal_weight_zero_of_prime_ne_two,
    `Komorebi.PaperII.SmithDyadic.positiveSignProjector_idempotent,
    `Komorebi.PaperII.SmithDyadic.signFactors_resultant,
    `Komorebi.PaperII.SmithDyadic.signInvolution_mul_self,
    `Komorebi.PaperII.SmithDyadic.signProjectors_complete,
    `Komorebi.PaperII.SmithDyadic.signProjectors_resultant_dyadic_weight_endpoint,
    `Komorebi.PaperII.SmithDyadic.smithPhase,
    `Komorebi.PaperII.SmithDyadic.smithPhase_neg_one_eq_inv,
    `Komorebi.PaperII.SmithDyadic.smithZModCoordinateCertificate,
    `Komorebi.PaperII.SmithDyadic.smithZModFiber_card_of_admissible,
    `Komorebi.PaperII.SmithDyadic.smithZModFiber_nonempty_iff,
    `Komorebi.PaperII.SmithDyadic.smithZModMulHom,
    `Komorebi.PaperII.SmithDyadic.smithZMod_global_conditional_count,
    `Komorebi.PaperII.SmithDyadic.smithZMod_global_solvable_iff,
    `Komorebi.PaperII.SmithDyadic.smith_conditional_product_count,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.RationalCertificate.certificate_explicit_rationality,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.RationalCertificate.constant_coefficient_recurrence,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.coefficientAlgorithm,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.coefficientAlgorithm_correct,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.coefficientAlgorithm_firstEdge,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.enumeratedPathZetaMatrix_eq_matrixPathZetaMatrix,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.exactWalkFirstEdgeEquiv,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.finite_graph_constant_coefficient_recurrence,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.finite_graph_pathZeta_rationality,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.finite_graph_transferZeta_trace,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.mem_walkTuplesAtWeight_iff,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.pathZetaAlgorithm_trace,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.pathZeta_eq_inverse_mul_transferNumerator,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.pathZeta_eq_matrixPathZeta,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.transferDenominator,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.transferDenominator_coeff_zero,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.transferDenominator_mul_pathZeta,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.transferMatrix,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.transferNumerator,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.tuple_captured_iff,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.walkTuplesAtWeight,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.weightedAdjacency,
    `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.weightedAdjacency_coeff,
    `Komorebi.PaperII.TypedLinearDefects.TwoSidedInverse,
    `Komorebi.PaperII.TypedLinearDefects.continuousDefect,
    `Komorebi.PaperII.TypedLinearDefects.continuousPolynomialAction_compatible_of_defect_eq_zero,
    `Komorebi.PaperII.TypedLinearDefects.continuousScalarShift,
    `Komorebi.PaperII.TypedLinearDefects.continuous_end_pow_norm_le,
    `Komorebi.PaperII.TypedLinearDefects.continuous_norm_power_defect_le,
    `Komorebi.PaperII.TypedLinearDefects.continuous_norm_power_defect_le_geometric_majorant,
    `Komorebi.PaperII.TypedLinearDefects.continuous_norm_resolvent_defect_le,
    `Komorebi.PaperII.TypedLinearDefects.continuous_power_defect_identity_all,
    `Komorebi.PaperII.TypedLinearDefects.continuous_resolvents_compatible_of_defect_eq_zero,
    `Komorebi.PaperII.TypedLinearDefects.continuous_scalarShift_resolvent_identity,
    `Komorebi.PaperII.TypedLinearDefects.defect,
    `Komorebi.PaperII.TypedLinearDefects.polynomialAction,
    `Komorebi.PaperII.TypedLinearDefects.polynomialAction_compatible_of_defect_eq_zero,
    `Komorebi.PaperII.TypedLinearDefects.power_defect_identity,
    `Komorebi.PaperII.TypedLinearDefects.power_defect_identity_all,
    `Komorebi.PaperII.TypedLinearDefects.powers_compatible_of_defect_eq_zero,
    `Komorebi.PaperII.TypedLinearDefects.resolvents_compatible_of_defect_eq_zero,
    `Komorebi.PaperII.TypedLinearDefects.scalarShift_resolvent_identity,
    `Komorebi.PaperII.WeightedTransfer.MultiplicativeFiltration,
    `Komorebi.PaperII.WeightedTransfer.PrecisionCertificate,
    `Komorebi.PaperII.WeightedTransfer.TwoSidedInverse,
    `Komorebi.PaperII.WeightedTransfer.analyticDiagonalTransferInverse_spec,
    `Komorebi.PaperII.WeightedTransfer.analyticGeometricInverse_spec,
    `Komorebi.PaperII.WeightedTransfer.diagonalTransferInverse_spec,
    `Komorebi.PaperII.WeightedTransfer.finiteGeometricInverse,
    `Komorebi.PaperII.WeightedTransfer.finiteGeometricInverse_spec_of_pow_eq_zero,
    `Komorebi.PaperII.WeightedTransfer.finitePrecisionPrunedDiagonalTransferInverse_of_minWeight,
    `Komorebi.PaperII.WeightedTransfer.finitePrecisionPrunedDiagonalTransferInverse_of_weightedEdges,
    `Komorebi.PaperII.WeightedTransfer.finitePrecisionPrunedInverse_of_weightedEdges,
    `Komorebi.PaperII.WeightedTransfer.le_mul_ceilDiv,
    `Komorebi.PaperII.WeightedTransfer.map_finiteGeometricInverse_eq_prunedWordInverse,
    `Komorebi.PaperII.WeightedTransfer.map_sum_pow_eq_zero_at_scaled_cutoff,
    `Komorebi.PaperII.WeightedTransfer.minWeight_mul_length_le_wordWeight,
    `Komorebi.PaperII.WeightedTransfer.prunedDiagonalTransferInverse,
    `Komorebi.PaperII.WeightedTransfer.prunedWordInverse,
    `Komorebi.PaperII.WeightedTransfer.prunedWordInverse_spec_of_minWeight,
    `Komorebi.PaperII.WeightedTransfer.retainedFixedWordSum,
    `Komorebi.Residue.FiniteRingFourierOrthogonalityCertificate,
    `Komorebi.Residue.FiniteRingFourierOrthogonalityCertificate.toRingCertificate,
    `Komorebi.Residue.crtComponents_bijective,
    `Komorebi.Residue.crtEquiv,
    `Komorebi.Residue.dyadicOddComponents_bijective,
    `Komorebi.Residue.dyadicOddEquiv,
    `Komorebi.Residue.fourierAverage_eq_residueProj_of_primitiveRoot,
    `Komorebi.Residue.polyphase_refinement,
    `Komorebi.Residue.primitiveRoot_fourierOrthogonalityCertificate,
    `Komorebi.Residue.residueProj_complete,
    `Komorebi.Residue.residueProj_crt,
    `Komorebi.Residue.residueProj_crt_comm,
    `Komorebi.Residue.residueProj_dyadicOdd,
    `Komorebi.Residue.residueProj_idempotent,
    `Komorebi.Residue.residueProj_orthogonal,
    `Komorebi.Residue.ringFourierAverage,
    `Komorebi.Residue.ringFourierAverage_eq_residueProj_of_finite_certificate,
    `Komorebi.Residue.ringFourierKernel_eq_residueKernel,
    `Komorebi.Residue.ringFourierResidueKernel,
  ]
  for name in targets do
    unless env.contains name do
      throwError "MISSING_FROZEN_TARGET: {name}"
  logInfo m!"FROZEN_MAP_PASS rows=25 unique_compiled_declarations={targets.size}"

run_cmd do
  let env ← getEnv
  let mut audited : Nat := 0
  for (name, info) in env.checked.get.constants.toList do
    if Name.isPrefixOf `Komorebi name then
      audited := audited + 1
      if info.isUnsafe then
        throwError "unsafe project declaration: {name}"
      let axioms ← Lean.collectAxioms name
      for axiomName in axioms do
        unless axiomName == ``propext || axiomName == ``Classical.choice ||
            axiomName == ``Quot.sound do
          throwError "unexpected axiom {axiomName} in project declaration {name}"
  if audited == 0 then
    throwError "kernel audit found no Komorebi declarations"
  logInfo m!"EXTENDED FAIL-CLOSED KERNEL AUDIT PASS: {audited} Komorebi declarations; allowed axioms only: propext, Classical.choice, Quot.sound"

run_cmd do
  let env ← getEnv
  let endpoints : Array Name := #[
    `Komorebi.PaperII.CommonRefinement.manuscript_common_refinement,
    `Komorebi.PaperII.CommonRefinement.manuscript_coarsest_unique,
    `Komorebi.PaperII.CommonRefinement.manuscript_finite_common,
    `Komorebi.PaperII.CommonRefinement.exists_common_iff,
    `Komorebi.PaperII.CommonRefinement.supported_index_empty_on_zero_module,
    `Komorebi.PaperII.CommonRefinement.noncommuting_product_not_idempotent,
  ]
  for name in endpoints do
    let some info := env.find? name | throwError "MISSING_CONSUMER: {name}"
    let some val := info.value? (allowOpaque := true) | throwError "MISSING_BODY: {name}"
    match Lean.Kernel.check env {} val with
    | .error _ => throwError "BODY_RECHECK_FAILED: {name}"
    | .ok inferred =>
      unless Lean.Kernel.isDefEqGuarded env {} inferred info.type do
        throwError "BODY_TYPE_MISMATCH: {name}"
    let axioms ← Lean.collectAxioms name
    logInfo m!"ENDPOINT_RECHECK_PASS {name} AXIOMS {axioms}"
  logInfo m!"ENDPOINT_BODY_RECHECK_PASS count={endpoints.size}"
open Lean Meta Elab Command in
run_cmd do
  let env ← getEnv
  let mut count : Nat := 0
  let mut bodies : Nat := 0
  for (name, info) in env.checked.get.constants.toList do
    if Name.isPrefixOf `Komorebi.PaperII.CommonRefinement name then
      count := count + 1
      let axs ← Lean.collectAxioms name
      for ax in axs do
        unless ax == ``propext || ax == ``Classical.choice || ax == ``Quot.sound do
          throwError m!"NEW_BODY_POLICY_REJECT {name} {ax}"
      if info.isUnsafe then throwError m!"UNSAFE_NEW_BODY {name}"
      match info.value? (allowOpaque := true) with
      | none => logInfo m!"NEW_DECL_STRUCTURAL {name}"
      | some value =>
        let inferred ← Lean.ofExceptKernelException (Lean.Kernel.check env {} value)
        unless Lean.Kernel.isDefEqGuarded env {} inferred info.type do
          throwError m!"NEW_BODY_TYPE_MISMATCH {name}"
        bodies := bodies + 1
        logInfo m!"NEW_DECL_BODY_CHECKED {name} AXIOMS {axs}"
  if count == 0 then throwError "NEW_EMPTY_NAMESPACE"
  logInfo m!"NEW_DECLARATION_BODY_AUDIT_PASS entries={count} bodies={bodies}"

#print Komorebi.PaperII.CommonRefinement.manuscript_common_refinement
#print Komorebi.PaperII.CommonRefinement.manuscript_coarsest_unique
#print Komorebi.PaperII.CommonRefinement.manuscript_finite_common
#print Komorebi.PaperII.CommonRefinement.exists_common_iff
#print Komorebi.PaperII.CommonRefinement.supported_index_empty_on_zero_module
#print Komorebi.PaperII.CommonRefinement.noncommuting_product_not_idempotent

#eval "PAPER_II_SUPPORTED_COMMON_REFINEMENT_RELEASE_PASS"
end ReleaseAudit
