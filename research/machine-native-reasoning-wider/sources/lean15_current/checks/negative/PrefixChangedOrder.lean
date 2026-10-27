import MachineTheory.PrefixExamples
open Komorebi.MachineTheory HardInquiry OrderedCompiler PrefixExamples Finset

/-- Deliberately false claim: the gate requires its mathematical diagnostic. -/
example :
  (search streamScanner BinaryExamples.three [0,1,2] [0,1,2] 2 [0,1,2]).answer =
  (search streamScanner BinaryExamples.three [1,0,2] [0,1,2] 2 [0,1,2]).answer := by
  simp only [query_order_changes_tree]
