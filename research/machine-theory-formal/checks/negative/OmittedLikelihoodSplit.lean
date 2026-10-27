import MachineTheory
open Komorebi.MachineTheory Komorebi.MachineTheory.Block02Examples
open Komorebi.MachineTheory.Instrument Komorebi.MachineTheory.Bayes
open Komorebi.MachineTheory.Bayes.ReportingModel Komorebi.MachineTheory.Refinement
noncomputable section
-- Deliberately false claim. Never import into production.
example : ∃ g : Bool → ℝ, (∀ b, 0 < g b) ∧
    ∀ p : Four → ℝ, IsDist p →
      push Prod.fst (update p (fun x => nonconstantLikelihood x.2)) =
        update (push Prod.fst p) g := by
  simp only [likelihood_split_cannot_be_omitted]
