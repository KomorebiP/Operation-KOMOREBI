import MachineTheory.Examples
open Komorebi.MachineTheory Komorebi.MachineTheory.Examples
open Komorebi.MachineTheory.Instrument
noncomputable section

-- Intentionally invalid. Never import into the production library.
example : partialRead (Nat.succ (Nat.succ 0)) = 0 := by decide
