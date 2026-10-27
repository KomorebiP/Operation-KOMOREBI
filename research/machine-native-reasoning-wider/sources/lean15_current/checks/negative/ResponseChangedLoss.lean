import MachineTheory.ResponseExamples
open Komorebi.MachineTheory
open Instrument Variation ApproximateDecision ResponseDecision DecisionHistory ResponseExamples
noncomputable section
example : |responseRisk (basis () : Unit → ℝ) (fun _ => (0 : ℝ)) (fun (_ : Unit) _ => (0 : ℝ)) ()-
    responseRisk (basis () : Unit → ℝ) (fun _ => (0 : ℝ)) (fun (_ : Unit) _ => (1 : ℝ)) ()| ≤ 0 := by
  rw [changed_loss_is_unaccounted]; norm_num
end
