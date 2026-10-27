import KomorebiSpace
import Lean

set_option maxHeartbeats 0

open Lean Elab Command in
run_cmd do
  let env ← getEnv
  let wanted := ((← IO.FS.readFile "scripts/type_names.txt").splitOn "\n").toArray
  let mut rows : Array Json := #[]
  let mut unexpected : Array Json := #[]
  for (name, ci) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let modName := env.header.moduleNames[idx.toNat]!
      if modName.toString == "KomorebiSpace" || modName.toString.startsWith "KomorebiSpace." then
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
        let newModule := ["KomorebiSpace.FinitePrefixBoundary", "KomorebiSpace.DyadicSupport",
          "KomorebiSpace.ProtectedHilbertRepair", "KomorebiSpace.ProtectedLinearCertificates",
          "KomorebiSpace.FiniteRealizationExistence"].contains modName.toString
        let typeString ← if (newModule && kind == "theorem") || wanted.contains name.toString then
          liftTermElabM do return (← Meta.ppExpr ci.type).pretty
        else pure ""
        let row := Json.mkObj [("name", toJson name.toString),
          ("module", toJson modName.toString), ("kind", toJson kind),
          ("type", toJson typeString), ("unsafe", toJson ci.isUnsafe), ("axioms", toJson (axs.map Name.toString))]
        rows := rows.push row
        if ci.isUnsafe || axs.any (fun a => !([`propext, `Classical.choice, `Quot.sound].contains a)) then
          unexpected := unexpected.push row
  let path ← IO.getEnv "KS_AUDIT_OUTPUT"
  let some path := path | throwError "KS_AUDIT_OUTPUT is required"
  IO.FS.writeFile path ((Json.mkObj [("declarations", toJson rows),
    ("unexpected", toJson unexpected), ("count", toJson rows.size)]).pretty)
  if !unexpected.isEmpty then throwError "Unapproved axiom or unsafe declaration in project"
  logInfo m!"Project declaration/axiom audit passed: {rows.size} declarations"
