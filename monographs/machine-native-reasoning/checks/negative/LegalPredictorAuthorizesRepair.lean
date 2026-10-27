import MachineTheory.LegalQuotientExamples
open Komorebi.MachineTheory LegalQuotient LegalQuotientExamples

example : Legal permissionBad false [true] := by
  simp [Legal, execute, permissionBad]
