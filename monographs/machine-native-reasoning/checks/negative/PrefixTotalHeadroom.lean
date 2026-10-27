import MachineTheory.PrefixExamples
open Komorebi.MachineTheory HardInquiry OrderedCompiler PrefixExamples Finset

/-- Deliberately false claim: the gate requires its mathematical diagnostic. -/
example : PrefixScan.Completable 9 4 0 0 := by
  simp only [missing_total_capacity.2]
