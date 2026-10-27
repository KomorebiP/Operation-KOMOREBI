import MachineTheory.PrefixExamples
open Komorebi.MachineTheory HardInquiry OrderedCompiler PrefixExamples Finset

/-- Deliberately false claim: the gate requires its mathematical diagnostic. -/
example : ¬ boolModel.Valid 2 ([false,false,false,true].toFinset) boolTree := by
  simp only [duplicate_rows_boundary.1,not_true_eq_false]
