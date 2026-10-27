import AVOC.LiveExecution
open Komorebi.AVOC
open ArtifactWorkflow PlannerRuntime LiveExecution
example (j : Job) (s : RunState) (a : Action (Fin 1) (Fin j.artifacts.size)) :
    acceptStep j s (a, .fault "timeout") = .ok s := by
  simp [acceptStep]
