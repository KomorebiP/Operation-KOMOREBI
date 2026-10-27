import MachineTheory.SynthesisExamples
open Komorebi.MachineTheory Synthesis SynthesisExamples

/-- Deliberately false claim, required to fail for the stated proof diagnostic. -/
example : (scan task [.maxGtC,.swappedMax] []).transcript = (scan task [.swappedMax] []).transcript := by
  simp only [later_representative_changes_ast.2.2]
