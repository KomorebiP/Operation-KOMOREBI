import MachineTheory
open Komorebi.MachineTheory Komorebi.MachineTheory.Block02Examples
open Komorebi.MachineTheory.Instrument Komorebi.MachineTheory.Bayes
open Komorebi.MachineTheory.Bayes.ReportingModel Komorebi.MachineTheory.Refinement
noncomputable section
-- Deliberately false claim. Never import into production.
example : nonconstantLikelihood false = nonconstantLikelihood true := by
  norm_num [nonconstantLikelihood]
