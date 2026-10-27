import MachineTheory.HardExamples
import MachineTheory.HardControls
open Komorebi.MachineTheory
open HardInquiry HardExamples HardControls Finset

/-- Intentionally false boundary claim. -/
example : taggedReset.Valid 1 origins resetTree := by
  have boundary := reset_does_not_recover_origin
  simp_all
