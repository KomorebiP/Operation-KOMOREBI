import MachineTheory.PriceRevision
open Komorebi.MachineTheory ResourcePrices PriceExamples

example : saving perUse (prices 5 1) ≥ 3 := by
  rw [priced_scan]
  norm_num
