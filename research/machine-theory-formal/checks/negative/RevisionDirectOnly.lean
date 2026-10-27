import MachineTheory.RevisionControls
open Komorebi.MachineTheory Dependency RevisionExamples RevisionControls BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false claim. This fixture must fail for its proof goal. -/
example : (4 : Node) ∉ graph.stale before repairAdded := by
  simp only [closure_is_necessary.2,not_true_eq_false]
