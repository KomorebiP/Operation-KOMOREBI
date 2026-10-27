import MachineTheory.SynthesisExamples
open Komorebi.MachineTheory Synthesis SynthesisExamples

/-- Deliberately false claim, required to fail for the stated proof diagnostic. -/
example : KeySound probeTask probeKey := by
  simp only [probe_key_is_unsound]
