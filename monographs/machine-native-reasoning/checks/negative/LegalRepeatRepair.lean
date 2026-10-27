import MachineTheory.LegalQuotientExamples
open Komorebi.MachineTheory LegalQuotient LegalQuotientExamples

example : Legal coarse true [true,true] := by
  simp [Legal, repeated_repair_refused.2]
