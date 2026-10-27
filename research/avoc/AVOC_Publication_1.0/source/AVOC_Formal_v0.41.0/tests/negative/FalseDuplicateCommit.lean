import AVOC.RecoveryExamples
open Komorebi.AVOC Komorebi.AVOC.RecoveryExamples Komorebi.AVOC.PlannerRuntime
example (j : Job) : AtomicCommitModel.publish j (committedStore j) (stopCommit j) =
    .ok (committedStore j) := by
  rw [repeat_publication_example]
  rfl
