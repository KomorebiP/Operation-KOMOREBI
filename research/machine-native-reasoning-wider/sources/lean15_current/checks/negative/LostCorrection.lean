import MachineTheory
open Komorebi.MachineTheory Komorebi.MachineTheory.Examples
open Komorebi.MachineTheory.Instrument
noncomputable section

-- Intentionally invalid. Never import into the production library.
example : physical '' (candidatesV ∩ conventionZero) = physical '' (candidatesW ∩ conventionZero) := by
  rw [corrected_target_V, corrected_target_W]
  simp
