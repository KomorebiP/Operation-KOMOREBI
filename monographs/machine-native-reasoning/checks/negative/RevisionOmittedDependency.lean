import MachineTheory.RevisionControls
open Komorebi.MachineTheory Dependency RevisionExamples RevisionControls BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false claim. This fixture must fail for its proof goal. -/
example : (∀ a b : Bool → Bool, omitted.view a () = omitted.view b () → (a false=a true ↔ b false=b true)) := by
  simp only [omitted_not_complete]
