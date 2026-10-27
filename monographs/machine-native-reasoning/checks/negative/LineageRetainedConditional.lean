import MachineTheory.LineageExamples
open Komorebi.MachineTheory.LineageExamples

example : prob fair (fixedBad true ∩ fixedBad true) / prob fair (fixedBad true) ≤ 1/2 := by
  rw [retention_can_condition_to_certain_error.2.2]
  norm_num
