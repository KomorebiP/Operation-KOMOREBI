import MachineTheory.RevisionControls
open Komorebi.MachineTheory Dependency RevisionExamples RevisionControls BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false claim. This fixture must fail for its proof goal. -/
example : (∃ r : Bool → ℕ, cyclic.Ranked r) := by
  simp only [cycle_has_no_rank]
