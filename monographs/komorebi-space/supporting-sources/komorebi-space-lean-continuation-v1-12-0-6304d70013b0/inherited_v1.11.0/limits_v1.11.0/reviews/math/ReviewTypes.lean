import KomorebiSpaceCombined
import Lean

set_option maxHeartbeats 0
set_option pp.maxSteps 10000000

open Lean Elab Command in
run_cmd do
  let env ← getEnv
  let mods := ["KomorebiSpace.RegularizationLimits",
    "KomorebiSpace.RegularizationStrongLimit", "KomorebiSpace.RegularizationNoiseLimits"]
  let mut rows : Array Json := #[]
  for (name, ci) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let modName := env.header.moduleNames[idx.toNat]!
      if mods.contains modName.toString then
        let typeString ← liftTermElabM do
          withOptions (fun o => o.setBool `pp.all false |>.setBool `pp.fullNames true
            |>.setBool `pp.universes true |>.setBool `pp.proofs true) do
            return (← Meta.ppExpr ci.type).pretty
        let valueString ← if ["KomorebiSpace.RegularizationLimits.path",
            "KomorebiSpace.RegularizationNoiseLimits.scalarSharpOperator"].contains name.toString then
          match ci with
          | .defnInfo v => liftTermElabM do
              withOptions (fun o => o.setBool `pp.all false |>.setBool `pp.fullNames true
                |>.setBool `pp.universes true |>.setBool `pp.proofs true) do
                return (← Meta.ppExpr v.value).pretty
          | _ => pure "not a definition"
        else pure ""
        rows := rows.push (Json.mkObj [("name", toJson name.toString),
          ("module", toJson modName.toString), ("type", toJson typeString),
          ("selected_definition_value", toJson valueString)])
  let some out ← IO.getEnv "KS_REVIEW_TYPES" | throwError "KS_REVIEW_TYPES required"
  IO.FS.writeFile out ((toJson rows).pretty)
  logInfo m!"Independent readable type display: {rows.size} declarations"
