import MachineTheory.BinaryExamples
open Komorebi.MachineTheory HardInquiry BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false boundary claim, required to fail for its proof diagnostic. -/
example : ∃ t : Tree Unit Bool Bool 5, silent.Valid 5 univ t := by
  simp only [silent_impossible 5]
