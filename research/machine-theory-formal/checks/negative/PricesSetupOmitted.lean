import MachineTheory.PriceRevision
open Komorebi.MachineTheory ResourcePrices PriceExamples

example : 0 < saving (paid 1) (prices 5 1) := by
  rw [paid_at_five]
  norm_num
