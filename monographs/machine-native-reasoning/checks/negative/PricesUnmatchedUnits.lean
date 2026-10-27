import MachineTheory.PriceRevision
open Komorebi.MachineTheory ResourcePrices PriceExamples

example : saving (fun _ : Unit => (10 : ℝ)) (fun _ => 1) = saving (fun _ : Unit => (1 : ℝ)) (fun _ => 1) := by
  norm_num [saving]
