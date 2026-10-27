module
import Lean
import ProbeModuleGood
open Lean Elab Command
run_cmd do
  let env ← getEnv
  let names := env.constants.fold (init := #[]) fun out name _ =>
    match env.getModuleIdxFor? name with
    | some idx => if env.header.moduleNames[idx.toNat]? == some `ProbeModuleGood then out.push name else out
    | none => out
  let names := names.qsort Name.lt
  for name in names do
    let axioms ← Lean.collectAxioms name
    liftIO <| IO.println ("IMPORTPROBE " ++ (Json.mkObj [("name",toJson name.toString),("axioms",toJson (axioms.map Name.toString))]).compress)
  liftIO <| IO.println ("IMPORTCOUNT " ++ toString names.size)
