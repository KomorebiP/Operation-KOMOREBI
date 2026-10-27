import LeanChecker

/-!
Audit instrumentation, not a mathematical proof module. Rebuild the kernel
constant closure with no production module in the starting environment.
All unsafe declarations, unreviewed partial implementations and all upstream name overlaps are rejected. Fourteen exact inherited code-generation helpers are inventoried separately and cannot be used by a logical production declaration.
Uses the pinned official Lean kernel; not an independent proof assistant.
-/
open Lean

unsafe def replayPaperIII : IO Unit := do
  let modules : Array Name := #[
    `KomorebiPaperIII.EdgeOperators, `KomorebiPaperIII.EdgeExtensions,
    `KomorebiPaperIII.Transport, `KomorebiPaperIII.ReversibleConnections,
    `KomorebiPaperIII.CoordinateNaturality, `KomorebiPaperIII.NonlinearObstructions,
    `KomorebiPaperIII.HolonomyBlocks, `KomorebiPaperIII.PacketCoordinates,
    `KomorebiPaperIII.NonlinearPacketCoordinates, `KomorebiPaperIII.PacketDirectSum,
    `KomorebiPaperIII, `PaperIIIContinuation]
  let generatedRuntime : Array Name := #[ `Komorebi.PaperIII.EdgeOperators.heterogeneousPathSum._unsafe_rec, `Komorebi.PaperIII.NonlinearObstructions.OperationTree.eval._unsafe_rec, `Komorebi.PaperIII.Transport.ReversibleConnection.pathTransport._unsafe_rec, `Komorebi.PaperIII.Transport.pathEndpoint._unsafe_rec, `Komorebi.PaperIII.EdgeOperators.SupportedPath._unsafe_rec, `Komorebi.PaperIII.Transport.exactPathTransport._unsafe_rec, `Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.terminalTarget._unsafe_rec, `Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.wordOp._unsafe_rec, `Komorebi.PaperIII.EdgeOperators.heterogeneousProduct._unsafe_rec, `Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.Composable._unsafe_rec, `Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.wordExpansion._unsafe_rec, `Komorebi.PaperIII.EdgeOperators.PacketGraph.EdgeSystem.reverseCoefficient._unsafe_rec, `Komorebi.PaperIII.NonlinearObstructions.OperationTree.inputs._unsafe_rec, `Komorebi.PaperIII.Transport.ReversibleConnection.indexedPathTransport._unsafe_rec ]
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
        unless upstream.any (fun j => j.module == imp.module) do
          upstream := upstream.push { imp with importAll := true }
    let some last := parts[parts.size - 1]? | throw <| IO.userError "No private module data"
    let data := last.1
    for name in data.constNames, ci in data.constants do
      if ci.isUnsafe then
        throw <| IO.userError s!"Unsafe production declaration {name}"
      if ci.isPartial then
        unless generatedRuntime.contains name do
          throw <| IO.userError s!"Unreviewed partial production declaration {name}"
        IO.println s!"REPLAY_EXCLUDED_GENERATED_RUNTIME {module} {name}"
        continue
      if generatedRuntime.contains name then
        throw <| IO.userError s!"Generated runtime classification changed {name}"
      for helper in generatedRuntime do
        if ci.getUsedConstantsAsSet.contains helper then
          throw <| IO.userError s!"Logical dependency on generated runtime: {name} -> {helper}"
      if let some old := constants[name]? then
        match old, ci with
        | .thmInfo a, .thmInfo b =>
          unless a.type == b.type && a.levelParams == b.levelParams && a.all == b.all && a.value == b.value do
            throw <| IO.userError s!"Incompatible duplicate theorem {name}"
          IO.println s!"REPLAY_IDENTICAL_THEOREM_COPY {module} {name}"
        | _, _ => throw <| IO.userError s!"Non-theorem duplicate {name}"
      else
        constants := constants.insert name ci
        owners := owners.insert name module
    IO.println s!"REPLAY_MODULE {module} {data.constNames.size}"
  let (_, state) ← importModulesCore upstream |>.run
  let env ← finalizeImport state upstream {} 0 false false (isModule := true)
  for module in modules do
    if env.header.moduleNames.contains module then
      throw <| IO.userError s!"Production already present in starting environment: {module}"
  for (name, _) in constants.toList do
    if (env.toKernelEnv.find? name).isSome then
      throw <| IO.userError s!"Unreviewed upstream name overlap: {name}"
  IO.println s!"REPLAY_UPSTREAM_ONLY_PASS {upstream.size} OVERLAPS 0"
  if (← IO.getEnv "KOMOREBI_REPLAY_CORRUPT") == some "1" then
    let name := `PaperIIIReplayControl.falseEquality
    let type := mkApp3 (mkConst ``Eq [Level.succ Level.zero]) (mkConst ``Nat) (mkNatLit 0) (mkNatLit 1)
    let value := mkApp2 (mkConst ``Eq.refl [Level.succ Level.zero]) (mkConst ``Nat) (mkNatLit 0)
    constants := constants.insert name (.thmInfo { name, levelParams := [], type, value })
    owners := owners.insert name `PaperIIIReplayControl
    IO.println "REPLAY_CORRUPT_CONTROL_INJECTED"
  let result ← env.toKernelEnv.replay constants
  for (name, _) in constants.toList do
    unless (result.find? name).isSome do
      throw <| IO.userError s!"Kernel did not produce {name}"
    IO.println ("REPLAY_CHECKED " ++ (Json.mkObj [
      ("module", toJson (owners[name]!).toString), ("name", toJson name.toString)]).compress)
  IO.println s!"REPLAY_CLOSURE_PASS MODULES {modules.size} CONSTANTS {constants.size} REGIONS {heldRegions.size}"
  env.freeRegions

#eval replayPaperIII
