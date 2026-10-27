import MachineTheory.ResponseExamples
open Komorebi.MachineTheory
open Instrument Variation ApproximateDecision ResponseDecision DecisionHistory ResponseExamples
noncomputable section
example : responseRisk (basis () : Unit → ℝ) (fun _ => (1/2 : ℝ)) scalarLoss false <
    responseRisk (basis () : Unit → ℝ) (fun _ => (1/2 : ℝ)) scalarLoss true := by
  rw [gap_equality_is_not_uniqueness.2]; norm_num
end
