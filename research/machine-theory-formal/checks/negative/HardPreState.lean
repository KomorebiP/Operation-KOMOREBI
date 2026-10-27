import MachineTheory.HardExamples
import MachineTheory.HardControls
open Komorebi.MachineTheory
open HardInquiry HardExamples HardControls Finset

/-- Intentionally false boundary claim. -/
example : reset.update univ () () = univ := by
  rw [reset_post_support]
  have h : ({false} : Finset Bool) ≠ univ := by decide
  simp only [h]
