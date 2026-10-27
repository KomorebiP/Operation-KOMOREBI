from pathlib import Path
root=Path(__file__).resolve().parents[3]
p=root/'release_work/runtime/release_audit/ReplayClosure.lean'
s=p.read_text().replace('between project modules. It is not an independent verifier.', '''between project modules. One reviewed, exactly identical upstream theorem is
checked under a fresh audit-only name because official replay skips duplicate
theorem names. Fresh-name replay and duplicate-body checks are counted separately.
It is not an independent verifier.''')
s=s.replace('  let mut heldRegions', '  let mut owners : Std.HashMap Name Name := {}\n  let mut heldRegions')
s=s.replace('constants := constants.insert name ci\n        IO.println ("REPLAY_CHECKED "', 'constants := constants.insert name ci\n        owners := owners.insert name module\n        IO.println ("REPLAY_CANDIDATE "')
s=s.replace('''  for (name, _) in constants.toList do
    if (env.toKernelEnv.find? name).isSome then
      throw <| IO.userError s!"Starting environment already trusts {name}"
  IO.println s!"REPLAY_UPSTREAM_ONLY_PASS {upstream.size}"''','''  let mut duplicates : Array (TheoremVal × Name) := #[]
  for (name, ci) in constants.toList do
    if let some old := env.toKernelEnv.find? name then
      -- An exact-name exception, reviewed against the pinned upstream source.
      -- No other overlap, declaration kind, mutual block, or changed body passes.
      unless name == `ContinuousLinearMap.codRestrict.congr_simp do
        throw <| IO.userError s!"Unreviewed starting-environment overlap {name}"
      let some idx := env.getModuleIdxFor? name
        | throw <| IO.userError s!"Unknown upstream owner for {name}"
      let upstreamOwner := env.header.moduleNames[idx.toNat]!
      unless upstreamOwner == `Mathlib.Analysis.LocallyConvex.HahnBanach do
        throw <| IO.userError s!"Unexpected upstream owner for {name}"
      match ci, old with
      | .thmInfo a, .thmInfo b =>
        unless a.name == b.name && a.type == b.type &&
            a.levelParams == b.levelParams && a.all == b.all && a.value == b.value &&
            a.all == [name] do
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
    let freshName := Name.str original.name "_paperIReplayBody"
    if (startingKernel.find? freshName).isSome || constants.contains freshName then
      throw <| IO.userError s!"Audit theorem name is not fresh: {freshName}"
    let mut fresh := { original with name := freshName, all := [freshName] }
    if corruptDuplicate then
      fresh := { fresh with value := mkNatLit 0 }
      IO.println "REPLAY_DUPLICATE_CORRUPT_CONTROL_INJECTED"
    -- This public kernel API checks the theorem's proof body at its unchanged type.
    match startingKernel.addDeclCore 0 0 (.thmDecl fresh) (cancelTk? := none) with
    | .error ex => throw <| IO.userError <| (← ex.toMessageData {} |>.toString)
    | .ok checked => startingKernel := checked
    let some (.thmInfo stored) := startingKernel.find? freshName
      | throw <| IO.userError s!"Kernel did not add fresh theorem {freshName}"
    unless stored.type == original.type && stored.value == original.value &&
        stored.levelParams == original.levelParams && stored.all == [freshName] do
      throw <| IO.userError s!"Fresh theorem body changed for {original.name}"
    IO.println ("REPLAY_UPSTREAM_DUPLICATE_RECHECKED " ++ (Json.mkObj [
      ("name", toJson original.name.toString), ("audit_name", toJson freshName.toString),
      ("module", toJson (owners[original.name]!).toString),
      ("upstream_owner", toJson upstreamOwner.toString),
      ("same_name", toJson true), ("same_type", toJson true),
      ("same_level_params", toJson true), ("same_all", toJson true),
      ("same_value", toJson true), ("fresh_kernel_body_check", toJson true)]).compress)''')
s=s.replace('let result ← env.toKernelEnv.replay constants','let result ← startingKernel.replay constants')
s=s.replace('''  IO.println s!"REPLAY_CLOSURE_PASS MODULES {modules.size} CONSTANTS {constants.size} REGIONS {heldRegions.size}"''','''  for (name, _) in constants.toList do
    unless duplicates.any (fun d ↦ d.1.name == name) do
      IO.println ("REPLAY_CHECKED " ++ (Json.mkObj [
        ("module", toJson (owners[name]!).toString), ("name", toJson name.toString)]).compress)
  IO.println s!"REPLAY_CLOSURE_PASS MODULES {modules.size} CONSTANTS {constants.size} NEW_NAME_REPLAYS {constants.size - duplicates.size} DUPLICATE_BODY_RECHECKS {duplicates.size} REGIONS {heldRegions.size}"''')
(root/'release_work/runtime/overlap_review/ReplayClosureCandidate.lean').write_text(s)
