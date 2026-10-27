import MachineTheory.SynthesisExamples
open Komorebi.MachineTheory Synthesis SynthesisExamples

/-- Deliberately false claim, required to fail for the stated proof diagnostic. -/
example : (prepare key [] grammar).2 + (scan task quotientGrammar []).comparisons ≤ (scan task grammar []).comparisons := by
  rw [preparation_count.2, compressed_run, original_run]
  norm_num
