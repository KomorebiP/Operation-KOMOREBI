import MachineTheory.LineageExamples
open Komorebi.MachineTheory.LineageExamples

example : prob fair selectedBad ≤ 1/10 := by
  rw [selected_candidate_certain]
  norm_num
