import MachineTheory.ApproximationExamples
open Komorebi.MachineTheory
open Instrument Variation ApproximateHistory ApproximateDecision ApproximationExamples
open scoped BigOperators
noncomputable section
example : posterior? (restrict rareEvent (rareP 0)) ≠ none := by
  unfold posterior?
  rw [positive_threshold_is_strict.2.2.2.2]
  norm_num

end
