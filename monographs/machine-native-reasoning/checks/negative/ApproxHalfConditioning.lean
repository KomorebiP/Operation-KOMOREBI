import MachineTheory.ApproximationExamples
open Komorebi.MachineTheory
open Instrument Variation ApproximateHistory ApproximateDecision ApproximationExamples
open scoped BigOperators
noncomputable section
example : tv (normalize (restrict rareEvent (rareP (1/10))))
    (normalize (restrict rareEvent (largerEventQ (1/10)))) ≤ 1/4 := by
  rw [unequal_mass_sharp.2.2.2]
  norm_num

end
