import MachineTheory.PriceRevision
open Komorebi.MachineTheory ResourcePrices PriceExamples

example : PriceRevision.system.claim PriceRevision.correctedQuote 2 := by
  change PriceRevision.correctedQuote true=PriceRevision.actualSaving (PriceRevision.correctedQuote false) ∧ 0 ≤ PriceRevision.correctedQuote true
  norm_num [PriceRevision.correctedQuote]
