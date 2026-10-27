import KomorebiVerification.ProjectorCore
import KomorebiVerification.ExactCoordinates
import KomorebiVerification.PaperII.NestedRefinement
import KomorebiVerification.FibreRefinement
import KomorebiVerification.ResidueProjectors
import KomorebiVerification.PaperII.ResidueFourierCRT
import KomorebiVerification.PaperII.WeightedTransfer
import KomorebiVerification.PaperII.TransferZeta
import KomorebiVerification.PaperII.ResultantSeparation
import KomorebiVerification.PaperII.SmithDyadic
import KomorebiVerification.PaperII.LinearDefects
import KomorebiVerification.PaperII.TypedLinearDefects
import KomorebiVerification.PaperII.CommonRefinement
import KomorebiVerification.PaperII.FiniteCommonRefinement
import KomorebiVerification.PaperII.CommonRefinementConsumers
import KomorebiVerification.PaperII.ReleaseCoordinatesAlgebra
import KomorebiVerification.PaperII.ReleaseCoordinatesHilbert
import KomorebiVerification.PaperII.ReleaseCoordinatesResidue
import KomorebiVerification.PaperII.ReleaseCoordinatesFourier
import KomorebiVerification.PaperII.ReleaseCoordinatesConsumers
import KomorebiVerification.PaperII.ReleaseFiltered
import KomorebiVerification.PaperII.ReleaseFilteredPaths
import KomorebiVerification.PaperII.ReleaseResultantPolynomial
import KomorebiVerification.PaperII.ReleaseResultantPackets
import KomorebiVerification.PaperII.ReleaseResultantIntegralPackets
import KomorebiVerification.PaperII.ReleaseGluing
import KomorebiVerification.PaperII.ReleaseGluingDVR
import KomorebiVerification.PaperII.ReleasePrecision
import KomorebiVerification.PaperII.ReleaseGluingPrecisionBridge
import KomorebiVerification.PaperII.ReleaseResultantDVR
import KomorebiVerification.PaperII.ReleaseGluingBinary
import KomorebiVerification.PaperII.ReleaseGluingSmith
import KomorebiVerification.PaperII.ReleaseGluingFinite
import KomorebiVerification.PaperII.ReleaseGluingEquivSmith
import KomorebiVerification.PaperII.ReleaseGluingMatrix
import KomorebiVerification.PaperII.ReleaseGluingPacketBridge
import KomorebiVerification.PaperII.ReleasePrecisionQuotient
import KomorebiVerification.PaperII.ReleaseDefectTower
import KomorebiVerification.PaperII.ReleaseAnalyticExponential
import KomorebiVerification.PaperII.ReleaseAnalyticContour
import KomorebiVerification.PaperII.ReleaseDefectCompatibility
import KomorebiVerification.PaperII.ReleaseTransferMatrix
import KomorebiVerification.PaperII.ReleaseTransferScalar
import KomorebiVerification.PaperII.ReleaseTransferMultigraded
import KomorebiVerification.PaperII.ReleaseTransferMultigradedRational
import KomorebiVerification.PaperII.ReleaseTransferConsequences
import KomorebiVerification.PaperII.ReleaseSmithDVR
import KomorebiVerification.PaperII.ReleaseSmithRectangular
import KomorebiVerification.PaperII.ReleaseSmithTransport
import KomorebiVerification.PaperII.ReleaseSmithSign
import KomorebiVerification.PaperII.ReleaseSmithCharacters
import KomorebiVerification.PaperII.ReleaseRectifiable
import KomorebiVerification.PaperII.ReleaseArcLength
import KomorebiVerification.PaperII.ReleaseRectifiableCycle
import KomorebiVerification.PaperII
import KomorebiVerification
import KomorebiVerification.PaperII.KernelAudit
import KomorebiVerification.PaperII.ReleaseAnalyticContourSup
import KomorebiVerification.PaperII.ReleaseDefectPolynomial
import KomorebiVerification.PaperII.ReleaseDefectKernelAudit
import PaperIIRefinement
import ReleaseAudit

open Lean Meta Elab Command

