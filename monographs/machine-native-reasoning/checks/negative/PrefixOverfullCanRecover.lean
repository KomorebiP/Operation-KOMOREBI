import MachineTheory.PrefixExamples
open Komorebi.MachineTheory HardInquiry OrderedCompiler PrefixExamples Finset

/-- Deliberately false claim: the gate requires its mathematical diagnostic. -/
example : PrefixScan.Completable 8 4 5 0 := by
  rw [PrefixScan.completion_iff 8 4 5 0 (by decide) (by decide)]
  norm_num
