import MachineTheory.LineageExamples
open Komorebi.MachineTheory.LineageExamples

example : prob fair (lateBad 100 100) ≤ 0 := by
  rw [(late_failure 100).2]
  norm_num
