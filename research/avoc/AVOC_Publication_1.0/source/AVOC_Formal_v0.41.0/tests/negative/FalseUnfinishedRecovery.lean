import AVOC.RecoveryExamples
open Komorebi.AVOC Komorebi.AVOC.CommitRecovery Komorebi.AVOC.PlannerRuntime
example (j : Job) (c d : Checkpoint j) (i : Intent j) (v : LiveExecution.StoreView) :
    recover j c (.unfinished i) v = .ok d := by
  rfl
