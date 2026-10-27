import MachineTheory
open Komorebi.MachineTheory
open Instrument Variation ApproximateHistory ApproximateDecision ApproximationExamples
open scoped BigOperators
noncomputable section
example : tv (law (fun _ => resetLaw) unitPolicy (basis false) 1)
    (law (fun _ => resetLaw) unitPolicy (basis true) 1) = 0 := by
  rw [reset_full_history_distance]
  norm_num

end
