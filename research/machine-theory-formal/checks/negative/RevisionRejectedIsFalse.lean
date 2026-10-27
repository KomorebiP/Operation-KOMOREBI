import MachineTheory.RevisionControls
open Komorebi.MachineTheory Dependency RevisionExamples RevisionControls BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false claim. This fixture must fail for its proof goal. -/
example : ¬ system.claim repairAdded 3 := by
  simp only [rejection_not_false.2,not_true_eq_false]