-- This is an audit program, not a mathematical proof or a new axiom.
run_cmd do
  let env ← getEnv
  let moduleNames := env.header.moduleNames
  let ownedModules : Array Name := #[`KomorebiVerification.ProjectorCore, `KomorebiVerification.ExactCoordinates, `KomorebiVerification.PaperII.NestedRefinement, `KomorebiVerification.FibreRefinement, `KomorebiVerification.ResidueProjectors, `KomorebiVerification.PaperII.ResidueFourierCRT, `KomorebiVerification.PaperII.WeightedTransfer, `KomorebiVerification.PaperII.TransferZeta, `KomorebiVerification.PaperII.ResultantSeparation, `KomorebiVerification.PaperII.SmithDyadic, `KomorebiVerification.PaperII.LinearDefects, `KomorebiVerification.PaperII.TypedLinearDefects, `KomorebiVerification.PaperII.CommonRefinement, `KomorebiVerification.PaperII.FiniteCommonRefinement, `KomorebiVerification.PaperII.CommonRefinementConsumers, `KomorebiVerification.PaperII.ReleaseCoordinatesAlgebra, `KomorebiVerification.PaperII.ReleaseCoordinatesHilbert, `KomorebiVerification.PaperII.ReleaseCoordinatesResidue, `KomorebiVerification.PaperII.ReleaseCoordinatesFourier, `KomorebiVerification.PaperII.ReleaseCoordinatesConsumers, `KomorebiVerification.PaperII.ReleaseFiltered, `KomorebiVerification.PaperII.ReleaseFilteredPaths, `KomorebiVerification.PaperII.ReleaseResultantPolynomial, `KomorebiVerification.PaperII.ReleaseResultantPackets, `KomorebiVerification.PaperII.ReleaseResultantIntegralPackets, `KomorebiVerification.PaperII.ReleaseGluing, `KomorebiVerification.PaperII.ReleaseGluingDVR, `KomorebiVerification.PaperII.ReleasePrecision, `KomorebiVerification.PaperII.ReleaseGluingPrecisionBridge, `KomorebiVerification.PaperII.ReleaseResultantDVR, `KomorebiVerification.PaperII.ReleaseGluingBinary, `KomorebiVerification.PaperII.ReleaseGluingSmith, `KomorebiVerification.PaperII.ReleaseGluingFinite, `KomorebiVerification.PaperII.ReleaseGluingEquivSmith, `KomorebiVerification.PaperII.ReleaseGluingMatrix, `KomorebiVerification.PaperII.ReleaseGluingPacketBridge, `KomorebiVerification.PaperII.ReleasePrecisionQuotient, `KomorebiVerification.PaperII.ReleaseDefectTower, `KomorebiVerification.PaperII.ReleaseAnalyticExponential, `KomorebiVerification.PaperII.ReleaseAnalyticContour, `KomorebiVerification.PaperII.ReleaseDefectCompatibility, `KomorebiVerification.PaperII.ReleaseTransferMatrix, `KomorebiVerification.PaperII.ReleaseTransferScalar, `KomorebiVerification.PaperII.ReleaseTransferMultigraded, `KomorebiVerification.PaperII.ReleaseTransferMultigradedRational, `KomorebiVerification.PaperII.ReleaseTransferConsequences, `KomorebiVerification.PaperII.ReleaseSmithDVR, `KomorebiVerification.PaperII.ReleaseSmithRectangular, `KomorebiVerification.PaperII.ReleaseSmithTransport, `KomorebiVerification.PaperII.ReleaseSmithSign, `KomorebiVerification.PaperII.ReleaseSmithCharacters, `KomorebiVerification.PaperII.ReleaseRectifiable, `KomorebiVerification.PaperII.ReleaseArcLength, `KomorebiVerification.PaperII.ReleaseRectifiableCycle, `KomorebiVerification.PaperII, `KomorebiVerification, `KomorebiVerification.PaperII.KernelAudit, `KomorebiVerification.PaperII.ReleaseAnalyticContourSup, `KomorebiVerification.PaperII.ReleaseDefectPolynomial, `KomorebiVerification.PaperII.ReleaseDefectKernelAudit, `PaperIIRefinement, `ReleaseAudit]
  -- Compiler-generated partial helpers are separately inventoried, never proof-replayed.
  let generatedRuntime : Array Name := #[`Komorebi.Seed.instReprOperatorExpr.repr._unsafe_rec, `Komorebi.FiniteDifference.iteratedWeightedDiff._unsafe_rec, `Komorebi.FiniteDifference.iteratedDiff._unsafe_rec, `Komorebi.Seed.OperatorExpr.eval._unsafe_rec, `Komorebi.PaperII.TransferZeta.PositiveWeightedMultigraph.IsWalk._unsafe_rec]
  let mut counts : Array Nat := ownedModules.map (fun _ => 0)
  let mut total : Nat := 0
  let mut outside : Nat := 0
  for (name, info) in env.checked.get.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let owner := moduleNames[idx.toNat]!
      for mi in [:ownedModules.size] do
        if owner == ownedModules[mi]! then
          total := total + 1
          counts := counts.modify mi (· + 1)
          let inNamespace := Name.isPrefixOf `Komorebi name || Name.isPrefixOf `KomorebiVerification name
          unless inNamespace do outside := outside + 1
          if info.isUnsafe then throwError "OWNED AUDIT REJECTED unsafe: {name}"
          if info.isPartial && !(generatedRuntime.contains name) then
            throwError "OWNED AUDIT REJECTED unreviewed partial declaration: {name}"
          if generatedRuntime.contains name && !info.isPartial then
            throwError "OWNED AUDIT REJECTED runtime classification changed: {name}"
          if !info.isPartial then
            let dependencies := info.getUsedConstantsAsSet
            for helper in generatedRuntime do
              if dependencies.contains helper then
                throwError "OWNED AUDIT REJECTED logical runtime-helper dependency: {name} -> {helper}"
          match info with
          | .axiomInfo _ => throwError "OWNED AUDIT REJECTED axiom: {name}"
          | .opaqueInfo _ => throwError "OWNED AUDIT REJECTED opaque: {name}"
          | _ => pure ()
          let axioms ← Lean.collectAxioms name
          for ax in axioms do
            unless ax == ``propext || ax == ``Classical.choice || ax == ``Quot.sound do
              throwError "OWNED AUDIT REJECTED dependency {ax}: {name}"
          let kind := match info with
            | .thmInfo _ => "theorem"
            | .defnInfo _ => "definition"
            | .inductInfo _ => "inductive"
            | .ctorInfo _ => "constructor"
            | .recInfo _ => "recursor"
            | .quotInfo _ => "quotient"
            | .axiomInfo _ => "axiom"
            | .opaqueInfo _ => "opaque"
          let row := Json.mkObj [
            ("module", toJson owner.toString), ("name", toJson name.toString),
            ("kind", toJson kind), ("in_project_namespace", toJson inNamespace),
            ("runtime_only", toJson info.isPartial),
            ("type_expr", toJson (if info.isPartial then reprStr info.type else "")),
            ("value_expr", toJson (if info.isPartial then (info.value? (allowOpaque := true)).map reprStr else none)),
            ("level_params", toJson (if info.isPartial then info.levelParams.map Name.toString else [])),
            ("axioms", toJson (axioms.map Name.toString))]
          liftIO <| IO.println ("OWNED " ++ row.compress)
  if total == 0 then throwError "OWNED AUDIT REJECTED empty inventory"
  for mi in [:ownedModules.size] do
    let m := ownedModules[mi]!
    if !(#[`KomorebiVerification.PaperII, `KomorebiVerification, `KomorebiVerification.PaperII.KernelAudit, `KomorebiVerification.PaperII.ReleaseDefectKernelAudit, `PaperIIRefinement, `ReleaseAudit]).contains m && counts[mi]! == 0 then
      throwError "OWNED AUDIT REJECTED missing declaration-bearing module: {m}"
    liftIO <| IO.println s!"OWNED_MODULE {m} {counts[mi]!}"
  liftIO <| IO.println s!"OWNED_AUDIT_PASS {total} OUTSIDE_NAMESPACE {outside}"
