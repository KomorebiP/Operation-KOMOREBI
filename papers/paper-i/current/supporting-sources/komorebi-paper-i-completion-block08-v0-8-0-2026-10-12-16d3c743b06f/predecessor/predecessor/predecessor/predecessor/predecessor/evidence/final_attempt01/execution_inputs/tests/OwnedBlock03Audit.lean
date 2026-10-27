import PaperICompletion3
import KomorebiVerification.KernelAudit

open Lean Meta Elab Command

-- This is an audit program, not a mathematical proof or a new axiom.
run_cmd do
  let env ← getEnv
  let moduleNames := env.header.moduleNames
  let ownedModules : Array Name := #[`KomorebiVerification.Basic, `KomorebiVerification.EllipticAlgorithms, `KomorebiVerification.ExactCoordinates, `KomorebiVerification.FibreRefinement, `KomorebiVerification.FullMatrixCyclicity, `KomorebiVerification.KernelAudit, `KomorebiVerification.MathlibImports, `KomorebiVerification.PacketNaturalityCompletion, `KomorebiVerification.PaperIBlockCompletion, `KomorebiVerification.PaperITransport, `KomorebiVerification.PathGraphKrylov, `KomorebiVerification.ProjectorCore, `KomorebiVerification.ResidueProjectors, `KomorebiVerification.SeedRankBasics, `KomorebiVerification.SeedRankOperations, `KomorebiVerification.SemisimpleCompletion, `KomorebiVerification.SemisimpleSeedRank, `KomorebiVerification.SingleOperatorGraph, `KomorebiVerification.TopologicalCompletion, `KomorebiVerification, `PaperICompletion.CyclicClassification, `PaperICompletion.SpectralCertificates, `PaperICompletion.ConditionedCoordinates, `PaperICompletion, `PaperICompletion3.PrimarySeedFormula, `PaperICompletion3.OperatorPrimaryAPI, `PaperICompletion3.InvariantFactorCount, `PaperICompletion3]
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
            ("axioms", toJson (axioms.map Name.toString))]
          liftIO <| IO.println ("OWNED " ++ row.compress)
  if total == 0 then throwError "OWNED AUDIT REJECTED empty inventory"
  for mi in [:ownedModules.size] do
    let m := ownedModules[mi]!
    if m != `KomorebiVerification && m != `PaperICompletion && m != `PaperICompletion3 && m != `KomorebiVerification.MathlibImports && counts[mi]! == 0 then
      throwError "OWNED AUDIT REJECTED missing declaration-bearing module: {m}"
    liftIO <| IO.println s!"OWNED_MODULE {m} {counts[mi]!}"
  liftIO <| IO.println s!"OWNED_AUDIT_PASS {total} OUTSIDE_NAMESPACE {outside}"
