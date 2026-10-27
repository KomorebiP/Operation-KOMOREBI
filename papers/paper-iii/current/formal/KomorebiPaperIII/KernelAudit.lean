/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIII

/-!
# Paper III v1.0.1 kernel audit

This file prints the dependency surface of all 143 declarations in the final
Paper III theorem map: 88 theorem declarations and 55 constructions.  The
fail-closed namespace gate then checks all 468 compiled declarations under
`Komorebi.PaperIII`, including generated declarations, and freezes the exact
namespace and theorem counts.  Any unsafe, axiom, opaque, unexpected-axiom, or
unreviewed new namespace declaration is a release blocker.
-/

#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.packetMatrix
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.packetMatrix_apply
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.edgeOp
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.edgeOp_apply
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.transferOp
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.edgeOp_eq_zero_off_support
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.packetMatrix_mul_packetMatrix
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.edgeOp_mul_edgeOp_eq_zero
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.edgeOp_mul_edgeOp_of_composable
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.Composable
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.wordOp
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.wordOp_nil
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.wordOp_singleton
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.wordOp_append
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.wordOp_eq_zero_of_first_break
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.wordOp_eq_zero_of_not_composable
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.wordExpansion
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.tupleWordOp
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.explicitWordExpansion
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.walkExpansion
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.tupleWordOp_snoc
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.explicitWordExpansion_succ
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.wordExpansion_eq_explicitWordExpansion
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.explicitWordExpansion_eq_walkExpansion
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.transferOp_pow_eq_wordExpansion
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.transferOp_pow_eq_explicitWordExpansion
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.transferOp_pow_eq_walkExpansion
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.reverseCoefficient
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.terminalTarget
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.Connects
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.wordOp_eq_packetMatrix_of_composable
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.wordOp_apply_eq_if_connects
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.endpointWalkCoefficientSum
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.transferOp_pow_apply_eq_sum_walks
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.transferOp_pow_apply_eq_zero_of_no_walk
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.Reachable
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.transferOp_pow_apply_eq_zero_of_not_reachable
#print axioms Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.transferOp_pow_mulVec_apply_eq_zero_of_unreachable_support
#print axioms Komorebi.PaperIII.EdgeOperators.heterogeneousPacketPathExpansion_two
#print axioms Komorebi.PaperIII.EdgeOperators.heterogeneousPacketPathExpansion_three
#print axioms Komorebi.PaperIII.EdgeOperators.heterogeneousProduct
#print axioms Komorebi.PaperIII.EdgeOperators.heterogeneousPathSum
#print axioms Komorebi.PaperIII.EdgeOperators.heterogeneousPacketPathExpansion
#print axioms Komorebi.PaperIII.EdgeOperators.SupportedStep
#print axioms Komorebi.PaperIII.EdgeOperators.SupportedPath
#print axioms Komorebi.PaperIII.EdgeOperators.heterogeneousPathSum_eq_zero_of_no_supportedPath
#print axioms Komorebi.PaperIII.EdgeOperators.supportedHeterogeneousPacketPathExpansion
#print axioms Komorebi.PaperIII.EdgeOperators.heterogeneousProduct_apply_eq_zero_of_no_supportedPath
#print axioms Komorebi.PaperIII.Transport.exactTransport
#print axioms Komorebi.PaperIII.Transport.exactTransport_apply
#print axioms Komorebi.PaperIII.Transport.exactTransport_self
#print axioms Komorebi.PaperIII.Transport.exactTransport_cocycle
#print axioms Komorebi.PaperIII.Transport.exactTransport_roundTrip
#print axioms Komorebi.PaperIII.Transport.exactTransport_triangleLoop
#print axioms Komorebi.PaperIII.Transport.pathEndpoint
#print axioms Komorebi.PaperIII.Transport.exactPathTransport
#print axioms Komorebi.PaperIII.Transport.exactPathTransport_eq_endpoint
#print axioms Komorebi.PaperIII.Transport.exactPathTransport_loop
#print axioms Komorebi.PaperIII.Transport.exactCoordinateTransport
#print axioms Komorebi.PaperIII.Transport.exactCoordinateTransport_apply
#print axioms Komorebi.PaperIII.Transport.exactCoordinateTransport_self
#print axioms Komorebi.PaperIII.Transport.exactCoordinateTransport_symm
#print axioms Komorebi.PaperIII.Transport.exactCoordinateTransport_cocycle
#print axioms Komorebi.PaperIII.Transport.exactCoordinateTransport_triangle
#print axioms Komorebi.PaperIII.Transport.exactCoordinateMap
#print axioms Komorebi.PaperIII.Transport.exactCoordinateMap_apply
#print axioms Komorebi.PaperIII.Transport.exactCoordinateMap_id
#print axioms Komorebi.PaperIII.Transport.exactCoordinateMap_comp
#print axioms Komorebi.PaperIII.Transport.exactCoordinateMap_naturality
#print axioms Komorebi.PaperIII.Transport.Connection
#print axioms Komorebi.PaperIII.Transport.Connection.CocycleAt
#print axioms Komorebi.PaperIII.Transport.Connection.Flat
#print axioms Komorebi.PaperIII.Transport.Connection.cocycleDefect
#print axioms Komorebi.PaperIII.Transport.Connection.triangleHolonomy
#print axioms Komorebi.PaperIII.Transport.Connection.triangleHolonomy_eq_refl_of_flat
#print axioms Komorebi.PaperIII.Transport.Connection.cocycleDefect_eq_refl_of_flat
#print axioms Komorebi.PaperIII.Transport.doubleEquiv
#print axioms Komorebi.PaperIII.Transport.doubleEquiv_apply
#print axioms Komorebi.PaperIII.Transport.twistedThreePointConnection
#print axioms Komorebi.PaperIII.Transport.twisted_triangleHolonomy_apply_one
#print axioms Komorebi.PaperIII.Transport.twisted_triangleHolonomy_ne_refl
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.Gauge
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.CocycleAt
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.Flat
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.cocycleDefect
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.triangleHolonomy
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.triangleObstruction
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.cocycleDefect_eq_zero_iff_cocycleAt
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.triangleHolonomy_sub_id
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.triangleObstruction_eq_zero_iff_cocycleDefect_eq_zero
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.triangleObstruction_eq_zero_iff_triangleHolonomy_eq_refl
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.cocycleDefect_eq_zero_iff_triangleHolonomy_eq_refl
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.flat_iff_triangleHolonomy_eq_refl
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.canonicalTransport
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.canonicalConnection
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.canonicalConnection_flat
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.canonicalTransport_zero_connectionDefect
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.canonicalTransport_triangleHolonomy_eq_refl
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.flatGauge
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.flat_isGaugeOfCanonical
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.pathTransport
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.pathTransport_eq_direct_of_flat
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.VertexPath
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.indexedPathTransport
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.indexedPathTransport_eq_direct_of_flat
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.indexedLoopTransport_eq_refl_of_flat
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.gauge
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.gauge_cocycleDefect
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.gauge_triangleHolonomy
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.gauge_cocycleAt_iff
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.gauge_flat_iff
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.gauge_triangleHolonomy_eq_refl_iff
#print axioms Komorebi.PaperIII.HolonomyBlocks.PacketResolution
#print axioms Komorebi.PaperIII.HolonomyBlocks.PacketResolution.block
#print axioms Komorebi.PaperIII.HolonomyBlocks.PacketResolution.sum_blocks
#print axioms Komorebi.PaperIII.HolonomyBlocks.PacketResolution.blocks_zero_iff
#print axioms Komorebi.PaperIII.HolonomyBlocks.PacketResolution.exists_packetWitness_of_block_ne_zero
#print axioms Komorebi.PaperIII.HolonomyBlocks.obstruction_sum_blocks
#print axioms Komorebi.PaperIII.HolonomyBlocks.obstructionBlocks_zero_iff
#print axioms Komorebi.PaperIII.HolonomyBlocks.obstructionDetection_equivalences
#print axioms Komorebi.PaperIII.HolonomyBlocks.exists_packetWitness_of_obstructionBlock_ne_zero
#print axioms Komorebi.PaperIII.HolonomyBlocks.PacketResolution.gaugeConjugate
#print axioms Komorebi.PaperIII.HolonomyBlocks.PacketResolution.PacketPreserving
#print axioms Komorebi.PaperIII.HolonomyBlocks.PacketResolution.symm_commutes_of_packetPreserving
#print axioms Komorebi.PaperIII.HolonomyBlocks.PacketResolution.block_gauge_of_commutes
#print axioms Komorebi.PaperIII.HolonomyBlocks.PacketResolution.gaugeConjugate_eq_zero_iff
#print axioms Komorebi.PaperIII.HolonomyBlocks.PacketResolution.block_gauge_eq_zero_iff
#print axioms Komorebi.PaperIII.Transport.ReversibleConnection.gauge_triangleObstruction
#print axioms Komorebi.PaperIII.HolonomyBlocks.obstructionBlock_gauge_of_commutes
#print axioms Komorebi.PaperIII.HolonomyBlocks.obstructionBlock_gauge_eq_zero_iff
#print axioms Komorebi.PaperIII.NonlinearObstructions.OperationTree
#print axioms Komorebi.PaperIII.NonlinearObstructions.OperationTree.eval
#print axioms Komorebi.PaperIII.NonlinearObstructions.OperationTree.inputs
#print axioms Komorebi.PaperIII.NonlinearObstructions.OperationTree.eval_congr_on_inputs
#print axioms Komorebi.PaperIII.NonlinearObstructions.OperationTree.eval_eq_of_inputs_eq_empty
#print axioms Komorebi.PaperIII.NonlinearObstructions.IsSolution
#print axioms Komorebi.PaperIII.NonlinearObstructions.ObstructionPacket
#print axioms Komorebi.PaperIII.NonlinearObstructions.ObstructionPacket.not_isSolution
#print axioms Komorebi.PaperIII.NonlinearObstructions.obstructionPacket_of_not_isSolution
#print axioms Komorebi.PaperIII.NonlinearObstructions.not_isSolution_iff_nonempty_obstructionPacket

