import MachineTheory
open Komorebi.MachineTheory Komorebi.MachineTheory.Examples
open Komorebi.MachineTheory.Instrument
noncomputable section

-- Intentionally invalid. Never import into the production library.
example : ∃ d : Attained display → Bool, ∀ x, d (record display x) = physical x := by
  exact ⟨fun h => h.val, fun x => by rfl⟩
