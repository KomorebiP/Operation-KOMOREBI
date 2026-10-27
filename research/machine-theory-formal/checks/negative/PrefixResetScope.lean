import MachineTheory.PrefixExamples
open Komorebi.MachineTheory HardInquiry OrderedCompiler PrefixExamples Finset

/-- Deliberately false claim: the gate requires its mathematical diagnostic. -/
example : ¬ BinaryExamples.reset.Valid 1 univ BinaryExamples.resetTree := by
  simp only [reset_boundary.1,not_true_eq_false]
