import MachineTheory.LegalQuotientExamples
open Komorebi.MachineTheory LegalQuotient LegalQuotientExamples

example : fine.step (true,false) false = fine.step (true,true) false := by
  simp only [iff_false_intro projected_not_literal_successors.1]
