import MachineTheory
import Lean.Elab.Command

/-! Inventory the actual compiled environment through its redundant imported
constant-name tables. This includes compiler-generated project declarations
without traversing every upstream ConstantInfo value. The source list is not
used as the enumeration oracle. -/
open Lean Elab Command in
run_cmd do
  let env ← getEnv
  for name in env.header.moduleNames do
    liftIO <| IO.println s!"IMPORTED_MODULE {name}"
  let mut seen : Std.HashSet Name := {}
  for data in env.header.moduleData do
    for name in data.constNames do
      if (`Komorebi.MachineTheory).isPrefixOf name && !seen.contains name then
        seen := seen.insert name
        let some ci := env.find? name | throwError "Missing imported constant {name}"
        let kind := match ci with
          | .thmInfo _ => "theorem"
          | .axiomInfo _ => "axiom"
          | .defnInfo _ => "definition"
          | .opaqueInfo _ => "opaque"
          | .quotInfo _ => "quotient"
          | .inductInfo _ => "inductive"
          | .ctorInfo _ => "constructor"
          | .recInfo _ => "recursor"
        liftIO <| IO.println s!"PROJECT_CONSTANT {kind} {name}"
