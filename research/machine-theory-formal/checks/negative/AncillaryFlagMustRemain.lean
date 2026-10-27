import MachineTheory
open Komorebi.MachineTheory Komorebi.MachineTheory.Block02Examples
open Komorebi.MachineTheory.Instrument Komorebi.MachineTheory.Bayes
open Komorebi.MachineTheory.Bayes.ReportingModel Komorebi.MachineTheory.Refinement
noncomputable section
-- Deliberately false claim. Never import into production.
example : ¬ flagged.PreservesAll := by
  simp only [flag_can_be_discarded_for_every_prior, not_true_eq_false]
