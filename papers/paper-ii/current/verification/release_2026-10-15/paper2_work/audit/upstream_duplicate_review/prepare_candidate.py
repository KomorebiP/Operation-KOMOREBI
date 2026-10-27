from pathlib import Path
import difflib,json,hashlib
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent;official=root/'paper2_work/tools/final_audit'
s=(official/'ReplayClosure.lean').read_text();old='''  for (name, _) in constants.toList do
    if (env.toKernelEnv.find? name).isSome then
      throw <| IO.userError s!"Unreviewed starting-environment overlap {name}"
  IO.println s!"REPLAY_UPSTREAM_ONLY_PASS {upstream.size} REVIEWED_THEOREM_OVERLAPS 0"
  let startingKernel := env.toKernelEnv
'''
new=r'''  let mut duplicates : Array (TheoremVal × Name) := #[]
  for (name, ci) in constants.toList do
    if let some old := env.toKernelEnv.find? name then
      -- Only this exact independently reviewed lazy upstream equation theorem.
      unless name == `Submodule.factor.eq_1 &&
          owners[name]? == some `KomorebiVerification.PaperII.ReleaseGluing do
        throw <| IO.userError s!"Unreviewed starting-environment overlap {name}"
      let some idx := env.getModuleIdxFor? name
        | throw <| IO.userError s!"Unknown upstream owner for {name}"
      let upstreamOwner := env.header.moduleNames[idx.toNat]!
      unless upstreamOwner == `Mathlib.RingTheory.AdicCompletion.Basic do
        throw <| IO.userError s!"Unexpected upstream owner for {name}"
      match ci, old with
      | .thmInfo a, .thmInfo b =>
        unless a.name == b.name && a.type == b.type && a.value == b.value &&
            a.levelParams == b.levelParams && a.all == b.all && a.all == [name] do
          throw <| IO.userError s!"Nonidentical or mutual upstream theorem {name}"
        if ci.getUsedConstantsAsSet.contains name then
          throw <| IO.userError s!"Self-referencing upstream theorem {name}"
        duplicates := duplicates.push (a, upstreamOwner)
      | _, _ => throw <| IO.userError s!"Non-theorem upstream overlap {name}"
  IO.println s!"REPLAY_UPSTREAM_ONLY_PASS {upstream.size} REVIEWED_THEOREM_OVERLAPS {duplicates.size}"
  let corruptDuplicate := (← IO.getEnv "KOMOREBI_REPLAY_DUPLICATE_CORRUPT") == some "1"
  if corruptDuplicate && duplicates.isEmpty then
    throw <| IO.userError "Duplicate corrupt control requires a reviewed duplicate"
  let mut startingKernel := env.toKernelEnv
  for (original, upstreamOwner) in duplicates do
    let freshName := Name.str original.name "_paperIIReplayBody"
    if (startingKernel.find? freshName).isSome || constants.contains freshName then
      throw <| IO.userError s!"Audit theorem name is not fresh: {freshName}"
    let mut fresh := { original with name := freshName, all := [freshName] }
    if corruptDuplicate then
      fresh := { fresh with value := mkNatLit 0 }
      IO.println "REPLAY_DUPLICATE_CORRUPT_CONTROL_INJECTED"
    -- Direct kernel type/body check; not replay's existing-name shortcut.
    match startingKernel.addDeclCore 0 0 (.thmDecl fresh) (cancelTk? := none) with
    | .error ex => throw <| IO.userError <| (← ex.toMessageData {} |>.toString)
    | .ok checked => startingKernel := checked
    let some (.thmInfo stored) := startingKernel.find? freshName
      | throw <| IO.userError s!"Kernel did not add fresh theorem {freshName}"
    unless stored.type == original.type && stored.value == original.value &&
        stored.levelParams == original.levelParams && stored.all == [freshName] do
      throw <| IO.userError s!"Fresh theorem body changed for {original.name}"
    IO.println ("REPLAY_UPSTREAM_DUPLICATE_RECHECKED " ++ (Json.mkObj [
      ("name",toJson original.name.toString), ("audit_name",toJson freshName.toString),
      ("serialized_in",toJson (owners[original.name]!).toString),
      ("upstream_owner",toJson upstreamOwner.toString),
      ("type_expr",toJson (reprStr original.type)),
      ("value_expr",toJson (reprStr original.value)),
      ("level_params",toJson (original.levelParams.map Name.toString)),
      ("all",toJson (original.all.map Name.toString)),
      ("fresh_kernel_body_check",toJson true)]).compress)
    -- Not source-owned: retain upstream identity only after independent body check.
    constants := constants.erase original.name
'''
assert old in s;s=s.replace(old,new).replace('between project modules. Every overlap with an upstream declaration is rejected.\nNo runtime-helper exception or upstream duplicate exception is preapproved.','between project modules. One exact reviewed lazy upstream equation theorem is\nrechecked at its declared type under a fresh name. All other overlaps are rejected.').replace('DUPLICATE_BODY_RECHECKS 0 REGIONS','DUPLICATE_BODY_RECHECKS {duplicates.size} REGIONS')
(out/'ReplayClosureCandidate.lean').write_text(s)
(out/'ReplayClosure.diff').write_text(''.join(difflib.unified_diff((official/'ReplayClosure.lean').read_text().splitlines(True),s.splitlines(True),fromfile='current/ReplayClosure.lean',tofile='proposed/ReplayClosure.lean')))
