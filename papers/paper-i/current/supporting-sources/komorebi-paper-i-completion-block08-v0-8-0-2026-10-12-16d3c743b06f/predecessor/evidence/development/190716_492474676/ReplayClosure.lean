import LeanChecker

/-!
Audit instrumentation only. This wrapper uses Lean's official kernel replay,
loading upstream imports but NO project modules into the starting environment.
The compiled production closure is rechecked together, including dependencies
between project modules. It is not an independent verifier.
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
  for module in modules do
    let mFile ← findOLean module
    let mut files := #[mFile]
    let server := OLeanLevel.server.adjustFileName mFile
    if ← server.pathExists then
      files := files.push server
      let priv := OLeanLevel.private.adjustFileName mFile
      if ← priv.pathExists then files := files.push priv
    let parts ← readModuleDataParts files
    if parts.isEmpty then throw <| IO.userError s!"No data for {module}"
    for imp in parts[0]!.1.imports do
      unless modules.contains imp.module do
        unless upstream.any (fun j ↦ j.module == imp.module) do
          upstream := upstream.push { imp with importAll := true }
    let data := parts[parts.size - 1]!.1
    for name in data.constNames, ci in data.constants do
      if constants.contains name then
        throw <| IO.userError s!"Duplicate project declaration {name}"
      if ci.isUnsafe || ci.isPartial then
        throw <| IO.userError s!"Replay refuses skipped declaration {name}"
      constants := constants.insert name ci
    IO.println s!"REPLAY_CLOSURE_MODULE {module} {data.constNames.size}"
  let (_, state) ← importModulesCore upstream |>.run
  let env ← finalizeImport state upstream {} 0 false false (isModule := true)
  for module in modules do
    if env.header.moduleNames.contains module then
      throw <| IO.userError s!"Starting environment already imports project module {module}"
  for (name, _) in constants.toList do
    if (env.toKernelEnv.find? name).isSome then
      throw <| IO.userError s!"Starting environment already trusts {name}"
  IO.println s!"REPLAY_UPSTREAM_ONLY_PASS {upstream.size}"
  if (← IO.getEnv "KOMOREBI_REPLAY_CORRUPT") == some "1" then
    let name := `ClosureControl.falseEquality
    let type := mkApp3 (mkConst ``Eq [Level.zero]) (mkConst ``Nat) (mkNatLit 0) (mkNatLit 1)
    let value := mkApp2 (mkConst ``Eq.refl [Level.zero]) (mkConst ``Nat) (mkNatLit 0)
    constants := constants.insert name (.thmInfo { name, levelParams := [], type, value })
    IO.println "REPLAY_CORRUPT_CONTROL_INJECTED"
  let result ← env.toKernelEnv.replay constants
  for (name, _) in constants.toList do
    unless (result.find? name).isSome then
      throw <| IO.userError s!"Replay did not produce {name}"
  IO.println s!"REPLAY_CLOSURE_PASS MODULES {modules.size} CONSTANTS {constants.size}"
  env.freeRegions

#eval replayProductionClosure
