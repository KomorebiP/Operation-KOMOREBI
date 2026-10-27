import KomorebiSpace.CoordinateCovector
import Lean
set_option maxHeartbeats 0
set_option pp.maxSteps 10000000
open Lean Elab Command in
run_cmd do
  let env ← getEnv
  let names := (← IO.FS.readFile "helper_names.txt").splitOn "\n"
  let mut rows : Array Json := #[]
  for (name, ci) in env.constants.toList do
    if names.contains name.toString then
      let typeString ← liftTermElabM do
        withOptions (fun o => o.setBool `pp.all false |>.setBool `pp.fullNames true
          |>.setBool `pp.universes true |>.setBool `pp.proofs false) do
          return (← Meta.ppExpr ci.type).pretty
      rows := rows.push <| Json.mkObj [("name", toJson name.toString),
        ("type", toJson typeString)]
  IO.FS.writeFile "generated_helpers_readable.json" (toJson rows).pretty
