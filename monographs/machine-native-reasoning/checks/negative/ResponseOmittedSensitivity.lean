import MachineTheory.ResponseExamples
open Komorebi.MachineTheory
open Instrument Variation ApproximateDecision ResponseDecision DecisionHistory ResponseExamples
noncomputable section
example : |(if (0 : ℝ)>0 then (1 : ℝ) else 0)-(if (1/100 : ℝ)>0 then (1 : ℝ) else 0)| ≤
    dist (0 : ℝ) (1/100) := by
  rw [bounded_is_not_lipschitz_one.1, bounded_is_not_lipschitz_one.2]; norm_num
end
