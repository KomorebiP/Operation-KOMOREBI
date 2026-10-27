import InjectedOpaque

open Lean Meta Elab Command

-- This is an audit program, not a mathematical proof or a new axiom.
run_cmd do
  let env ← getEnv
  let moduleNames := env.header.moduleNames
  let ownedModules : Array Name := #[`InjectedOpaque]
  -- Compiler-generated partial helpers are separately inventoried, never proof-replayed.
  let generatedRuntime : Array Name := #[]
  let mut counts : Array Nat := ownedModules.map (fun _ => 0)
  let mut total : Nat := 0
  let mut outside : Nat := 0
  for (name, info) in env.checked.get.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let owner := moduleNames[idx.toNat]!
      for mi in [:ownedModules.size] do
        if owner == ownedModules[mi]! then
          total := total + 1
          counts := counts.modify mi (· + 1)
          let inNamespace := Name.isPrefixOf `Komorebi name || Name.isPrefixOf `KomorebiVerification name
          unless inNamespace do outside := outside + 1
          if info.isUnsafe then throwError "OWNED AUDIT REJECTED unsafe: {name}"
          if info.isPartial && !(generatedRuntime.contains name) then
            throwError "OWNED AUDIT REJECTED unreviewed partial declaration: {name}"
          if generatedRuntime.contains name && !info.isPartial then
            throwError "OWNED AUDIT REJECTED runtime classification changed: {name}"
          if !info.isPartial then
            let dependencies := info.getUsedConstantsAsSet
            for helper in generatedRuntime do
              if dependencies.contains helper then
                throwError "OWNED AUDIT REJECTED logical runtime-helper dependency: {name} -> {helper}"
          match info with
          | .axiomInfo _ => throwError "OWNED AUDIT REJECTED axiom: {name}"
          | .opaqueInfo _ => throwError "OWNED AUDIT REJECTED opaque: {name}"
          | _ => pure ()
          let axioms ← Lean.collectAxioms name
          for ax in axioms do
            unless ax == ``propext || ax == ``Classical.choice || ax == ``Quot.sound do
              throwError "OWNED AUDIT REJECTED dependency {ax}: {name}"
          let kind := match info with
            | .thmInfo _ => "theorem"
            | .defnInfo _ => "definition"
            | .inductInfo _ => "inductive"
            | .ctorInfo _ => "constructor"
            | .recInfo _ => "recursor"
            | .quotInfo _ => "quotient"
            | .axiomInfo _ => "axiom"
            | .opaqueInfo _ => "opaque"
          let row := Json.mkObj [
            ("module", toJson owner.toString), ("name", toJson name.toString),
            ("kind", toJson kind), ("in_project_namespace", toJson inNamespace),
            ("runtime_only", toJson info.isPartial),
            ("type_expr", toJson (if info.isPartial then reprStr info.type else "")),
            ("value_expr", toJson (if info.isPartial then (info.value? (allowOpaque := true)).map reprStr else none)),
            ("level_params", toJson (if info.isPartial then info.levelParams.map Name.toString else [])),
            ("axioms", toJson (axioms.map Name.toString))]
          liftIO <| IO.println ("OWNED " ++ row.compress)
  if total == 0 then throwError "OWNED AUDIT REJECTED empty inventory"
  for mi in [:ownedModules.size] do
    let m := ownedModules[mi]!
    if !(#[]).contains m && counts[mi]! == 0 then
      throwError "OWNED AUDIT REJECTED missing declaration-bearing module: {m}"
    liftIO <| IO.println s!"OWNED_MODULE {m} {counts[mi]!}"
  liftIO <| IO.println s!"OWNED_AUDIT_PASS {total} OUTSIDE_NAMESPACE {outside}"
