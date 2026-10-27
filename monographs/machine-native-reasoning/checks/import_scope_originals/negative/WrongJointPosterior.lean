import MachineTheory
open Komorebi.MachineTheory Komorebi.MachineTheory.Examples
open Komorebi.MachineTheory.Instrument
noncomputable section

-- Intentionally invalid. Never import into the production library.
example : Instrument.normalize (applyKernel (correlated () true) (basis false)) true =
    Instrument.normalize (applyKernel (anticorrelated () true) (basis false)) true := by
  norm_num [mass, applyKernel, Instrument.normalize, basis, correlated, anticorrelated, Fintype.sum_bool]
