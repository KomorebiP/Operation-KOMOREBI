import MachineTheory.RecipientExamples
open Komorebi.MachineTheory
open Recipient RecipientExamples

/-- Deliberately false claim for the stated boundary. -/
example : Feasible blindRecord (fun x c : Bool => c = x) := by
  simp only [individually_possible_not_common]
