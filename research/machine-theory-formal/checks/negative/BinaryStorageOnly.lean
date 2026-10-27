import MachineTheory.BinaryExamples
open Komorebi.MachineTheory HardInquiry BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false boundary claim, required to fail for its proof diagnostic. -/
example : checkCandidate eight 7 univ equality = true := by
  simp only [equality_rejected, Bool.false_eq_true]
