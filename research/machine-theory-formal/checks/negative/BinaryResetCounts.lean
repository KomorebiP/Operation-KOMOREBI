import MachineTheory.BinaryExamples
open Komorebi.MachineTheory HardInquiry BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false boundary claim, required to fail for its proof diagnostic. -/
example : 4 ≤ (reset.profile 1 univ resetTree).1 () := by
  rw [reset_valid_and_small.2]
  norm_num
