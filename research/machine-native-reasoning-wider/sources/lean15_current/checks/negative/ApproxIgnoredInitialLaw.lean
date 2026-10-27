import MachineTheory
open Komorebi.MachineTheory
open Instrument Variation ApproximateHistory ApproximateDecision ApproximationExamples
open scoped BigOperators
noncomputable section
example : tv (law (fun _ => resetLaw) unitPolicy (basis false) 0)
    (law (fun _ => resetLaw) unitPolicy (basis true) 0) ≤ 0 := by
  change tv (basis false : Bool → ℝ) (basis true) ≤ 0
  norm_num [tv,l1,basis,Fintype.sum_bool]

end
