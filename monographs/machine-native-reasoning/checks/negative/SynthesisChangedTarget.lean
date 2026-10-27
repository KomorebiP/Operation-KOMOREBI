import MachineTheory.SynthesisExamples
open Komorebi.MachineTheory Synthesis SynthesisExamples

/-- Deliberately false claim, required to fail for the stated proof diagnostic. -/
example : (scan changedTask grammar []).answer = (scan task grammar []).answer := by
  rw [target_change_breaks_old_answer.1, target_change_breaks_old_answer.2]
  simp
