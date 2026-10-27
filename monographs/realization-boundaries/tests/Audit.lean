import RealizationBoundaries
import Lean.Util.CollectAxioms
import Lean.Elab.Command
import Lean.Meta.Basic

open Lean Elab Command

/-! This is verification tooling, not a production theorem module. -/
run_cmd do
  let env ← getEnv
  let modules := env.header.moduleNames
  let allowed := #[``propext, ``Classical.choice, ``Quot.sound]
  let mut count := 0
  for (name, info) in env.constants.toList do
    let moduleName := match env.getModuleIdxFor? name with
      | some i => modules[i.toNat]!
      | none => env.mainModule
    if (`RealizationBoundaries).isPrefixOf moduleName || (`RealizationBoundaries).isPrefixOf name then
      count := count + 1
      let axioms ← collectAxioms name
      for a in axioms do
        unless allowed.contains a do
          throwError "AXIOM_POLICY_FAILURE {name}: {a}"
      if info.isUnsafe then
        throwError "UNSAFE_PRODUCTION_DECLARATION {name}"
      let kind := match info with
        | .thmInfo _ => "theorem"
        | .defnInfo _ => "definition"
        | .axiomInfo _ => "axiom"
        | .opaqueInfo _ => "opaque"
        | .quotInfo _ => "quotient"
        | .inductInfo _ => "inductive"
        | .ctorInfo _ => "constructor"
        | .recInfo _ => "recursor"
      if kind == "axiom" then
        throwError "PROJECT_AXIOM_DECLARATION {name}"
      let typeText ← liftTermElabM do
        return (← Meta.ppExpr info.type).pretty
      let row := Json.mkObj [
        ("record", toJson "declaration"), ("name", toJson name.toString),
        ("module", toJson moduleName.toString), ("kind", toJson kind),
        ("unsafe", toJson info.isUnsafe), ("type", toJson typeText),
        ("axioms", toJson (axioms.map Name.toString))]
      liftIO <| IO.println row.compress
  for moduleName in modules do
    let path ← liftIO <| findOLean moduleName
    liftIO <| IO.println (Json.mkObj [("record", toJson "import"),
      ("module", toJson moduleName.toString), ("path", toJson path.toString)]).compress
  if count == 0 then
    throwError "EMPTY_PROJECT_AUDIT"
  liftIO <| IO.println (Json.mkObj [("record", toJson "summary"),
    ("declarations", toJson count), ("status", toJson "PASS")]).compress
