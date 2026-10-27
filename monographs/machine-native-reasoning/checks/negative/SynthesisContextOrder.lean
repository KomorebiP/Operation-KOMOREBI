import MachineTheory.SynthesisExamples
open Komorebi.MachineTheory Synthesis SynthesisExamples

/-- Deliberately false claim, required to fail for the stated proof diagnostic. -/
example : (scan reversedTask grammar []).transcript = (scan task grammar []).transcript := by
  simp only [changed_context_order.2]
