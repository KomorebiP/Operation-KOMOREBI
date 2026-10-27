import negative_controls.block51.policy.CustomAxiom
import Lean

open Lean Elab Command
run_cmd do
  let env ← getEnv
  let modules : Array Name := #[`negative_controls.block51.policy.CustomAxiom]
  let allowed : Array Name := #[`propext, `Classical.choice, `Quot.sound]
  let mut count : Nat := 0
  for (name, ci) in env.constants.toList do
    let some idx := env.getModuleIdxFor? name | continue
    let mod := env.allImportedModuleNames[idx.toNat]!
    if modules.contains mod then
      let axioms ← collectAxioms name
      if ci.isUnsafe || ci.isPartial then
        throwError "AUDIT_UNSAFE_OR_PARTIAL {name}"
      for ax in axioms do
        unless allowed.contains ax do
          throwError "AUDIT_FORBIDDEN_AXIOM {name}: {ax}"
      let row := Json.mkObj [
        ("name", Json.str name.toString),
        ("module", Json.str mod.toString),
        ("is_theorem", Json.bool ci.isTheorem),
        ("axioms", Json.arr (axioms.map fun n => Json.str n.toString))]
      logInfo m!"AUDIT_JSON|{row.compress}"
      count := count + 1
  logInfo m!"AUDIT_COUNT|{count}"
