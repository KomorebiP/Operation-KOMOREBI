import MachineTheory.SafeEndingExamples
open Komorebi.MachineTheory.SafeEnding Komorebi.MachineTheory.SafeEnding.Examples

example : ∃ P, SwitchingGuarantee threeState P 1 := by
  simp only [iff_false_intro ready_cannot_preserve_ending]
