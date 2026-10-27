import MachineTheory.RecipientExamples
open Komorebi.MachineTheory
open Recipient RecipientExamples

/-- Deliberately false claim for the stated boundary. -/
example : Feasible (fun _ : Fin 3 => ()) (fun x c : Fin 3 => c ≠ x) := by
  simp only [triple_blind_sender_impossible]
