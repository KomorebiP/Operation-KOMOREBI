import MachineTheory.HardExamples
import MachineTheory.HardControls
open Komorebi.MachineTheory
open HardInquiry HardExamples HardControls Finset

/-- Intentionally false boundary claim. -/
example : readBit.Valid 1 univ missingBranch := by
  have boundary := missing_reachable_rejected
  simp_all
