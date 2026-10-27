import KomorebiVerification.Basic
import KomorebiVerification.ExactCoordinates
import KomorebiVerification.FibreRefinement
import KomorebiVerification.ResidueProjectors
import KomorebiVerification.PaperITransport
import KomorebiVerification.PaperIBlockCompletion
import KomorebiVerification.SeedRankBasics
import KomorebiVerification.SemisimpleSeedRank
import KomorebiVerification.FullMatrixCyclicity
import KomorebiVerification.PathGraphKrylov
import KomorebiVerification.SeedRankOperations
import KomorebiVerification.SemisimpleCompletion
import KomorebiVerification.SingleOperatorGraph
import KomorebiVerification.PacketNaturalityCompletion
import KomorebiVerification.TopologicalCompletion
import KomorebiVerification.EllipticAlgorithms
import Mathlib.Util.AssertNoSorry

/-!
# Kernel audit and concrete smoke tests

Author: Komorebi P.

The examples below instantiate the abstract results on four rational
coordinates. The declaration list is exactly the unique compiled surface of
the versioned theorem map. The final command then fails compilation if any
project declaration depends on a nonstandard axiom or is unsafe.
-/

set_option autoImplicit false

namespace Komorebi.Verification

open Komorebi.Foundation
open Komorebi.Foundation.LinearProjectorFamily
open Komorebi.Packet

/-- Fine addresses are the four individual coordinates. -/
def fineAddress (i : Fin 4) : Fin 4 := i

/-- Coarse addresses merge the four coordinates into their parity classes. -/
def parityAddress (i : Fin 4) : Fin 2 :=
  ⟨i.val % 2, Nat.mod_lt _ (by omega)⟩

/-- The concrete coordinate masks form a complete orthogonal linear family. -/
def fourCoordinateFamily :
    LinearProjectorFamily ℚ (Fin 4 → ℚ) (Fin 4) :=
  fibreLinearProjectorFamily (R := ℚ) (M := ℚ) fineAddress

/-- Exact recovery holds in the concrete four-coordinate model. -/
example (x : Fin 4 → ℚ) :
    fourCoordinateFamily.rangeSynthesis
      (fourCoordinateFamily.rangeAnalysis x) = x := by
  exact fourCoordinateFamily.rangeSynthesis_rangeAnalysis x

/-- Every valid tuple of range packets is recovered by analysis after synthesis. -/
example (packets : fourCoordinateFamily.PacketSpace) :
    fourCoordinateFamily.rangeAnalysis
      (fourCoordinateFamily.rangeSynthesis packets) = packets := by
  exact fourCoordinateFamily.rangeAnalysis_rangeSynthesis packets

/--
The independently defined parity mask is exactly the sum of its fine
coordinate masks.  This is a concrete `Fin 4 → Fin 2` refinement test.
-/
theorem parity_refinement (b : Fin 2) (x : Fin 4 → ℚ) :
    fibreProj parityAddress b x =
      ∑ c, if parityAddress c = b then fibreProj fineAddress c x else 0 := by
  simpa [fineAddress] using
    (fibreProj_refinement fineAddress parityAddress b x)

/-- A linear operator is recovered exactly from all sixteen packet blocks. -/
example (T : (Fin 4 → ℚ) →ₗ[ℚ] (Fin 4 → ℚ)) (x : Fin 4 → ℚ) :
    (∑ j, ∑ i,
      fourCoordinateFamily.proj j (T (fourCoordinateFamily.proj i x))) = T x := by
  exact transferBlock_reconstruction
    fourCoordinateFamily fourCoordinateFamily T x

end Komorebi.Verification

