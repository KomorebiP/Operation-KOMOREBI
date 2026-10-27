import MachineTheory.RecipientExamples
open Komorebi.MachineTheory
open Recipient RecipientExamples

/-- Deliberately false claim for the stated boundary. -/
example : Feasible display ignoresMessage.Accepts := by
  simp only [fixed_ignoring_decoder_has_no_encoder]
