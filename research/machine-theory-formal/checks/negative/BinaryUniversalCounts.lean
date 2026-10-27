import MachineTheory.BinaryExamples
open Komorebi.MachineTheory HardInquiry BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false boundary claim, required to fail for its proof diagnostic. -/
example : 15 ≤ (universalRepair.profile 0 univ (false,false,false)).2 := by
  rw [universal_repair_small.2]
  norm_num
