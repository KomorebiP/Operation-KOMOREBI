import MachineTheory.HardExamples
import MachineTheory.HardControls
open Komorebi.MachineTheory
open HardInquiry HardExamples HardControls Finset

/-- Intentionally false boundary claim. -/
example : paidTerminal.profile 1 univ bitTree ≤ (fun _ => 1,3) := by
  have boundary := one_unit_not_total_work
  simp_all
