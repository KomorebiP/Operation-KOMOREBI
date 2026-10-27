import MachineTheory.PrefixExamples
open Komorebi.MachineTheory HardInquiry OrderedCompiler PrefixExamples Finset

/-- Deliberately false claim: the gate requires its mathematical diagnostic. -/
example : ¬ ∃ t : Tree Unit Bool Bool 1, boolModel.Valid 1 univ t := by
  simp only [missing_query_boundary.2,not_true_eq_false]
