import KomorebiPaperIV.CyclicFilters
namespace PaperIVNegativeFixture
axiom injected : False
theorem invalid : False := injected
end PaperIVNegativeFixture
open Lean Elab Command
run_cmd do
  let axioms ← Lean.collectAxioms ``PaperIVNegativeFixture.invalid
  if axioms.contains ``PaperIVNegativeFixture.injected then
    throwError "PAPER_IV_CUSTOM_AXIOM_REJECTED"
  else
    logInfo "ERROR_CONTROL_MISSED_INJECTION"
