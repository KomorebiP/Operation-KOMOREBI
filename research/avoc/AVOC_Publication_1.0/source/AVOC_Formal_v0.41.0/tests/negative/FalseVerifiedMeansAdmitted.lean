import AVOC.ArtifactWorkflowExamples
open Komorebi.AVOC.ArtifactWorkflowExamples
example : (0 : Fin 1) ∈ passed.completed := by
  rw [verified_not_admitted]
  simp
