import LeanChecker

/-!
Audit instrumentation only. This wrapper uses Lean's official kernel replay,
loading upstream imports but NO project modules into the starting environment.
The compiled production closure is rechecked together, including dependencies
between project modules. One reviewed, exactly identical upstream theorem is
checked under a fresh audit-only name because official replay skips duplicate
theorem names. Fresh-name replay and duplicate-body checks are counted separately.
It is not an independent verifier.
-/
open Lean

unsafe def replayProductionClosure : IO Unit := do
  let some raw ← IO.getEnv "KOMOREBI_REPLAY_MODULES"
    | throw <| IO.userError "KOMOREBI_REPLAY_MODULES is required"
  let modules := (raw.splitOn ",").toArray.map String.toName
  if modules.isEmpty || modules.any Name.isAnonymous then
    throw <| IO.userError "Empty replay closure is forbidden"
  let mut upstream : Array Import := #[]
  let mut constants : Std.HashMap Name ConstantInfo := {}
  let mut owners : Std.HashMap Name Name := {}
  let mut heldRegions : Array CompactedRegion := #[]
  for module in modules do
    let mFile ← findOLean module
    let mut files := #[mFile]
    let server := OLeanLevel.server.adjustFileName mFile
    if ← server.pathExists then
      files := files.push server
      let priv := OLeanLevel.private.adjustFileName mFile
      if ← priv.pathExists then files := files.push priv
    let parts ← readModuleDataParts files
    for part in parts do heldRegions := heldRegions.push part.2
    let some first := parts[0]? | throw <| IO.userError s!"No data for {module}"
    for imp in first.1.imports do
      unless modules.contains imp.module do
        unless upstream.any (fun j ↦ j.module == imp.module) do
          upstream := upstream.push { imp with importAll := true }
    let some last := parts[parts.size - 1]? | throw <| IO.userError "Missing final module part"
    let data := last.1
    for name in data.constNames, ci in data.constants do
      if let some previous := constants[name]? then
        match previous, ci with
        | .thmInfo a, .thmInfo b =>
          unless a.type == b.type && a.levelParams == b.levelParams &&
              a.all == b.all && a.value == b.value do
            throw <| IO.userError s!"Incompatible duplicate theorem {name}"
          IO.println ("REPLAY_IDENTICAL_DUPLICATE " ++ (Json.mkObj [
            ("module", toJson module.toString), ("name", toJson name.toString)]).compress)
        | _, _ => throw <| IO.userError s!"Non-theorem duplicate {name}"
      else if ci.isUnsafe || ci.isPartial then
        IO.println ("REPLAY_RUNTIME_ONLY " ++ (Json.mkObj [
          ("module", toJson module.toString), ("name", toJson name.toString),
          ("unsafe", toJson ci.isUnsafe), ("partial", toJson ci.isPartial)]).compress)
      else
        constants := constants.insert name ci
        owners := owners.insert name module
        IO.println ("REPLAY_CANDIDATE " ++ (Json.mkObj [
          ("module", toJson module.toString), ("name", toJson name.toString)]).compress)
    IO.println s!"REPLAY_CLOSURE_MODULE {module} {data.constNames.size}"
  let (_, state) ← importModulesCore upstream |>.run
  let env ← finalizeImport state upstream {} 0 false false (isModule := true)
  for module in modules do
    if env.header.moduleNames.contains module then
      throw <| IO.userError s!"Starting environment already imports project module {module}"
  let mut duplicates : Array (TheoremVal × Name) := #[]
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
      ("same_value", toJson true), ("fresh_kernel_body_check", toJson true)]).compress)
  if (← IO.getEnv "KOMOREBI_REPLAY_CORRUPT") == some "1" then
    let name := `ClosureControl.falseEquality
    let type := mkApp3 (mkConst ``Eq [Level.succ Level.zero]) (mkConst ``Nat) (mkNatLit 0) (mkNatLit 1)
    let value := mkApp2 (mkConst ``Eq.refl [Level.succ Level.zero]) (mkConst ``Nat) (mkNatLit 0)
    constants := constants.insert name (.thmInfo { name, levelParams := [], type, value })
    IO.println "REPLAY_CORRUPT_CONTROL_INJECTED"
  let result ← startingKernel.replay constants
  for (name, _) in constants.toList do
    unless (result.find? name).isSome do
      throw <| IO.userError s!"Replay did not produce {name}"
  for (name, _) in constants.toList do
    unless duplicates.any (fun d ↦ d.1.name == name) do
      IO.println ("REPLAY_CHECKED " ++ (Json.mkObj [
        ("module", toJson (owners[name]!).toString), ("name", toJson name.toString)]).compress)
  IO.println s!"REPLAY_CLOSURE_PASS MODULES {modules.size} CONSTANTS {constants.size} NEW_NAME_REPLAYS {constants.size - duplicates.size} DUPLICATE_BODY_RECHECKS {duplicates.size} REGIONS {heldRegions.size}"
  env.freeRegions

#eval replayProductionClosure
