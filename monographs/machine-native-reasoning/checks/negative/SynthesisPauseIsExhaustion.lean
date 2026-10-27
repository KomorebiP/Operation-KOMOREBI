import MachineTheory.SynthesisExamples
open Komorebi.MachineTheory Synthesis SynthesisExamples

/-- Deliberately false claim, required to fail for the stated proof diagnostic. -/
example : ∃ r, boundedScan task 4 grammar [] = .complete r ∧ r.answer = none := by
  simp only [suspension_is_not_exhaustion]
