import MachineTheory.RecipientExamples
open Komorebi.MachineTheory
open Recipient RecipientExamples

/-- Deliberately false claim for the stated boundary. -/
example : ∃ c : Bool, ∀ i : Bool, c = i := by
  simp only [no_one_artifact_for_opposed_recipients]
