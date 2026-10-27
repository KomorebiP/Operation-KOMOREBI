import MachineTheory.RecipientExamples
open Komorebi.MachineTheory
open Recipient RecipientExamples

/-- Deliberately false claim for the stated boundary. -/
example : timedOut.Accepts (false, false, false) false := by
  simp only [timeout_is_not_success]
