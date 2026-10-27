import MachineTheory.HardExamples
import MachineTheory.HardControls
open Komorebi.MachineTheory
open HardInquiry HardExamples HardControls Finset

/-- Intentionally false boundary claim. -/
example : ∃ t : Tree Unit Bool Bool 1, sensor.Valid 1 univ t ∧ sensor.profile 1 univ t ≤ (fun j => if j=0 then 1 else if j=1 then 2 else 1,2) := by
  simp only [sensor_two_records_insufficient]
