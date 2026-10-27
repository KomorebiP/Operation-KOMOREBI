import KomorebiSpaceRegularization
import Lean

set_option maxHeartbeats 0

open Lean Elab Command in
run_cmd do
  let env ← getEnv
  let wanted := ((← IO.FS.readFile "wanted_modules.txt").splitOn "\n").toArray
  let mut rows : Array Json := #[]
  let mut unexpected : Array Json := #[]
  for (name, ci) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let modName := env.header.moduleNames[idx.toNat]!
      if wanted.contains modName.toString then
        let axs ← collectAxioms name
        let kind := match ci with
          | .thmInfo _ => "theorem"
          | .defnInfo _ => "definition"
          | .opaqueInfo _ => "opaque"
          | .axiomInfo _ => "axiom"
          | .inductInfo _ => "inductive"
          | .ctorInfo _ => "constructor"
          | .recInfo _ => "recursor"
          | .quotInfo _ => "quotient"
        let newModule := ["KomorebiSpace.RegularizedHilbertRepair",
          "KomorebiSpace.RegularizationCertificates", "KomorebiSpace.ProtectedRegularizedRepair"].contains modName.toString
        let typeString ← if newModule && kind == "theorem" then
          liftTermElabM do return (← Meta.ppExpr ci.type).pretty
        else pure ""
        let row := Json.mkObj [("name", toJson name.toString),
          ("module", toJson modName.toString), ("kind", toJson kind),
          ("type", toJson typeString), ("unsafe", toJson ci.isUnsafe),
          ("axioms", toJson (axs.map Name.toString))]
        rows := rows.push row
        if rows.size % 25 == 0 then IO.println s!"Audited {rows.size} project declarations"
        if ci.isUnsafe || axs.any (fun a => !([`propext, `Classical.choice, `Quot.sound].contains a)) then
          unexpected := unexpected.push row
  let some path ← IO.getEnv "KS_EXTENSION_AUDIT" | throwError "KS_EXTENSION_AUDIT required"
  IO.FS.writeFile path ((Json.mkObj [("declarations", toJson rows),
    ("unexpected", toJson unexpected), ("count", toJson rows.size)]).pretty)
  if !unexpected.isEmpty then throwError "Unapproved axioms or unsafe declarations"
  logInfo m!"Focused declaration/axiom audit passed: {rows.size} declarations"
