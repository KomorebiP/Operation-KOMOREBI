import MachineTheory.Examples
open Komorebi.MachineTheory Komorebi.MachineTheory.Examples
open Komorebi.MachineTheory.Instrument
noncomputable section

-- Intentionally invalid. Never import into the production library.
example : IsDist (fun _ : Bool => (1 : ℝ)) := by
  constructor
  · intro x; norm_num
  · norm_num [mass, Fintype.sum_bool]
