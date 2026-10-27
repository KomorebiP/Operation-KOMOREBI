import MachineTheory.BinaryExamples
open Komorebi.MachineTheory HardInquiry BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false boundary claim, required to fail for its proof diagnostic. -/
example : ∃ t : Tree Query Bool World 2, eight.Valid 2 univ t := by
  simp only [eight_no_two_queries]
