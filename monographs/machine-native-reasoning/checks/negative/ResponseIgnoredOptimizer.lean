import MachineTheory.ResponseExamples
open Komorebi.MachineTheory
open Instrument Variation ApproximateDecision ResponseDecision DecisionHistory ResponseExamples
noncomputable section
example : responseRisk (basis () : Unit → ℝ) (fun _ => (1/4 : ℝ)) scalarLoss true-
    responseRisk (basis () : Unit → ℝ) (fun _ => (1/4 : ℝ)) scalarLoss false ≤ 0 := by
  rw [optimization_residual_cannot_disappear]; norm_num
end
