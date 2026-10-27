import MachineTheory.BinaryExamples
open Komorebi.MachineTheory HardInquiry BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false boundary claim, required to fail for its proof diagnostic. -/
example : Model.records 2 unaryThree = 5 := by
  rw [unaryThree_extra_record.2]
  norm_num
