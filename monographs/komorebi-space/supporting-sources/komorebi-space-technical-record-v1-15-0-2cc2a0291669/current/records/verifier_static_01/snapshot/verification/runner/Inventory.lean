-- The runner prepends imports for every project entrypoint to a generated copy.
import Lean.Util.CollectAxioms

set_option maxHeartbeats 0

open Lean Elab Command in
run_cmd do
  let env ← getEnv
  let some wantedPath ← IO.getEnv "KOMOREBI_AUDIT_MODULES"
    | throwError "KOMOREBI_AUDIT_MODULES is required"
  let some outputPath ← IO.getEnv "KOMOREBI_AUDIT_OUTPUT"
    | throwError "KOMOREBI_AUDIT_OUTPUT is required"
  let wanted := ((← IO.FS.readFile wantedPath).splitOn "\n").toArray
  let allowed := #[`propext, `Classical.choice, `Quot.sound]
  let mut rows : Array Json := #[]
  let mut rejected : Array Json := #[]
  for (name, info) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let moduleName := env.header.moduleNames[idx.toNat]!
      if wanted.contains moduleName.toString then
        let axioms ← collectAxioms name
        let kind := match info with
          | .thmInfo _ => "theorem"
          | .defnInfo _ => "definition"
          | .opaqueInfo _ => "opaque"
          | .axiomInfo _ => "axiom"
          | .inductInfo _ => "inductive"
          | .ctorInfo _ => "constructor"
          | .recInfo _ => "recursor"
          | .quotInfo _ => "quotient"
        let row := Json.mkObj [
          ("name", toJson name.toString),
          ("module", toJson moduleName.toString),
          ("kind", toJson kind),
          ("axioms", toJson (axioms.map Name.toString)),
          ("unsafe", toJson info.isUnsafe),
          ("axiom_declaration", toJson info.isAxiom)]
        rows := rows.push row
        if info.isUnsafe || info.isAxiom || axioms.any (fun ax => !allowed.contains ax) then
          rejected := rejected.push row
  IO.FS.writeFile outputPath ((Json.mkObj [
    ("count", toJson rows.size),
    ("declarations", toJson rows),
    ("rejected", toJson rejected)]).pretty)
  if rows.isEmpty then throwError "Empty project inventory"
  if !rejected.isEmpty then throwError "Project declaration policy rejected {rejected.size} declarations"
  logInfo m!"Project declaration/recursive axiom inventory passed: {rows.size} declarations"
