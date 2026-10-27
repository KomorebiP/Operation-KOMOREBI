import MachineTheory.PriceRevision
open Komorebi.MachineTheory ResourcePrices PriceExamples

example : ∃ w : Unit → ℝ,w ∈ (∅ : Finset (Unit → ℝ)) := by
  simp
