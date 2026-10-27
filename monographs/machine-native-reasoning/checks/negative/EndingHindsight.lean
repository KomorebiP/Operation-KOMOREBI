import MachineTheory.SafeEndingExamples
open Komorebi.MachineTheory.SafeEnding Komorebi.MachineTheory.SafeEnding.Examples

example : ∃ a : Bool, ∀ y : Bool, a = y := by
  simp only [iff_false_intro hindsight_is_stronger.2]
