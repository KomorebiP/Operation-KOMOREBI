import MachineTheory.PrefixExamples
open Komorebi.MachineTheory HardInquiry OrderedCompiler PrefixExamples Finset

/-- Deliberately false claim: the gate requires its mathematical diagnostic. -/
example : (PrefixScan.stream id 4 0 0 [false,false,false,false,true,true,true,true]).branches=none := by
  rw [capacity_equality_survives.1]
  simp
