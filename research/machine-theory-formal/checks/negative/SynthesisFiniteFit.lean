import MachineTheory.SynthesisExamples
open Komorebi.MachineTheory Synthesis SynthesisExamples

/-- Deliberately false claim, required to fail for the stated proof diagnostic. -/
example : evaluate .capped (0,5,8) = evaluate .maxGtC (0,5,8) := by
  change true = false
  simp
