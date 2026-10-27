import KomorebiVerification.ProjectorCore
import KomorebiVerification.ExactCoordinates
import KomorebiVerification.FibreRefinement
import KomorebiVerification.ResidueProjectors
import KomorebiVerification.PaperII.NestedRefinement
import KomorebiVerification.PaperII.ResidueFourierCRT
import KomorebiVerification.PaperII.WeightedTransfer
import KomorebiVerification.PaperII.TransferZeta
import KomorebiVerification.PaperII.ResultantSeparation
import KomorebiVerification.PaperII.SmithDyadic
import KomorebiVerification.PaperII.LinearDefects
import KomorebiVerification.PaperII.TypedLinearDefects
import KomorebiVerification.PaperII
import KomorebiVerification
import KomorebiVerification.PaperII.KernelAudit
import KomorebiVerification.PaperII.CommonRefinement
import KomorebiVerification.PaperII.FiniteCommonRefinement
import KomorebiVerification.PaperII.CommonRefinementConsumers
import PaperIIRefinement
import ReleaseAudit
open Lean Meta Elab Command
set_option maxHeartbeats 8000000
run_cmd do
  let env ← getEnv
  let modules : Array Name := #[`KomorebiVerification.ProjectorCore, `KomorebiVerification.ExactCoordinates, `KomorebiVerification.FibreRefinement, `KomorebiVerification.ResidueProjectors, `KomorebiVerification.PaperII.NestedRefinement, `KomorebiVerification.PaperII.ResidueFourierCRT, `KomorebiVerification.PaperII.WeightedTransfer, `KomorebiVerification.PaperII.TransferZeta, `KomorebiVerification.PaperII.ResultantSeparation, `KomorebiVerification.PaperII.SmithDyadic, `KomorebiVerification.PaperII.LinearDefects, `KomorebiVerification.PaperII.TypedLinearDefects, `KomorebiVerification.PaperII, `KomorebiVerification, `KomorebiVerification.PaperII.KernelAudit, `KomorebiVerification.PaperII.CommonRefinement, `KomorebiVerification.PaperII.FiniteCommonRefinement, `KomorebiVerification.PaperII.CommonRefinementConsumers, `PaperIIRefinement, `ReleaseAudit]
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