/-! ## Fail-closed full-namespace audit -/

open Lean Meta Elab Command

run_cmd do
  let env ← getEnv
  let mut audited : Nat := 0
  let mut theorems : Nat := 0
  for (name, info) in env.checked.get.constants.toList do
    if Name.isPrefixOf `Komorebi.PaperIII name then
      audited := audited + 1
      match info with
      | .thmInfo _ => theorems := theorems + 1
      | _ => pure ()
      if info.isUnsafe then
        throwError "unsafe Paper III declaration: {name}"
      match info with
      | .axiomInfo _ =>
          throwError "Paper III axiom declaration: {name}"
      | .opaqueInfo _ =>
          throwError "opaque Paper III declaration: {name}"
      | _ => pure ()
      let axioms ← Lean.collectAxioms name
      for axiomName in axioms do
        unless axiomName == ``propext || axiomName == ``Classical.choice ||
            axiomName == ``Quot.sound do
          throwError "unexpected axiom {axiomName} in Paper III declaration {name}"
  if audited != 468 then
    throwError "Paper III namespace declaration count changed: expected 468, found {audited}"
  if theorems != 229 then
    throwError "Paper III namespace theorem count changed: expected 229, found {theorems}"
  logInfo m!"FAIL-CLOSED PAPER III v1.0.1 KERNEL AUDIT PASS: {audited} declarations ({theorems} theoremInfo); 143 explicit mapped targets; allowed axioms only: propext, Classical.choice, Quot.sound"
