import KomorebiSpaceDiagonal
import Lean.Util.CollectAxioms

open Lean Elab Command

run_cmd do
  let env ← getEnv
  let modules := #[`KomorebiSpace.DiagonalDefinitions,
    `KomorebiSpace.DiagonalSeriesBounds, `KomorebiSpace.InfiniteDiagonalModel,
    `KomorebiSpace.DiagonalNoisyRate, `KomorebiSpace.MonotoneBudgetAsymptotic,
    `KomorebiSpace.DiagonalAsymptotic, `KomorebiSpace.DiagonalTheorems,
    `KomorebiSpaceDiagonal]
  let allowed := #[`propext, `Classical.choice, `Quot.sound]
  let mut count := 0
  for (name, info) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let modName := env.header.moduleNames[idx.toNat]!
      if modules.contains modName then
        let axioms ← collectAxioms name
        let foreign := axioms.filter fun a => !allowed.contains a
        let row := Json.mkObj [
          ("name", toJson name.toString),
          ("module", toJson modName.toString),
          ("axioms", toJson (axioms.map Name.toString)),
          ("unsafe", toJson info.isUnsafe),
          ("axiom_declaration", toJson info.isAxiom)]
        liftIO <| IO.println row.compress
        if info.isUnsafe || info.isAxiom || !foreign.isEmpty then
          throwError "Rejected production declaration {name}: {foreign}"
        count := count + 1
  if count == 0 then throwError "Empty inventory"
  liftIO <| IO.println s!"AUDIT_DECLARATION_COUNT={count}"
