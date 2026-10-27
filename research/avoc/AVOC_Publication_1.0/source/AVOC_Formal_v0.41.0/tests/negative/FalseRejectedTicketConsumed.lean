import AVOC.ArtifactWorkflowExamples
open Komorebi.AVOC.ArtifactWorkflowExamples
example : rejected.slot.pending = none := by
  rw [rejection_retains_exact_ticket]
  simp
