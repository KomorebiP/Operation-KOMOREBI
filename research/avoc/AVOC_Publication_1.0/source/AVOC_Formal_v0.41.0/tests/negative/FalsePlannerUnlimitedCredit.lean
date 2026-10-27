import AVOC.PlannerExamples
open Komorebi.AVOC ExecutablePlanner PlannerExamples ArtifactWorkflowExamples
example : (runReserved executable 4 2 3 1460 initial).isSome = true := by
  rw [insufficient_credit_rejects]
  decide
