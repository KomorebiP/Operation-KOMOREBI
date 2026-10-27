import MachineTheory.BinaryExamples
open Komorebi.MachineTheory HardInquiry BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false boundary claim, required to fail for its proof diagnostic. -/
example : 3 ≤ (directFour.profile 1 univ directFourTree).1 () := by
  rw [direct_four_small.2]
  norm_num
