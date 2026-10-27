import MachineTheory.ResponseExamples
open Komorebi.MachineTheory
open Instrument Variation ApproximateDecision ResponseDecision DecisionHistory ResponseExamples
noncomputable section
example : |risk (basis false : Bool → ℝ) (fun b => if b then 10 else 0)-
    risk (basis true : Bool → ℝ) (fun b => if b then 10 else 0)| ≤ 1 := by
  rw [unbounded_loss_breaks_cap.1, unbounded_loss_breaks_cap.2]; norm_num
end
