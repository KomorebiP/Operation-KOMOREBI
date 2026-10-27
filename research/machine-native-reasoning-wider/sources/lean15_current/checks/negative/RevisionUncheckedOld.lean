import MachineTheory.RevisionControls
open Komorebi.MachineTheory Dependency RevisionExamples RevisionControls BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false claim. This fixture must fail for its proof goal. -/
example : (∀ v, cyclicSystem.Established (fun _ => false) v true) := by
  simp only [cyclic_flags_are_not_proofs.2]
