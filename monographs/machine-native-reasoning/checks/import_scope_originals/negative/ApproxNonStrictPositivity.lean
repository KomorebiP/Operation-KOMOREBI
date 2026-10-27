import MachineTheory
open Komorebi.MachineTheory
open Instrument Variation ApproximateHistory ApproximateDecision ApproximationExamples
open scoped BigOperators
noncomputable section
example : 0 < mass (restrict rareEvent (rareP 0)) := by
  rw [positive_threshold_is_strict.2.2.2.2]
  norm_num

end
