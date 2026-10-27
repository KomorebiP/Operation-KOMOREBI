import MachineTheory.PriceRevision
open Komorebi.MachineTheory ResourcePrices PriceExamples

example : (1 : ℝ)*1+2*(-1) ≥ 0 := by
  norm_num
