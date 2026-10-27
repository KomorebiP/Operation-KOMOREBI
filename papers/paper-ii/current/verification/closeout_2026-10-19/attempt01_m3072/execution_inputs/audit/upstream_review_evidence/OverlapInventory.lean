import LeanChecker

/-!
Audit instrumentation only. This wrapper uses Lean's official kernel replay,
loading upstream imports but NO project modules into the starting environment.
The compiled production closure is rechecked together, including dependencies
between project modules. Every overlap with an upstream declaration is rejected.
No runtime-helper exception or upstream duplicate exception is preapproved.
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
  let mut overlaps : Nat := 0
  for (name, ci) in constants.toList do
    if let some old := env.toKernelEnv.find? name then
      overlaps := overlaps + 1
      let some idx := env.getModuleIdxFor? name
        | throw <| IO.userError s!"No upstream owner: {name}"
      let upstreamOwner := env.header.moduleNames[idx.toNat]!
      match ci, old with
      | .thmInfo a, .thmInfo b =>
        IO.println ("OVERLAP_REVIEW " ++ (Json.mkObj [
          ("name", toJson name.toString), ("serialized_in", toJson (owners[name]!).toString),
          ("upstream_owner", toJson upstreamOwner.toString),
          ("same_name",toJson (a.name == b.name)), ("same_type",toJson (a.type == b.type)),
          ("same_value",toJson (a.value == b.value)), ("same_level_params",toJson (a.levelParams == b.levelParams)),
          ("same_all",toJson (a.all == b.all)), ("single_theorem",toJson (a.all == [name])),
          ("self_reference",toJson (ci.getUsedConstantsAsSet.contains name)),
          ("project_type_expr",toJson (reprStr a.type)), ("project_value_expr",toJson (reprStr a.value)),
          ("upstream_type_expr",toJson (reprStr b.type)), ("upstream_value_expr",toJson (reprStr b.value)),
          ("level_params",toJson (a.levelParams.map Name.toString)),
          ("all",toJson (a.all.map Name.toString)),
          ("used_constants",toJson (ci.getUsedConstantsAsSet.toList.map Name.toString))]).compress)
      | _, _ => throw <| IO.userError s!"Non-theorem overlap {name}"
  IO.println s!"OVERLAP_INVENTORY_PASS RAW_LOGICAL {constants.size} OVERLAPS {overlaps} UPSTREAM_IMPORTS {upstream.size}"
  env.freeRegions

#eval replayProductionClosure
