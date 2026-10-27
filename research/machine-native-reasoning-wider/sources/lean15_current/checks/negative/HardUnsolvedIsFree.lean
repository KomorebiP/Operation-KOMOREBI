import MachineTheory.HardExamples
import MachineTheory.HardControls
open Komorebi.MachineTheory
open HardInquiry HardExamples HardControls Finset

/-- Intentionally false boundary claim. -/
example : ∃ t : Tree Unit Bool Bool 1, noArtifact.Valid 1 univ t := by
  have boundary := noArtifact_no_tree
  simp_all
