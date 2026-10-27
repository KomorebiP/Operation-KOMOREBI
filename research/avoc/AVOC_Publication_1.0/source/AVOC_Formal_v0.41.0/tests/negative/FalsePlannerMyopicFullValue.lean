import AVOC.PlannerExamples
open Komorebi.AVOC ExecutablePlanner PlannerExamples ArtifactWorkflowExamples
example : (evaluate executable 1 initial).score = (evaluate executable 3 initial).score := by
  rw [myopic_value_zero, executable_three_step_value]
  norm_num
