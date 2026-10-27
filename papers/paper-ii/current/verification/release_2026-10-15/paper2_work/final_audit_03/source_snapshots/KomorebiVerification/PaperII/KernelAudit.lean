/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiVerification.PaperII.NestedRefinement
import KomorebiVerification.PaperII.ResidueFourierCRT
import KomorebiVerification.PaperII.WeightedTransfer
import KomorebiVerification.PaperII.TransferZeta
import KomorebiVerification.PaperII.ResultantSeparation
import KomorebiVerification.PaperII.SmithDyadic
import KomorebiVerification.PaperII.LinearDefects
import KomorebiVerification.PaperII.TypedLinearDefects
import Mathlib.Util.AssertNoSorry

/-!
# Paper II kernel audit

Author: Komorebi P.

This module imports every Paper II theorem module, reports the trusted
dependencies of representative public declarations, and then performs a
fail-closed namespace-wide audit.  The final audit inspects every imported
`Komorebi.*` declaration and rejects placeholders, project axioms, unsafe
declarations, or any axiom outside Lean's standard quotient/extensionality/
choice basis.
-/

set_option autoImplicit false

/-! ## Nested refinement and exact packet coordinates -/

#print axioms Komorebi.PaperII.NestedRefinement.finitePacket_decomposition_unique
#print axioms Komorebi.PaperII.NestedRefinement.Refines.trans
#print axioms Komorebi.PaperII.NestedRefinement.coordinateRefinementEquiv
#print axioms Komorebi.PaperII.NestedRefinement.refineCoordinates_comp
#print axioms Komorebi.PaperII.NestedRefinement.coordinateRefinementEquiv_trans
#print axioms Komorebi.PaperII.NestedRefinement.coordinateOperator_comp
#print axioms Komorebi.PaperII.NestedRefinement.coordinateOperator_naturality
#print axioms Komorebi.PaperII.NestedRefinement.transferBlock_refinement_between
#print axioms Komorebi.PaperII.NestedRefinement.transferBlock_refinement_and_reconstruction
#print axioms Komorebi.PaperII.NestedRefinement.transferBlock_refinement

/-! ## Residue, Fourier, and CRT packets -/

#print axioms Komorebi.Residue.polyphase_refinement
#print axioms Komorebi.Residue.ringFourierAverage_eq_residueProj_of_certificate
#print axioms Komorebi.Residue.FiniteRingFourierOrthogonalityCertificate.toRingCertificate
#print axioms Komorebi.Residue.ringFourierAverage_eq_residueProj_of_finite_certificate
#print axioms Komorebi.Residue.fourierAverage_eq_residueProj_of_certificate
#print axioms Komorebi.Residue.fourierAverage_eq_residueProj_of_primitiveRoot
#print axioms Komorebi.Residue.residueProj_crt
#print axioms Komorebi.Residue.residueProj_dyadicOdd

/-! ## Weighted transfer and finite-precision inversion -/

#print axioms Komorebi.PaperII.WeightedTransfer.finiteGeometricInverse_spec_of_pow_eq_zero
#print axioms Komorebi.PaperII.WeightedTransfer.analyticDiagonalTransferInverse_spec
#print axioms Komorebi.PaperII.WeightedTransfer.map_eq_pruned_of_wordExpansion
#print axioms Komorebi.PaperII.WeightedTransfer.map_finiteGeometricInverse_eq_prunedWordInverse
#print axioms Komorebi.PaperII.WeightedTransfer.prunedWordInverse_spec_of_minWeight
#print axioms Komorebi.PaperII.WeightedTransfer.finitePrecisionPrunedInverse_of_weightedEdges
#print axioms Komorebi.PaperII.WeightedTransfer.finitePrecisionInverse_of_weightedEdges
#print axioms Komorebi.PaperII.WeightedTransfer.finitePrecisionPrunedDiagonalTransferInverse_of_minWeight
#print axioms Komorebi.PaperII.WeightedTransfer.finitePrecisionPrunedDiagonalTransferInverse_of_weightedEdges
#print axioms Komorebi.PaperII.WeightedTransfer.le_mul_ceilDiv
#print axioms Komorebi.PaperII.WeightedTransfer.finitePrecisionDiagonalTransferInverse_of_weightedEdges

/-! ## Transfer-zeta coefficients and rationality certificates -/

#print axioms Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.coefficientAlgorithm_correct
#print axioms Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.coefficientAlgorithm_eq_card_exactWalk
#print axioms Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.coefficientAlgorithm_firstEdge
#print axioms Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.weightedAdjacency_coeff
#print axioms Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.enumeratedPathZetaMatrix_eq_matrixPathZetaMatrix
#print axioms Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.pathZeta_eq_matrixPathZeta
#print axioms Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.transferDenominator_mul_pathZeta
#print axioms Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.finite_graph_constant_coefficient_recurrence
#print axioms Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.finite_graph_pathZeta_rationality
#print axioms Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.finite_graph_transferZeta_trace
#print axioms Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.pathZetaAlgorithm_trace
#print axioms Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.RationalCertificate.certificate_explicit_rationality
#print axioms Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.RationalCertificate.constant_coefficient_recurrence

