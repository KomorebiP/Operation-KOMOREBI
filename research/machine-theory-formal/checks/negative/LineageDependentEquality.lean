import MachineTheory.LineageExamples
open Komorebi.MachineTheory.LineageExamples

example : prob fair (fixedBad true ∪ fixedBad true) = prob fair (fixedBad true) + prob fair (fixedBad true) := by
  simp only [Finset.union_self, fixed_candidate_half]
  norm_num
