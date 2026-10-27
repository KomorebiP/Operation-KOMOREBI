import MachineTheory
open Komorebi.MachineTheory Komorebi.MachineTheory.Block02Examples
open Komorebi.MachineTheory.Instrument Komorebi.MachineTheory.Bayes
open Komorebi.MachineTheory.Bayes.ReportingModel Komorebi.MachineTheory.Refinement
noncomputable section
-- Deliberately false claim. Never import into production.
example : Refinement.sequence fourKernel mandatory 2 =
    Refinement.sequence fourKernel mandatory 1 := by
  simp only [two_strict_rounds.2.1]
