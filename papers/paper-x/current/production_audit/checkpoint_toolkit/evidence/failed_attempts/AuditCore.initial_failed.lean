import Lean

/-!
Verification tooling only. This module contains no Paper X mathematical result.
Audit imported declarations by owning module, not by namespace spelling.
The default policy permits only Lean's three recorded foundational axioms.
-/
namespace PaperXAudit
open Lean Elab Command

structure Target where
  name : Name
  kind : String
  owner : Name

private def kindOf : ConstantInfo → String
  | .thmInfo _ => "theorem"
  | .defnInfo _ => "definition"
  | .opaqueInfo _ => "opaque"
  | .axiomInfo _ => "axiom"
  | .inductInfo _ => "inductive"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"
  | .quotInfo _ => "quotient"

private def ownerOf (env : Environment) (name : Name) : Option Name := do
  let idx ← env.getModuleIdxFor? name
  env.header.moduleNames[idx.toNat]?

private def emit (fields : List (String × Json)) : CommandElabM Unit := do
  liftIO <| IO.println ("P10AUDIT " ++ (Json.mkObj fields).compress)

private def allowed (name : Name) : Bool :=
  name == ``propext || name == ``Classical.choice || name == ``Quot.sound

/-- Audit every kernel constant owned by the supplied imported modules.
Explicit targets must also have the stated declaration kind and owning module.
The final marker is emitted only after the complete enumeration succeeds. -/
def auditModules (owners : Array Name) (targets : Array Target) : CommandElabM Unit := do
  let env ← getEnv
  if owners.isEmpty then
    throwError "P10_EMPTY_OWNER_SET"
  for i in [:owners.size] do
    if (owners.extract 0 i).contains owners[i]! then
      throwError "P10_DUPLICATE_OWNER"
    if (env.getModuleIdx? owners[i]!).isNone then
      throwError "P10_OWNER_NOT_IMPORTED: {owners[i]!}"
  for i in [:targets.size] do
    let t := targets[i]!
    if (targets.extract 0 i).any (fun s => s.name == t.name) then
      throwError "P10_DUPLICATE_TARGET"
    if !owners.contains t.owner then
      throwError "P10_TARGET_OWNER_OUT_OF_SCOPE: {t.name}"
    match env.find? t.name with
    | none => throwError "P10_TARGET_MISSING: {t.name}"
    | some ci =>
      if kindOf ci != t.kind then
        throwError "P10_TARGET_KIND: {t.name}"
      if ownerOf env t.name != some t.owner then
        throwError "P10_TARGET_OWNER: {t.name}"
      emit [("event", toJson "target"), ("name", toJson t.name.toString),
        ("kind", toJson t.kind), ("owner", toJson t.owner.toString)]
  let constants := env.constants.toList.filter fun (name, _) =>
    match ownerOf env name with
    | some owner => owners.contains owner
    | none => false
  if constants.isEmpty then
    throwError "P10_EMPTY_OWNED_CONSTANT_SET"
  let sorted := constants.toArray.qsort (fun a b => Name.lt a.1 b.1)
  let mut theorems := 0
  let mut rejected := 0
  for (name, ci) in sorted do
    let axioms ← Lean.collectAxioms name
    let forbidden := axioms.filter fun ax => !allowed ax
    if !forbidden.isEmpty then
      rejected := rejected + 1
    if kindOf ci == "theorem" then
      theorems := theorems + 1
    emit [("event", toJson "declaration"), ("name", toJson name.toString),
      ("kind", toJson (kindOf ci)),
      ("owner", toJson ((ownerOf env name).getD Name.anonymous).toString),
      ("axioms", toJson (axioms.map Name.toString)),
      ("forbidden", toJson (forbidden.map Name.toString))]
  if rejected > 0 then
    throwError "P10_FORBIDDEN_AXIOMS: {rejected} declarations"
  emit [("event", toJson "complete"), ("owners", toJson (owners.map Name.toString)),
    ("declarations", toJson sorted.size), ("theorems", toJson theorems),
    ("targets", toJson targets.size)]
end PaperXAudit
