import MachineTheory.PriceRevision
open Komorebi.MachineTheory ResourcePrices PriceExamples

example : PriceRevision.staleResult 1 = .reused true := by
  rw [PriceRevision.stale_quote_outcomes.2.1]
  simp
