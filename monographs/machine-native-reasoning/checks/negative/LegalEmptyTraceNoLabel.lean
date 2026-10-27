import MachineTheory.LegalQuotientExamples
open Komorebi.MachineTheory LegalQuotient LegalQuotientExamples

example : labels fine (true,false) [] = some [] := by
  rw [empty_trace_keeps_initial_label]
  simp
