import KomorebiSpaceCombined
import Lean

set_option maxHeartbeats 0

open Lean Elab Command in
run_cmd do
  let env ← getEnv
  let wanted := ((← IO.FS.readFile "wanted_modules.txt").splitOn "\n").toArray
  let newModules := ((← IO.FS.readFile "new_modules.txt").splitOn "\n").toArray
  let wantedTypes := ((← IO.FS.readFile "type_names.txt").splitOn "\n").toArray
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
        let extensionModule := ["KomorebiSpace.RegularizedHilbertRepair",
          "KomorebiSpace.RegularizationCertificates", "KomorebiSpace.ProtectedRegularizedRepair"].contains modName.toString
        let closureModule := ["KomorebiSpace.FinitePrefixBoundary", "KomorebiSpace.DyadicSupport",
          "KomorebiSpace.ProtectedHilbertRepair", "KomorebiSpace.ProtectedLinearCertificates",
          "KomorebiSpace.FiniteRealizationExistence"].contains modName.toString
        let typeString ← if ((extensionModule || closureModule || newModules.contains modName.toString) && kind == "theorem") || wantedTypes.contains name.toString then
          liftTermElabM do return (← Meta.ppExpr ci.type).pretty
        else pure ""
        let row := Json.mkObj [("name", toJson name.toString),
          ("module", toJson modName.toString), ("kind", toJson kind),
          ("type", toJson typeString), ("unsafe", toJson ci.isUnsafe),
          ("axioms", toJson (axs.map Name.toString))]
        rows := rows.push row
        if rows.size % 100 == 0 then IO.println s!"Audited {rows.size} cumulative declarations"
        if ci.isUnsafe || axs.any (fun a => !([`propext, `Classical.choice, `Quot.sound].contains a)) then
          unexpected := unexpected.push row
  let some path ← IO.getEnv "KS_COMBINED_AUDIT" | throwError "KS_COMBINED_AUDIT required"
  IO.FS.writeFile path ((Json.mkObj [("declarations", toJson rows),
    ("unexpected", toJson unexpected), ("count", toJson rows.size)]).pretty)
  if !unexpected.isEmpty then throwError "Unapproved axiom or unsafe declaration in cumulative project"
  logInfo m!"Cumulative declaration/axiom audit passed: {rows.size} declarations"
