import MachineTheory.SafeEndingExamples
open Komorebi.MachineTheory.SafeEnding Komorebi.MachineTheory.SafeEnding.Examples

example : ∃ σ, EndingGuarantee threeState σ 2 := by
  simp only [iff_false_intro trap_cannot_end]
