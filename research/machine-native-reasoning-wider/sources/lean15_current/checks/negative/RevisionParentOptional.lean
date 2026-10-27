import MachineTheory.RevisionControls
open Komorebi.MachineTheory Dependency RevisionExamples RevisionControls BinaryDiagnosis BinaryExamples Finset

/-- Deliberately false claim. This fixture must fail for its proof goal. -/
example : (system.evaluate repairAdded allFresh externalOK (fun _ => .pending) 2).ready = true := by
  simp only [parent_required_for_local_return.1,Verdict.ready,Verdict.witness?,Option.isSome_none,Bool.false_eq_true]
