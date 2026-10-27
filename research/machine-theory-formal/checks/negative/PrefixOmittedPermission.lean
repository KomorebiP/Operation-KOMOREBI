import MachineTheory.PrefixExamples
open Komorebi.MachineTheory HardInquiry OrderedCompiler PrefixExamples Finset

/-- Deliberately false claim: the gate requires its mathematical diagnostic. -/
example : (search streamScanner forbidden [()] [false,true] 1 [false,true]).answer ≠ none := by
  rw [permission_boundary.1]
  simp
