import KomorebiSpaceRegularization
import Lean
axiom unsupportedRepair : False
open Lean Elab Command in
run_cmd do
  let axs ← collectAxioms `unsupportedRepair
  if axs.any (fun a => !([`propext, `Classical.choice, `Quot.sound].contains a)) then
    throwError "custom axiom rejected by the extension policy"
