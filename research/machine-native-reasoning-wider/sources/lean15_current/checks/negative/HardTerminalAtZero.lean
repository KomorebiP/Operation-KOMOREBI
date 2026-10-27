import MachineTheory.HardExamples
import MachineTheory.HardControls
open Komorebi.MachineTheory
open HardInquiry HardExamples HardControls Finset

/-- Intentionally false boundary claim. -/
example : sensor.compute 0 univ ≠ ∅ := by
  have boundary := sensor_needs_observation
  simp_all
