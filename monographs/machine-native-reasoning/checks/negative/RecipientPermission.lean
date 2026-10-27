import MachineTheory.RecipientExamples
open Komorebi.MachineTheory
open Recipient RecipientExamples

/-- Deliberately false claim for the stated boundary. -/
example : forbidden.Accepts (false, false, false) false := by
  simp only [correct_output_still_forbidden]