/-! ## Resultant-controlled separation -/

#print axioms Komorebi.PaperII.ResultantSeparation.separatorNumerator_mul_self_of_bezout
#print axioms Komorebi.PaperII.ResultantSeparation.separator_idempotent_of_bezout
#print axioms Komorebi.PaperII.ResultantSeparation.separator_idempotent
#print axioms Komorebi.PaperII.ResultantSeparation.scalar_mul_separator_preservesLattice
#print axioms Komorebi.PaperII.ResultantSeparation.pow_smul_separator_eq_unit_inv_smul_separatorNumerator
#print axioms Komorebi.PaperII.ResultantSeparation.separationWeight_clears
#print axioms Komorebi.PaperII.ResultantSeparation.separationWeight_le_of_clears
#print axioms Komorebi.PaperII.ResultantSeparation.IsSeparationWeight.mono
#print axioms Komorebi.PaperII.ResultantSeparation.separator_isSeparationWeight_of_unit_mul_pow_eq_of_inv_preserves
#print axioms Komorebi.PaperII.ResultantSeparation.separator_separationWeight_le_of_unit_mul_pow_eq
#print axioms Komorebi.PaperII.ResultantSeparation.separator_isSeparationWeight_of_pow_eq
#print axioms Komorebi.PaperII.ResultantSeparation.separator_separationWeight_le_of_pow_eq
#print axioms Komorebi.PaperII.ResultantSeparation.projector_precision_delay

/-! ## Smith fibres and dyadic separation -/

#print axioms Komorebi.PaperII.SmithDyadic.smithZModFiber_nonempty_iff
#print axioms Komorebi.PaperII.SmithDyadic.smithZModFiber_card_of_admissible
#print axioms Komorebi.PaperII.SmithDyadic.smithZMod_global_solvable_iff
#print axioms Komorebi.PaperII.SmithDyadic.smithZMod_global_conditional_count
#print axioms Komorebi.PaperII.SmithDyadic.global_solvable_iff_coordinatewise
#print axioms Komorebi.PaperII.SmithDyadic.smith_conditional_product_count
#print axioms Komorebi.PaperII.SmithDyadic.positiveSignProjector_pIntegral_of_prime_ne_two
#print axioms Komorebi.PaperII.SmithDyadic.positiveSignProjector_exact_dyadic_weight
#print axioms Komorebi.PaperII.SmithDyadic.positiveSignProjector_exact_pLocal_weight_zero_of_prime_ne_two
#print axioms Komorebi.PaperII.SmithDyadic.signFactors_resultant
#print axioms Komorebi.PaperII.SmithDyadic.signProjectors_resultant_dyadic_weight_endpoint
#print axioms Komorebi.PaperII.SmithDyadic.oddAdicVersusDyadicSignBehavior_trace
#print axioms Komorebi.PaperII.SmithDyadic.padicValNat_two_at_odd_prime
#print axioms Komorebi.PaperII.SmithDyadic.smithPhase_neg_one_eq_inv

/-! ## Linear refinement defects -/

#print axioms Komorebi.PaperII.LinearDefects.power_defect_identity_all
#print axioms Komorebi.PaperII.LinearDefects.norm_power_defect_le
#print axioms Komorebi.PaperII.LinearDefects.inverse_sandwich_identity
#print axioms Komorebi.PaperII.LinearDefects.resolvent_defect_identity

/-! ## Typed linear refinement defects -/

#print axioms Komorebi.PaperII.TypedLinearDefects.power_defect_identity_all
#print axioms Komorebi.PaperII.TypedLinearDefects.powers_compatible_of_defect_eq_zero
#print axioms Komorebi.PaperII.TypedLinearDefects.polynomialAction_compatible_of_defect_eq_zero
#print axioms Komorebi.PaperII.TypedLinearDefects.continuous_norm_power_defect_le
#print axioms Komorebi.PaperII.TypedLinearDefects.continuous_norm_power_defect_le_geometric_majorant
#print axioms Komorebi.PaperII.TypedLinearDefects.scalarShift_resolvent_identity
#print axioms Komorebi.PaperII.TypedLinearDefects.resolvents_compatible_of_defect_eq_zero
#print axioms Komorebi.PaperII.TypedLinearDefects.continuous_scalarShift_resolvent_identity
#print axioms Komorebi.PaperII.TypedLinearDefects.continuous_norm_resolvent_defect_le
#print axioms Komorebi.PaperII.TypedLinearDefects.continuous_resolvents_compatible_of_defect_eq_zero

/-! ## Fail-closed namespace audit -/

open Lean Meta Elab Command

/-
Audit every declaration in the imported `Komorebi` namespace.  Unlike the
human-readable `#print axioms` sample above, this command fails compilation if
any declaration depends on `sorryAx`, a project-specific axiom, or any axiom
outside the explicitly allowed Lean basis.  It also rejects unsafe
declarations.
-/
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
  logInfo m!"FAIL-CLOSED KERNEL AUDIT PASS: {audited} Komorebi declarations; allowed axioms only: propext, Classical.choice, Quot.sound"
