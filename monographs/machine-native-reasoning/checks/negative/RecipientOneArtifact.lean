import MachineTheory.RecipientExamples
open Komorebi.MachineTheory
open Recipient RecipientExamples

/-- Deliberately false claim for the stated boundary. -/
example : ∃ f : Attained display → Bool, Valid display xorAudience.Accepts f ∧ (image display f).card ≤ 1 := by
  simp only [xor_one_artifact_impossible]
