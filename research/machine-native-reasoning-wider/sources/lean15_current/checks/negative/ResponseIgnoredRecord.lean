import MachineTheory.ResponseExamples
open Komorebi.MachineTheory
open Instrument Variation ApproximateDecision ResponseDecision DecisionHistory ResponseExamples
noncomputable section
example : |responseRisk (basis false) (fun b : Bool => if b then (1 : ℝ) else 0) scalarLoss false-
    responseRisk (basis true) (fun b : Bool => if b then (1 : ℝ) else 0) scalarLoss false| ≤ 0 := by
  rw [probability_term_is_necessary.2]; norm_num
end
