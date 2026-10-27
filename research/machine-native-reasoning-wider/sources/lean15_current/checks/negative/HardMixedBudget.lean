import MachineTheory.HardExamples
import MachineTheory.HardControls
open Komorebi.MachineTheory
open HardInquiry HardExamples HardControls Finset

/-- Intentionally false boundary claim. -/
example : ∃ t : Tree (Option (Fin 4)) (Fin 4) (Fin 4) 3, four.Valid 3 univ t ∧ four.profile 3 univ t ≤ scalar 3 5 := by
  simp only [four_no_mixed_budget 3]
