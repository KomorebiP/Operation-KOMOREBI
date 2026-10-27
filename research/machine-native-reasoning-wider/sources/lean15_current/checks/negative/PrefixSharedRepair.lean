import MachineTheory.PrefixExamples
open Komorebi.MachineTheory HardInquiry OrderedCompiler PrefixExamples Finset

/-- Deliberately false claim: the gate requires its mathematical diagnostic. -/
example : ¬ classRepair.Valid 1 univ classTree := by
  simp only [non_singleton_boundary.1,not_true_eq_false]
