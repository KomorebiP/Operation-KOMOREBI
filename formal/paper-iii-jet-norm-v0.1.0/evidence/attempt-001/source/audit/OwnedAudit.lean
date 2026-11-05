import KomorebiPaperIIIJetNorm
open Lean Meta Elab Command

run_cmd do
  let env ← getEnv
  let ownedModules : Array Name := #[`KomorebiPaperIII.PacketCoordinates, `KomorebiPaperIII.MultilinearPacketJets, `KomorebiPaperIII.BoundedPacketJetNorm, `KomorebiPaperIII.ContinuousPacketJets, `KomorebiPaperIIIJetNorm.Bounds, `KomorebiPaperIIIJetNorm]
  let mut total := 0
  for (name, info) in env.checked.get.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let owner := env.header.moduleNames[idx.toNat]!
      if ownedModules.contains owner then
        total := total + 1
        if info.isUnsafe then throwError "OWNED AUDIT REJECTED unsafe: {name}"
        if info.isPartial then throwError "OWNED AUDIT REJECTED partial: {name}"
        match info with
        | .axiomInfo _ => throwError "OWNED AUDIT REJECTED axiom: {name}"
        | .opaqueInfo _ => throwError "OWNED AUDIT REJECTED opaque: {name}"
        | _ => pure ()
        let axioms ← Lean.collectAxioms name
        for ax in axioms do
          unless ax == ``propext || ax == ``Classical.choice || ax == ``Quot.sound do
            throwError "OWNED AUDIT REJECTED dependency {ax}: {name}"
        liftIO <| IO.println ("OWNED " ++ (Json.mkObj [
          ("module", toJson owner.toString), ("name", toJson name.toString),
          ("axioms", toJson (axioms.map Name.toString))]).compress)
  if total == 0 then throwError "OWNED AUDIT REJECTED empty inventory"
  liftIO <| IO.println s!"OWNED_AUDIT_PASS {total}"
