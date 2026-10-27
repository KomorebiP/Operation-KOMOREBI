import MachineTheory.RevisionControls
open Komorebi.MachineTheory Dependency RevisionExamples RevisionControls BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false claim. This fixture must fail for its proof goal. -/
example : system.checkedFinish before before oldWitness allFresh (fun _ => false) rank ≠ none := by
  simp only [external_guard_rejects,ne_eq,not_true_eq_false]
