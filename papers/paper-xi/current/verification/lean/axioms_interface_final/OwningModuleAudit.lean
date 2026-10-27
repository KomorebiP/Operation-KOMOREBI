import PaperXI.SingleCandidateComparison
import Lean.Elab.Command
import Lean.Util.CollectAxioms

open Lean Elab Command

-- The release catalogue has 4,342 entries; elaborating its literal array
-- exceeds Lean's default recursion-depth guard before the audit can run.
set_option maxRecDepth 32768

private def auditKind : ConstantInfo → String
  | .axiomInfo _ => "axiom"
  | .defnInfo _ => "definition"
  | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque"
  | .quotInfo _ => "quotient"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"
  | .inductInfo _ => "inductive"

private def auditOwners : Array Name := #["PaperXI.SingleCandidateComparison".toName]
private def auditCatalogue : Array (Name × Name) := #[
  ("PaperXI.SingleCandidateComparison.source".toName, "PaperXI.SingleCandidateComparison".toName)
]

set_option maxHeartbeats 10000000 in
run_cmd do
  let env ← getEnv
  let allowed : Array Name := #[``Classical.choice, ``Quot.sound, ``propext]
  let mut forbidden : Nat := 0
  let mut count : Nat := 0
  let mut catalogueCount : Nat := 0
  let mut auxiliaryCount : Nat := 0
  let mut selectedIdxs : Std.HashSet ModuleIdx := {}
  for owner in auditOwners do
    let some idx := env.getModuleIdx? owner |
      throwError "Requested owning module is not imported: {owner}"
    selectedIdxs := selectedIdxs.insert idx
  let kernelEnv := (env.setExporting false).toKernelEnv
  let entries := (env.const2ModIdx.toList.filter (fun entry => selectedIdxs.contains entry.2)).toArray.qsort (fun a b => Name.lt a.1 b.1)
  for (name, expectedOwner) in auditCatalogue do
    let (kernelName, resolution) ← if (kernelEnv.find? name).isSome then
        pure (name, "direct")
      else do
        -- The retained catalogue records source names for private theorems.
        -- Resolve only a unique private kernel name in the stated owner.
        let privateCandidates := entries.filter fun (candidate, idx) =>
          env.header.moduleNames[idx.toNat]! == expectedOwner &&
          privateToUserName? candidate == some name &&
          (kernelEnv.find? candidate).isSome
        unless privateCandidates.size == 1 do
          throwError "Catalogue name is absent or ambiguous: {name}; private matches: {privateCandidates.size}"
        pure (privateCandidates[0]!.1, "private_user_name")
    let some idx := env.getModuleIdxFor? kernelName |
      throwError "Catalogue name has no imported owner: {name}"
    let owner := env.header.moduleNames[idx.toNat]!
    unless owner == expectedOwner do
      throwError "Catalogue owner mismatch for {name}: {owner} != {expectedOwner}"
    catalogueCount := catalogueCount + 1
    liftIO <| IO.println <| (Json.mkObj [
      ("event", toJson "catalogue"), ("name", toJson name.toString),
      ("kernel_name", toJson kernelName.toString),
      ("resolution", toJson resolution),
      ("module", toJson owner.toString)]).compress
  for (name, idx) in entries do
    let owner := env.header.moduleNames[idx.toNat]!
    if let some info := kernelEnv.find? name then
      let axioms ← collectAxioms name
      let extra := axioms.filter (fun ax => !allowed.contains ax)
      count := count + 1
      if !extra.isEmpty then forbidden := forbidden + 1
      liftIO <| IO.println <| (Json.mkObj [
        ("event", toJson "owned_constant"), ("name", toJson name.toString),
        ("module", toJson owner.toString), ("kind", toJson (auditKind info)),
        ("unsafe", toJson info.isUnsafe),
        ("axioms", toJson (axioms.map Name.toString)),
        ("forbidden_axioms", toJson (extra.map Name.toString))]).compress
    else
      auxiliaryCount := auxiliaryCount + 1
      liftIO <| IO.println <| (Json.mkObj [
        ("event", toJson "compiler_auxiliary"), ("name", toJson name.toString),
        ("module", toJson owner.toString)]).compress
  liftIO <| IO.println <| (Json.mkObj [
    ("event", toJson "summary"), ("owned_constant_count", toJson count),
    ("catalogue_count", toJson catalogueCount),
    ("compiler_auxiliary_count", toJson auxiliaryCount),
    ("forbidden_constant_count", toJson forbidden),
    ("requested_module_count", toJson auditOwners.size)]).compress
  unless forbidden == 0 do
    throwError "Nonstandard axioms found in {forbidden} owned constants"
