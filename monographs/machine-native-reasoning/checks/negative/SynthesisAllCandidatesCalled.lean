import MachineTheory.SynthesisExamples
open Komorebi.MachineTheory Synthesis SynthesisExamples

/-- Deliberately false claim, required to fail for the stated proof diagnostic. -/
example : (scan task grammar []).transcript.length = grammar.length := by
  rw [original_run]
  norm_num [expectedTrace, grammar]
