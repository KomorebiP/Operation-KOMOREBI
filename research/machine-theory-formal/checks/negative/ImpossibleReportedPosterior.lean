import MachineTheory
open Komorebi.MachineTheory Komorebi.MachineTheory.Block02Examples
open Komorebi.MachineTheory.Instrument Komorebi.MachineTheory.Bayes
open Komorebi.MachineTheory.Bayes.ReportingModel Komorebi.MachineTheory.Refinement
noncomputable section
-- Deliberately false claim. Never import into production.
example : posterior? (weights fair (unusedReport.report true)) ≠ none := by
  simp only [impossible_report_has_no_posterior, ne_eq, not_true_eq_false]
