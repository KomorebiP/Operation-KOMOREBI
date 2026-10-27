import MachineTheory.PrefixExamples
open Komorebi.MachineTheory HardInquiry OrderedCompiler PrefixExamples Finset

/-- Deliberately false claim: the gate requires its mathematical diagnostic. -/
example : (search streamScanner BinaryExamples.silent [()] [false,true] 2 [false,true]).answer ≠ none := by
  rw [silent_capacity_is_not_solution.2]
  simp
