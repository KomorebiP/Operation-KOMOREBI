__IMPORTS__

open Lean Meta Elab Command

-- This is an audit program, not a mathematical proof or a new axiom.
run_cmd do
  let env ← getEnv
  let moduleNames := env.header.moduleNames
  let ownedModules : Array Name := __MODULES__
  -- Compiler-generated partial helpers are separately inventoried, never proof-replayed.
  let generatedRuntime : Array Name := #[`Komorebi.FiniteAlgorithms.orbitClosureIter._unsafe_rec, `Komorebi.FiniteDifference.iteratedDiff._unsafe_rec, `Komorebi.FiniteDifference.iteratedWeightedDiff._unsafe_rec, `Komorebi.PacketNaturalityCompletion.Reachability.wordApply._unsafe_rec, `Komorebi.PaperIRelease.CategoryExport.evaluate._unsafe_rec, `Komorebi.PaperIRelease.CategoryExport.evaluateTransported._unsafe_rec, `Komorebi.PaperIRelease.GrammarAlgebra.TypedData.pathMap._unsafe_rec, `Komorebi.PaperIRelease.GrammarAlgebra.TypedPath.word._unsafe_rec, `Komorebi.PaperIRelease.StrictPath._unsafe_rec, `Komorebi.PaperIRelease.operatorWord._unsafe_rec, `Komorebi.PathGraphKrylov.krylov._unsafe_rec, `Komorebi.Seed.OperatorExpr.eval._unsafe_rec, `Komorebi.Seed.instReprOperatorExpr.repr._unsafe_rec]
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
            ("axioms", toJson (axioms.map Name.toString))]
          liftIO <| IO.println ("OWNED " ++ row.compress)
  if total == 0 then throwError "OWNED AUDIT REJECTED empty inventory"
  for mi in [:ownedModules.size] do
    let m := ownedModules[mi]!
    if !(__EMPTY_MODULES__).contains m && counts[mi]! == 0 then
      throwError "OWNED AUDIT REJECTED missing declaration-bearing module: {m}"
    liftIO <| IO.println s!"OWNED_MODULE {m} {counts[mi]!}"
  liftIO <| IO.println s!"OWNED_AUDIT_PASS {total} OUTSIDE_NAMESPACE {outside}"
