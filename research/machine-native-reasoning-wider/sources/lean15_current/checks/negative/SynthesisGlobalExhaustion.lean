import MachineTheory.SynthesisExamples
open Komorebi.MachineTheory Synthesis SynthesisExamples

/-- Deliberately false claim, required to fail for the stated proof diagnostic. -/
example : ¬ Correct task .maxGtC := by
  simp only [outside_grammar_solution.1, not_true_eq_false]
