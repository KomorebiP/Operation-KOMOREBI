import MachineTheory.RevisionControls
open Komorebi.MachineTheory Dependency RevisionExamples RevisionControls BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false claim. This fixture must fail for its proof goal. -/
example : system.claim oldProfileTarget 4 := by
  simp only [obsolete_profile_rejected.2.2]
