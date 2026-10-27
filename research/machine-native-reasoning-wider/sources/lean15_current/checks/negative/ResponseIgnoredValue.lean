import MachineTheory.ResponseExamples
open Komorebi.MachineTheory
open Instrument Variation ApproximateDecision ResponseDecision DecisionHistory ResponseExamples
noncomputable section
example : |responseRisk (basis () : Unit → ℝ) (fun _ => (0 : ℝ)) scalarLoss false-
    responseRisk (basis () : Unit → ℝ) (fun _ => (1/5 : ℝ)) scalarLoss false| ≤ 0 := by
  rw [response_term_is_necessary.2]; norm_num
end
