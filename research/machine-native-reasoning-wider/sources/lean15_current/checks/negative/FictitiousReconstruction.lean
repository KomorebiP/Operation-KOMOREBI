import MachineTheory
open Komorebi.MachineTheory Komorebi.MachineTheory.Block02Examples
open Komorebi.MachineTheory.Instrument Komorebi.MachineTheory.Bayes
open Komorebi.MachineTheory.Bayes.ReportingModel Komorebi.MachineTheory.Refinement
noncomputable section
-- Deliberately false claim. Never import into production.
example : ∃ ρ, erased.Reconstructs ρ := by
  simp only [erased_has_no_actual_reconstruction]
