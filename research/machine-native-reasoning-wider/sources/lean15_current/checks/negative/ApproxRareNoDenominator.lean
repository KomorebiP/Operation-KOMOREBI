import MachineTheory
open Komorebi.MachineTheory
open Instrument Variation ApproximateHistory ApproximateDecision ApproximationExamples
open scoped BigOperators
noncomputable section
example : tv (normalize (restrict rareEvent (rareP (1/100))))
    (normalize (restrict rareEvent (rareQ (1/100)))) ≤ tv (rareP (1/100)) (rareQ (1/100)) := by
  rw [rare_conditional_distance _ (by norm_num), rare_distance _ (by norm_num)]
  norm_num

end
