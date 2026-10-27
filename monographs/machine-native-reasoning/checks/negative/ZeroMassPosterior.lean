import MachineTheory.Examples
open Komorebi.MachineTheory Komorebi.MachineTheory.Examples
open Komorebi.MachineTheory.Instrument
noncomputable section

-- Intentionally invalid. Never import into the production library.
example : posterior? (fun _ : Bool => (0 : ℝ)) = some (fun _ => 0) := by
  simp [posterior?, mass]
