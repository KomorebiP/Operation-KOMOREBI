import MachineTheory.PriceRevision
open Komorebi.MachineTheory ResourcePrices PriceExamples

example : 0 ≤ saving perUse (prices 1 1) := by
  rw [priced_scan]
  norm_num
