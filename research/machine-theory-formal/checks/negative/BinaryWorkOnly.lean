import MachineTheory.BinaryExamples
open Komorebi.MachineTheory HardInquiry BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false boundary claim, required to fail for its proof diagnostic. -/
example : checkCandidate three 2 univ unaryThree = true := by
  simp only [unaryThree_rejected, Bool.false_eq_true]
