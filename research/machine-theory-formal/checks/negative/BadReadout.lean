import MachineTheory
open Komorebi.MachineTheory Komorebi.MachineTheory.Examples
open Komorebi.MachineTheory.Instrument
noncomputable section

-- Intentionally invalid. Never import into the production library.
example : physical (flip () (false, false, false)) = physical (false, false, false) := by decide
