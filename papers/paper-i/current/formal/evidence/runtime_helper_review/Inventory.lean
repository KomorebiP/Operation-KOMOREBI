import KomorebiVerification.MathlibImports
import KomorebiVerification.Basic
import KomorebiVerification.ProjectorCore
import KomorebiVerification.FibreRefinement
import KomorebiVerification.ExactCoordinates
import KomorebiVerification.ResidueProjectors
import KomorebiVerification.PaperITransport
import KomorebiVerification.PaperIBlockCompletion
import KomorebiVerification.SeedRankBasics
import KomorebiVerification.SeedRankOperations
import KomorebiVerification.SemisimpleSeedRank
import KomorebiVerification.FullMatrixCyclicity
import KomorebiVerification.SemisimpleCompletion
import KomorebiVerification.PathGraphKrylov
import KomorebiVerification.SingleOperatorGraph
import KomorebiVerification.PacketNaturalityCompletion
import KomorebiVerification.TopologicalCompletion
import KomorebiVerification.EllipticAlgorithms
import KomorebiVerification
import KomorebiVerification.KernelAudit
import PaperICompletion.CyclicClassification
import PaperICompletion.SpectralCertificates
import PaperICompletion.ConditionedCoordinates
import PaperICompletion
import PaperICompletion3.PrimarySeedFormula
import PaperICompletion3.OperatorPrimaryAPI
import PaperICompletion3.InvariantFactorCount
import PaperICompletion3
import PaperICompletion4.ResidueQuotient
import PaperICompletion4.IntrinsicPrimary
import PaperICompletion4.GroupedPrimary
import PaperICompletion4.OperatorIntrinsicFormula
import PaperICompletion4
import PaperICompletion5.LinearPrimaryEigenspace
import PaperICompletion5.GeometricSeedFormula
import PaperICompletion5.CyclicGeometricCriterion
import PaperICompletion5
import PaperICompletion6.ScalarExtension
import PaperICompletion6.PrimaryCyclicCriterion
import PaperICompletion6.OneInvariantFactor
import PaperICompletion6.SixWayCyclicCriterion
import PaperICompletion6
import PaperICompletion7.Nakayama
import PaperICompletion7.ModuleTop
import PaperICompletion7.LocalResidue
import PaperICompletion7
import PaperICompletion8.DivisionRows
import PaperICompletion8.DivisionBlock
import PaperICompletion8.DivisionProduct
import PaperICompletion8.RegularMultiplicity
import PaperICompletion8.SemisimpleFormula
import PaperICompletion8.ProductPresentation
import PaperICompletion8.SemisimpleExistence
import PaperICompletion8
import PaperIRelease.AlgebraSupport
import PaperIRelease.AlgebraTransfer
import PaperIRelease.PacketAggregation
import PaperIRelease.AlgebraPreorder
import PaperIRelease.AlgebraQuotient
import PaperIRelease.AlgebraClassGrouping
import PaperIRelease.AlgebraDiagonal
import PaperIRelease.BoundedStar
import PaperIRelease.CategoryPackets
import PaperIRelease.CategoryExport
import PaperIRelease.GrammarAlgebra
import PaperIRelease.GrammarTyped
import PaperIRelease.GrammarModules
import PaperIRelease.GrammarEquivalence
import PaperIRelease.GrammarIdeal
import PaperIRelease.GrammarPaths
import PaperIRelease.GrammarFactorization
import PaperIRelease.CategoryBoundaries
import PaperIRelease.CategoryUniversal
import PaperIRelease.CoordinateTransport
import PaperIRelease.ExactSequences
import PaperIRelease.GeneralNormedPackets
import PaperIRelease.GeneralPacketBounds
import PaperIRelease.GeneralConditionedCoordinates
import PaperIRelease.GeneralFiniteCompletion
import PaperIRelease.GraphReachability
import PaperIRelease.GraphSources
import PaperIRelease.GraphPropagation
import PaperIRelease.GraphSourceProjection
import PaperIRelease.GraphSourceBoundary
import PaperIRelease.PacketDescent
import PaperIRelease.PacketCorners
import PaperIRelease.PacketPureRank
import PaperIRelease.PacketLocalRank
import PaperIRelease.GraphSourceCount
import PaperIRelease.GraphSourceObstruction
import PaperIRelease.PacketExactSequence
import PaperIRelease.PacketTopology
import PaperIRelease.PacketBoundaryTests
import PaperIRelease.PacketEquivalentNorm
import PaperIRelease.PacketSourceLower
import PaperIRelease.PacketSourceUpper
import PaperIRelease.PacketSourceRank
import PaperIRelease.PacketPureBoundaryTests
import PaperIRelease.PacketTopologyGeneral
import PaperIRelease.PacketUniversal
import PaperIRelease.PolynomialModule
import PaperIRelease.PolynomialMonic
import PaperIRelease.ScalarExtension
import PaperIRelease.SeedOperations
import PaperIRelease.TensorPackets
import PaperIRelease.TopologyTransport
import PaperIRelease.TopologyCategories
import PaperIRelease.TopologyCountablePackets
import PaperIRelease.TopologyDenseCompletion
import PaperIRelease.TopologyFiniteCompletion
import PaperIRelease.TopologyPresentations
import PaperIRelease.TopologySeedRank
import PaperIRelease.TopologySemilinearRank
import PaperIRelease.TopologyUnconditional
import PaperIRelease.TopologyUnconditionalBridge
import PaperIRelease
import ReleaseBoundary
open Lean Meta Elab Command
-- Diagnostic inventory only: no audit whitelist is changed by this command.
run_cmd do
  let env ← getEnv
  let moduleNames := env.header.moduleNames
  let ownedModules : Array Name := #[`KomorebiVerification.MathlibImports, `KomorebiVerification.Basic, `KomorebiVerification.ProjectorCore, `KomorebiVerification.FibreRefinement, `KomorebiVerification.ExactCoordinates, `KomorebiVerification.ResidueProjectors, `KomorebiVerification.PaperITransport, `KomorebiVerification.PaperIBlockCompletion, `KomorebiVerification.SeedRankBasics, `KomorebiVerification.SeedRankOperations, `KomorebiVerification.SemisimpleSeedRank, `KomorebiVerification.FullMatrixCyclicity, `KomorebiVerification.SemisimpleCompletion, `KomorebiVerification.PathGraphKrylov, `KomorebiVerification.SingleOperatorGraph, `KomorebiVerification.PacketNaturalityCompletion, `KomorebiVerification.TopologicalCompletion, `KomorebiVerification.EllipticAlgorithms, `KomorebiVerification, `KomorebiVerification.KernelAudit, `PaperICompletion.CyclicClassification, `PaperICompletion.SpectralCertificates, `PaperICompletion.ConditionedCoordinates, `PaperICompletion, `PaperICompletion3.PrimarySeedFormula, `PaperICompletion3.OperatorPrimaryAPI, `PaperICompletion3.InvariantFactorCount, `PaperICompletion3, `PaperICompletion4.ResidueQuotient, `PaperICompletion4.IntrinsicPrimary, `PaperICompletion4.GroupedPrimary, `PaperICompletion4.OperatorIntrinsicFormula, `PaperICompletion4, `PaperICompletion5.LinearPrimaryEigenspace, `PaperICompletion5.GeometricSeedFormula, `PaperICompletion5.CyclicGeometricCriterion, `PaperICompletion5, `PaperICompletion6.ScalarExtension, `PaperICompletion6.PrimaryCyclicCriterion, `PaperICompletion6.OneInvariantFactor, `PaperICompletion6.SixWayCyclicCriterion, `PaperICompletion6, `PaperICompletion7.Nakayama, `PaperICompletion7.ModuleTop, `PaperICompletion7.LocalResidue, `PaperICompletion7, `PaperICompletion8.DivisionRows, `PaperICompletion8.DivisionBlock, `PaperICompletion8.DivisionProduct, `PaperICompletion8.RegularMultiplicity, `PaperICompletion8.SemisimpleFormula, `PaperICompletion8.ProductPresentation, `PaperICompletion8.SemisimpleExistence, `PaperICompletion8, `PaperIRelease.AlgebraSupport, `PaperIRelease.AlgebraTransfer, `PaperIRelease.PacketAggregation, `PaperIRelease.AlgebraPreorder, `PaperIRelease.AlgebraQuotient, `PaperIRelease.AlgebraClassGrouping, `PaperIRelease.AlgebraDiagonal, `PaperIRelease.BoundedStar, `PaperIRelease.CategoryPackets, `PaperIRelease.CategoryExport, `PaperIRelease.GrammarAlgebra, `PaperIRelease.GrammarTyped, `PaperIRelease.GrammarModules, `PaperIRelease.GrammarEquivalence, `PaperIRelease.GrammarIdeal, `PaperIRelease.GrammarPaths, `PaperIRelease.GrammarFactorization, `PaperIRelease.CategoryBoundaries, `PaperIRelease.CategoryUniversal, `PaperIRelease.CoordinateTransport, `PaperIRelease.ExactSequences, `PaperIRelease.GeneralNormedPackets, `PaperIRelease.GeneralPacketBounds, `PaperIRelease.GeneralConditionedCoordinates, `PaperIRelease.GeneralFiniteCompletion, `PaperIRelease.GraphReachability, `PaperIRelease.GraphSources, `PaperIRelease.GraphPropagation, `PaperIRelease.GraphSourceProjection, `PaperIRelease.GraphSourceBoundary, `PaperIRelease.PacketDescent, `PaperIRelease.PacketCorners, `PaperIRelease.PacketPureRank, `PaperIRelease.PacketLocalRank, `PaperIRelease.GraphSourceCount, `PaperIRelease.GraphSourceObstruction, `PaperIRelease.PacketExactSequence, `PaperIRelease.PacketTopology, `PaperIRelease.PacketBoundaryTests, `PaperIRelease.PacketEquivalentNorm, `PaperIRelease.PacketSourceLower, `PaperIRelease.PacketSourceUpper, `PaperIRelease.PacketSourceRank, `PaperIRelease.PacketPureBoundaryTests, `PaperIRelease.PacketTopologyGeneral, `PaperIRelease.PacketUniversal, `PaperIRelease.PolynomialModule, `PaperIRelease.PolynomialMonic, `PaperIRelease.ScalarExtension, `PaperIRelease.SeedOperations, `PaperIRelease.TensorPackets, `PaperIRelease.TopologyTransport, `PaperIRelease.TopologyCategories, `PaperIRelease.TopologyCountablePackets, `PaperIRelease.TopologyDenseCompletion, `PaperIRelease.TopologyFiniteCompletion, `PaperIRelease.TopologyPresentations, `PaperIRelease.TopologySeedRank, `PaperIRelease.TopologySemilinearRank, `PaperIRelease.TopologyUnconditional, `PaperIRelease.TopologyUnconditionalBridge, `PaperIRelease, `ReleaseBoundary]
  let mut count := 0
  let mut partialCount := 0
  let mut unsafeCount := 0
  for (name, info) in env.checked.get.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let owner := moduleNames[idx.toNat]!
      if ownedModules.contains owner then
        count := count + 1
        if info.isPartial then partialCount := partialCount + 1
        if info.isUnsafe then unsafeCount := unsafeCount + 1
        if info.isPartial || info.isUnsafe then
          let axioms ← Lean.collectAxioms name
          let typ ← liftTermElabM <| Meta.ppExpr info.type
          let kind := match info with
            | .defnInfo _ => "definition"
            | .thmInfo _ => "theorem"
            | .opaqueInfo _ => "opaque"
            | .axiomInfo _ => "axiom"
            | _ => "other"
          let row := Json.mkObj [
            ("module", toJson owner.toString), ("name", toJson name.toString),
            ("kind", toJson kind), ("unsafe", toJson info.isUnsafe),
            ("partial", toJson info.isPartial),
            ("type", toJson typ.pretty),
            ("axioms", toJson (axioms.map Name.toString))]
          liftIO <| IO.println ("DIAGNOSTIC_HELPER " ++ row.compress)
  liftIO <| IO.println s!"DIAGNOSTIC_COMPLETE OWNED {count} PARTIAL {partialCount} UNSAFE {unsafeCount}"
