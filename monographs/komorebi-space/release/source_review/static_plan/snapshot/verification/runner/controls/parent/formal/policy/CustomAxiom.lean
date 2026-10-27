import Lean
-- Legal to declare in Lean, deliberately prohibited by this project's audit.
axiom injectedUnprovedExistence : False
 theorem usesInjectedAssumption : False := injectedUnprovedExistence
open Lean Elab Command in
run_cmd do
  let axs ← collectAxioms `usesInjectedAssumption
  if axs.any (fun a => !([`propext, `Classical.choice, `Quot.sound].contains a)) then
    throwError "AXIOM_POLICY_REJECTION: unapproved dependency detected: {axs}"
