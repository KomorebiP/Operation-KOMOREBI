import MachineTheory.BinaryExamples
open Komorebi.MachineTheory HardInquiry BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false boundary claim, required to fail for its proof diagnostic. -/
example : eight.Valid 3 univ wrongLeaves := by
  simp only [wrong_leaves_rejected.2]
