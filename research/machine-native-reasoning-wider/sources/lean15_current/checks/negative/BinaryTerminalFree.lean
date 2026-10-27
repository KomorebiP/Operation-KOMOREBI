import MachineTheory.BinaryExamples
open Komorebi.MachineTheory HardInquiry BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false boundary claim, required to fail for its proof diagnostic. -/
example : 4 ≤ (freeTerminal.profile 3 univ balanced).1 () := by
  rw [free_terminal_work.2]
  norm_num
