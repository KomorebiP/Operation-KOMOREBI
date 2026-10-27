import MachineTheory.Examples
open Komorebi.MachineTheory Komorebi.MachineTheory.Examples
open Komorebi.MachineTheory.Instrument
noncomputable section

-- Intentionally invalid. Never import into the production library.
example : compress (swap (swap (reconstruct 1))) = 0 := by
  norm_num [compress, reconstruct, swap]
