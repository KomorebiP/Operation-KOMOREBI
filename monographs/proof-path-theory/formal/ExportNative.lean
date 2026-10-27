import ProofPath.Examples
import Lean

open Lean Elab Command

/-- Export actual compiled dependency metadata. This metaprogram is not itself
    a formally verified parser or a general proof-term interpretation theorem. -/
elab "#export_native_field " file:str : command => do
  let env ← getEnv
  let roots : Array Name := #[
    `ProofPath.Field.derives_iff_all_models,
    `ProofPath.Field.support_cover_gluing,
    `ProofPath.protected_alternative,
    `ProofPath.exact_observation_count,
    `ProofPath.all_predicates_sufficient_iff_injective]
  let allowed := #[`propext, `Classical.choice, `Quot.sound]
  let mut names : Array Name := roots
  let mut justifications : Array Json := #[]
  let mut records : Array Json := #[]
  for root in roots do
    let some info := env.find? root | throwError "missing declaration {root}"
    let axioms ← collectAxioms root
    for ax in axioms do
      unless allowed.contains ax do
        throwError "forbidden dependency {ax} in {root}"
    let deps := info.getUsedConstantsAsSet.toArray.filter (· != root)
    for dep in deps do
      unless names.contains dep do names := names.push dep
    let js := deps.map (fun d => Json.str d.toString)
    justifications := justifications.push <| Json.mkObj [
      ("id", toJson ("native:" ++ root.toString)),
      ("premises", Json.arr js), ("conclusion", toJson root.toString),
      ("rule", toJson "compiled Lean type and proof constant dependencies"),
      ("certified", toJson true), ("evidence_ids", toJson #["lean-environment"])]
    records := records.push <| Json.mkObj [
      ("declaration", toJson root.toString),
      ("axioms", toJson (axioms.map Name.toString)),
      ("direct_dependencies", Json.arr js)]
  let nodes := names.map fun n => Json.mkObj [
    ("id", toJson n.toString), ("label", toJson ("Lean declaration: " ++ n.toString)),
    ("kind", toJson (if roots.contains n then "theorem" else "external_result"))]
  let payload := Json.mkObj [
    ("schema_version", toJson "1.0"),
    ("metadata", Json.mkObj [
      ("scope", toJson "Syntactic dependencies of five compiled declarations. Nonselected dependencies are explicit external leaves. This export does not recover failed discovery routes."),
      ("lean_version", toJson Lean.versionString), ("native_records", Json.arr records)]),
    ("premises", toJson ((names.filter (!roots.contains ·)).map Name.toString)),
    ("targets", toJson (roots.map Name.toString)), ("nodes", Json.arr nodes),
    ("evidence", Json.arr #[Json.mkObj [
      ("id", toJson "lean-environment"), ("kind", toJson "formal_proof"),
      ("source", toJson "ExportNative.lean freshly imports the built ProofPath modules"),
      ("scope", toJson "Already elaborated named declarations; transitive axiom allowlist checked"),
      ("certifies", toJson true)]]),
    ("justifications", Json.arr justifications)]
  liftIO <| IO.FS.writeFile file.getString (payload.pretty ++ "\n")

#export_native_field "../data/native_lean_field.json"
