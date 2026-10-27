import AVOC.ArtifactWorkflowExamples
open Komorebi.AVOC.ArtifactWorkflowExamples
example : admitted.spent = 2 := by
  rw [final_budget.2]
  norm_num
