import MachineTheory.LineageExamples
open Komorebi.MachineTheory.LineageExamples

example : prob fair (fixedBad false ∪ fixedBad true) ≤ 1/2 := by
  rw [disjoint_union_sharp.2.2]
  norm_num
