import MachineTheory.HardExamples
import MachineTheory.HardControls
open Komorebi.MachineTheory
open HardInquiry HardExamples HardControls Finset

/-- Intentionally false boundary claim. -/
example : restricted.Valid 1 univ bitTree := by
  have boundary := existential_permission_insufficient
  simp_all
