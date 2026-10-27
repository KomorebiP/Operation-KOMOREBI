import MachineTheory
open Komorebi.MachineTheory
open Instrument Variation ApproximateHistory ApproximateDecision ApproximationExamples
open scoped BigOperators
noncomputable section
example : tv (basis true : Bool → ℝ) (basis false) ≤ 0 := by
  rw [baseline_only_audit_fails.2.1]
  norm_num

end
