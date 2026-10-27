import MachineTheory.PriceRevision
open Komorebi.MachineTheory ResourcePrices PriceExamples

example : ((fullCounts true-streamCounts true : ℕ) : ℝ) = (fullCounts true : ℝ)-streamCounts true := by
  rw [natural_subtraction_loses_cost.1,natural_subtraction_loses_cost.2]
  norm_num
