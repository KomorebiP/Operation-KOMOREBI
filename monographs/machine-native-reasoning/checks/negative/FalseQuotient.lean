import MachineTheory.Examples
open Komorebi.MachineTheory Komorebi.MachineTheory.Examples
open Komorebi.MachineTheory.Instrument
noncomputable section

-- Intentionally invalid. Never import into the production library.
example : FiberCriterion visible mixedLaw.kernel := by
  intro a o z x y h
  rfl
