import MachineTheory.PrefixExamples
open Komorebi.MachineTheory HardInquiry OrderedCompiler PrefixExamples Finset

/-- Deliberately false claim: the gate requires its mathematical diagnostic. -/
example : streamEight.reads+streamEight.checks ≤ fullEight.reads+fullEight.checks := by
  have h := predicate_work_can_cost_more
  simp only [not_le_of_gt h]
