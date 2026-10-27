import MachineTheory
import Lean

open Lean Elab Command in
run_cmd do
  let env ← getEnv
  for name in env.header.moduleNames do
    logInfo m!"IMPORTED_MODULE {name}"
  for (name, ci) in env.constants do
    if (`Komorebi.MachineTheory).isPrefixOf name then
      let kind := match ci with
        | .thmInfo _ => "theorem"
        | .axiomInfo _ => "axiom"
        | .defnInfo _ => "definition"
        | .opaqueInfo _ => "opaque"
        | .quotInfo _ => "quotient"
        | .inductInfo _ => "inductive"
        | .ctorInfo _ => "constructor"
        | .recInfo _ => "recursor"
      logInfo m!"PROJECT_CONSTANT {kind} {name}"
