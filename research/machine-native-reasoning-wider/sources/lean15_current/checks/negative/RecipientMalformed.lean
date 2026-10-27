import MachineTheory.RecipientExamples
open Komorebi.MachineTheory
open Recipient RecipientExamples

/-- Deliberately false claim for the stated boundary. -/
example : malformed.Accepts (false, false, false) false := by
  simp only [malformed_is_not_success]
