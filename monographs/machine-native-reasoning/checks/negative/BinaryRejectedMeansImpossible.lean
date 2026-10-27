import MachineTheory.BinaryExamples
open Komorebi.MachineTheory HardInquiry BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false boundary claim, required to fail for its proof diagnostic. -/
example : ¬ ∃ t : Tree Query Bool World 7, eight.Valid 7 univ t := by
  have h : ∃ t : Tree Query Bool World 7, eight.Valid 7 univ t := ⟨equality,equality_valid⟩
  simp only [h,not_true_eq_false]
