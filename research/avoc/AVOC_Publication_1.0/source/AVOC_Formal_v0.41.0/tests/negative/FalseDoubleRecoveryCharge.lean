import AVOC.RecoveryExamples
open Komorebi.AVOC Komorebi.AVOC.CommitRecovery Komorebi.AVOC.PlannerRuntime
example (j : Job) (c d : Checkpoint j) (r : Commit j) (v : LiveExecution.StoreView)
    (h : acknowledge j c r v = .ok d) :
    acknowledge j d r v = .ok { d with next := d.next + 1 } := by
  rw [acknowledge_idempotent j c d r v h]
  congr 1
