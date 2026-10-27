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
import KomorebiVerification.PaperII.ReleaseDefectPolynomial
import KomorebiVerification.PaperII.ReleaseAnalyticContourSup
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
import KomorebiVerification.PaperII.ReleaseRectifiableLength
import KomorebiVerification.PaperII.ReleaseRectifiableRSError
import KomorebiVerification.PaperII.ReleaseRectifiableDefect
import ReleaseCyclePrimitive
import KomorebiVerification.PaperII.ReleaseCycleParameter
import KomorebiVerification.PaperII.ReleaseCycleDecay
import KomorebiVerification.PaperII.ReleaseCycleWinding
import KomorebiVerification.PaperII.ReleaseCycleDixon
import KomorebiVerification.PaperII.ReleaseCycleDSlope
import KomorebiVerification.PaperII.ReleaseCycleCauchy
import KomorebiVerification.PaperII.ReleaseCanonicalHFC
import KomorebiVerification.PaperII.ReleaseCanonicalNaturality
import KomorebiVerification.PaperII.ReleaseCanonicalDefect
import KomorebiVerification
import KomorebiVerification.PaperII.KernelAudit
import KomorebiVerification.PaperII.ReleaseDefectKernelAudit
import PaperIIRefinement
import ReleaseAudit
open Lean Meta Elab Command
set_option maxHeartbeats 8000000
run_cmd do
  let env ← getEnv
  let modules : Array Name := #[`KomorebiVerification.ProjectorCore, `KomorebiVerification.ExactCoordinates, `KomorebiVerification.PaperII.NestedRefinement, `KomorebiVerification.FibreRefinement, `KomorebiVerification.ResidueProjectors, `KomorebiVerification.PaperII.ResidueFourierCRT, `KomorebiVerification.PaperII.WeightedTransfer, `KomorebiVerification.PaperII.TransferZeta, `KomorebiVerification.PaperII.ResultantSeparation, `KomorebiVerification.PaperII.SmithDyadic, `KomorebiVerification.PaperII.LinearDefects, `KomorebiVerification.PaperII.TypedLinearDefects, `KomorebiVerification.PaperII.CommonRefinement, `KomorebiVerification.PaperII.FiniteCommonRefinement, `KomorebiVerification.PaperII.CommonRefinementConsumers, `KomorebiVerification.PaperII.ReleaseCoordinatesAlgebra, `KomorebiVerification.PaperII.ReleaseCoordinatesHilbert, `KomorebiVerification.PaperII.ReleaseCoordinatesResidue, `KomorebiVerification.PaperII.ReleaseCoordinatesFourier, `KomorebiVerification.PaperII.ReleaseCoordinatesConsumers, `KomorebiVerification.PaperII.ReleaseFiltered, `KomorebiVerification.PaperII.ReleaseFilteredPaths, `KomorebiVerification.PaperII.ReleaseResultantPolynomial, `KomorebiVerification.PaperII.ReleaseResultantPackets, `KomorebiVerification.PaperII.ReleaseResultantIntegralPackets, `KomorebiVerification.PaperII.ReleaseGluing, `KomorebiVerification.PaperII.ReleaseGluingDVR, `KomorebiVerification.PaperII.ReleasePrecision, `KomorebiVerification.PaperII.ReleaseGluingPrecisionBridge, `KomorebiVerification.PaperII.ReleaseResultantDVR, `KomorebiVerification.PaperII.ReleaseGluingBinary, `KomorebiVerification.PaperII.ReleaseGluingSmith, `KomorebiVerification.PaperII.ReleaseGluingFinite, `KomorebiVerification.PaperII.ReleaseGluingEquivSmith, `KomorebiVerification.PaperII.ReleaseGluingMatrix, `KomorebiVerification.PaperII.ReleaseGluingPacketBridge, `KomorebiVerification.PaperII.ReleasePrecisionQuotient, `KomorebiVerification.PaperII.ReleaseDefectTower, `KomorebiVerification.PaperII.ReleaseAnalyticExponential, `KomorebiVerification.PaperII.ReleaseAnalyticContour, `KomorebiVerification.PaperII.ReleaseDefectCompatibility, `KomorebiVerification.PaperII.ReleaseDefectPolynomial, `KomorebiVerification.PaperII.ReleaseAnalyticContourSup, `KomorebiVerification.PaperII.ReleaseTransferMatrix, `KomorebiVerification.PaperII.ReleaseTransferScalar, `KomorebiVerification.PaperII.ReleaseTransferMultigraded, `KomorebiVerification.PaperII.ReleaseTransferMultigradedRational, `KomorebiVerification.PaperII.ReleaseTransferConsequences, `KomorebiVerification.PaperII.ReleaseSmithDVR, `KomorebiVerification.PaperII.ReleaseSmithRectangular, `KomorebiVerification.PaperII.ReleaseSmithTransport, `KomorebiVerification.PaperII.ReleaseSmithSign, `KomorebiVerification.PaperII.ReleaseSmithCharacters, `KomorebiVerification.PaperII.ReleaseRectifiable, `KomorebiVerification.PaperII.ReleaseArcLength, `KomorebiVerification.PaperII.ReleaseRectifiableCycle, `KomorebiVerification.PaperII, `KomorebiVerification.PaperII.ReleaseRectifiableLength, `KomorebiVerification.PaperII.ReleaseRectifiableRSError, `KomorebiVerification.PaperII.ReleaseRectifiableDefect, `ReleaseCyclePrimitive, `KomorebiVerification.PaperII.ReleaseCycleParameter, `KomorebiVerification.PaperII.ReleaseCycleDecay, `KomorebiVerification.PaperII.ReleaseCycleWinding, `KomorebiVerification.PaperII.ReleaseCycleDixon, `KomorebiVerification.PaperII.ReleaseCycleDSlope, `KomorebiVerification.PaperII.ReleaseCycleCauchy, `KomorebiVerification.PaperII.ReleaseCanonicalHFC, `KomorebiVerification.PaperII.ReleaseCanonicalNaturality, `KomorebiVerification.PaperII.ReleaseCanonicalDefect, `KomorebiVerification, `KomorebiVerification.PaperII.KernelAudit, `KomorebiVerification.PaperII.ReleaseDefectKernelAudit, `PaperIIRefinement, `ReleaseAudit]
  let mut owned : Array (Name × ConstantInfo × Name) := #[]
  let mut helpers : Array Name := #[]
  for (name, info) in env.checked.get.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let owner := env.header.moduleNames[idx.toNat]!
      if modules.contains owner then
        owned := owned.push (name, info, owner)
        if info.isPartial then helpers := helpers.push name
  let mut references : Nat := 0
  for (name, info, owner) in owned do
    if info.isUnsafe then throwError "UNSAFE OWNED DECLARATION {name}"
    if !info.isPartial then
      let used := info.getUsedConstantsAsSet
      for helper in helpers do
        if used.contains helper then
          references := references + 1
          logInfo m!"LOGICAL_HELPER_REFERENCE {name} {helper}"
    else
      let parent := name.getPrefix
      let some parentInfo := env.find? parent | throwError "Missing logical parent {parent}"
      let body := info.value? (allowOpaque := true)
      let parentBody := parentInfo.value? (allowOpaque := true)
      let axioms ← Lean.collectAxioms name
      let row := Json.mkObj [
        ("name", toJson name.toString), ("module", toJson owner.toString),
        ("unsafe", toJson info.isUnsafe), ("partial", toJson info.isPartial),
        ("type_expr", toJson (reprStr info.type)),
        ("value_expr", toJson (body.map reprStr)),
        ("level_params", toJson (info.levelParams.map Name.toString)),
        ("parent", toJson parent.toString), ("parent_partial", toJson parentInfo.isPartial),
        ("parent_unsafe", toJson parentInfo.isUnsafe),
        ("parent_type_expr", toJson (reprStr parentInfo.type)),
        ("parent_value_expr", toJson (parentBody.map reprStr)),
        ("axioms", toJson (axioms.map Name.toString))]
      liftIO <| IO.println ("HELPER_REVIEW " ++ row.compress)
  if references != 0 then throwError "Logical dependency on runtime helper"
  logInfo m!"HELPER_DEPENDENCY_SEPARATION_PASS OWNED {owned.size} HELPERS {helpers.size} REFERENCES {references}"
