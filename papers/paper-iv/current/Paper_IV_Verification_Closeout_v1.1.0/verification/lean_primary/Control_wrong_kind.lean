import KomorebiPaperIV.CyclicFilters
open Lean Elab Command
run_cmd do
  let env ← getEnv
  match env.find? ``Komorebi.PaperIV.cyclicProjector with
  | some (.thmInfo _) => logInfo "ERROR_KIND_CONTROL_ACCEPTED_DEFINITION"
  | _ => throwError "PAPER_IV_WRONG_KIND_REJECTED"