#print axioms Komorebi.FiniteAlgorithms.assembleTransferBlockTable
#print axioms Komorebi.FiniteAlgorithms.exactGraphSeedRank
#print axioms Komorebi.FiniteAlgorithms.exactGraphSeedRank_isLeast
#print axioms Komorebi.FiniteAlgorithms.orbitClosureIter_eq_orbitHull_of_stop
#print axioms Komorebi.FiniteAlgorithms.orbitHull_algorithm_terminates_and_correct
#print axioms Komorebi.FiniteAlgorithms.transferBlockTable
#print axioms Komorebi.FiniteAlgorithms.transferBlock_algorithm_correct
#print axioms Komorebi.FiniteAlgorithms.transferGraph_iff_block_ne_zero
#print axioms Komorebi.Foundation.LinearProjectorFamily.conjugate
#print axioms Komorebi.Foundation.LinearProjectorFamily.exactPacketCoordinates
#print axioms Komorebi.Foundation.LinearProjectorFamily.rangeAnalysis_rangeSynthesis
#print axioms Komorebi.Foundation.LinearProjectorFamily.rangeSynthesis_rangeAnalysis
#print axioms Komorebi.Foundation.conjugate_transferBlock
#print axioms Komorebi.Foundation.end_comp_eq_sum_transferBlock_comps
#print axioms Komorebi.Foundation.transferBlock_comp_end
#print axioms Komorebi.Foundation.transferBlock_comp_linearMap
#print axioms Komorebi.Foundation.transferBlock_reconstruction_end
#print axioms Komorebi.Foundation.transferBlock_reconstruction_linearMap
#print axioms Komorebi.PacketNaturalityCompletion.FullBlocks.blockMulClosed_iff_transitive
#print axioms Komorebi.PacketNaturalityCompletion.FullBlocks.end_finrank_eq_packet_sum_eq_square
#print axioms Komorebi.PacketNaturalityCompletion.FullBlocks.finrank_eq_sum_packet_finrank
#print axioms Komorebi.PacketNaturalityCompletion.FullBlocks.fullBlockAlgEquiv
#print axioms Komorebi.PacketNaturalityCompletion.FullBlocks.identity_blocks_supported_iff_reflexive
#print axioms Komorebi.PacketNaturalityCompletion.FullBlocks.packetBlockAlgebra_mul_eq_blockMul
#print axioms Komorebi.PacketNaturalityCompletion.FullBlocks.restrictBlocks_synthesizeBlocks
#print axioms Komorebi.PacketNaturalityCompletion.FullBlocks.synthesizeBlocks_restrictBlocks
#print axioms Komorebi.PacketNaturalityCompletion.Packets.eq_iff_projectors_eq
#print axioms Komorebi.PacketNaturalityCompletion.Packets.transferBlock_pow_eq_packetPathSum
#print axioms Komorebi.PacketNaturalityCompletion.Reachability.algebraicOrbitHull_le_reachable_support
#print axioms Komorebi.PacketNaturalityCompletion.Reachability.conjugate_reachableFrom_iff
#print axioms Komorebi.PacketNaturalityCompletion.Reachability.conjugate_transferEdge_iff
#print axioms Komorebi.PacketNaturalityCompletion.Reachability.unreachable_nonzero_packet_obstruction
#print axioms Komorebi.PacketNaturalityCompletion.StrictNaturality.full_transfer_edge_zero_pattern_correspondence
#print axioms Komorebi.PacketNaturalityCompletion.StrictNaturality.generatedHull_natural
#print axioms Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_naturality_package
#print axioms Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_eq_of_bijective
#print axioms Komorebi.PacketNaturalityCompletion.StrictNaturality.strict_seedRank_le
#print axioms Komorebi.PacketNaturalityCompletion.TypedQuiver.typed_reachability_certificate
#print axioms Komorebi.SeedRankBasics.generates_singleton_iff_surjective
#print axioms Komorebi.SeedRankBasics.multiSeedQuotientEquiv
#print axioms Komorebi.SeedRankBasics.multiSeedQuotientEquivRange
#print axioms Komorebi.SeedRankBasics.multiSeedQuotientEquivRange_apply_mk
#print axioms Komorebi.SeedRankBasics.oneSeedQuotientEquivRange
#print axioms Komorebi.SeedRankBasics.oneSeedQuotientEquivRange_apply_mk
#print axioms Komorebi.SeedRankOperations.seedFinrank_isLeast_free_surjection
#print axioms Komorebi.SeedRankOperations.cyclic_iff_seedRank_eq_one
#print axioms Komorebi.SeedRankOperations.seedRank_le_of_surjective_semilinear
#print axioms Komorebi.SeedRankOperations.seedRank_imageAlgebra_eq
#print axioms Komorebi.SeedRankOperations.seedRank_prod_le_add
#print axioms Komorebi.SeedRankOperations.seedRank_prod_productAlgebra
#print axioms Komorebi.SeedRankOperations.seedRank_tensorProduct_le_mul
#print axioms Komorebi.SeedRankOperations.finrank_le_seedRank_of_scalar_quotient
#print axioms Komorebi.SeedRankOperations.tensorOperator_smul_tmul
#print axioms Komorebi.SemisimpleCompletion.fullMatrix_every_nonzero_vector_generates
#print axioms Komorebi.SemisimpleCompletion.fullMatrix_seedRank_eq_one
#print axioms Komorebi.SemisimpleCompletion.multiplicity_obstruction
#print axioms Komorebi.SemisimpleCompletion.multiplicity_seedRank_formula
#print axioms Komorebi.SemisimpleCompletion.semisimple_seedRank_eq_maxCeilDiv_of_equivalences
#print axioms Komorebi.SemisimpleCompletion.splitProduct_seedRank_eq_maxCeilDiv
#print axioms Komorebi.SingleOperatorGraph.complex_cycle_seedNumber_isLeast_two
#print axioms Komorebi.SingleOperatorGraph.cyclic_matrix_criterion_of_primary_decomposition
#print axioms Komorebi.SingleOperatorGraph.cyclic_matrix_four_way_iff_of_primary_decomposition
#print axioms Komorebi.SingleOperatorGraph.graph_seedNumber_eq_max_eigenspace_multiplicity
#print axioms Komorebi.SingleOperatorGraph.graph_seedNumber_eq_max_eigenspace_multiplicity_of_distinct
#print axioms Komorebi.SingleOperatorGraph.operatorAlgebra_seedFinrank_eq_of_seedNumber_isLeast
#print axioms Komorebi.SingleOperatorGraph.operatorAlgebra_seedRank_eq_of_seedNumber_isLeast
#print axioms Komorebi.SingleOperatorGraph.path_endpoint_seedNumber_isLeast_one
#print axioms Komorebi.SingleOperatorGraph.singleOperator_operatorAlgebra_seedRanks_eq_of_primary_decomposition
#print axioms Komorebi.SingleOperatorGraph.singleOperator_seedNumber_isLeast_of_primary_decomposition
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.BilateralShiftRepresentation.concretePower_apply
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.adjoint_transferBlock
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.closure_le_ker_of_le_ker
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense_intertwines
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.completionEquivOfIsometryDense_unique
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.concreteBilateralShift_seedCardinality_isLeast
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.concreteBilateralShift_topologicallyCyclic
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.dense_operatorHull_image
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.idempotentRange_eq_closure_map
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.map_packetRange_eq
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.packetEquiv
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.packetRange_eq_closure_map
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.topological_packet_isomorphism
#print axioms KomorebiVerification.TopologicalCompletion.BoundedProjectorFamily.topological_reachability_obstruction

/-! ## Fail-closed project audit -/

open Lean Meta Elab Command

/-
Audit every imported declaration owned by either project namespace. This
turns the trust boundary into a compilation gate instead of a review of
selected diagnostic output.
-/
run_cmd do
  let env ← getEnv
  let mut audited : Nat := 0
  for (name, info) in env.checked.get.constants.toList do
    if Name.isPrefixOf `Komorebi name || Name.isPrefixOf `KomorebiVerification name then
      audited := audited + 1
      if info.isUnsafe then
        throwError "unsafe project declaration: {name}"
      match info with
      | .axiomInfo _ =>
          throwError "project axiom declaration: {name}"
      | .opaqueInfo _ =>
          throwError "opaque project declaration: {name}"
      | _ => pure ()
      let axioms ← Lean.collectAxioms name
      for axiomName in axioms do
        unless axiomName == ``propext || axiomName == ``Classical.choice ||
            axiomName == ``Quot.sound do
          throwError "unexpected axiom {axiomName} in project declaration {name}"
  if audited == 0 then
    throwError "kernel audit found no project declarations"
  logInfo m!"FAIL-CLOSED KERNEL AUDIT PASS: {audited} project declarations; allowed axioms only: propext, Classical.choice, Quot.sound"
