import AVOC.RecoveryCodec

namespace Komorebi.AVOC.RecoveryExamples
open LiveExecution CommitRecovery AtomicCommitModel PlannerRuntime Binding

/-- A no-op visible state can still have a distinct committed sequence. -/
def emptyView : StoreView := ⟨⟨0,none⟩,none,none⟩
def beforeStore (j : Job) : Store j := ⟨emptyView,0,none,none⟩
def stopIntent (j : Job) : Intent j := ⟨0,emptyView,.stop⟩
def stopCommit (j : Job) : Commit j := ⟨stopIntent j,false,emptyView⟩
def preparedStore (j : Job) : Store j := ⟨emptyView,0,some (stopIntent j),none⟩
def committedStore (j : Job) : Store j := ⟨emptyView,1,none,some (stopCommit j)⟩

theorem preparation_example (j : Job) :
    prepare j (beforeStore j) (stopIntent j) = .ok (preparedStore j) := by
  simp [prepare,beforeStore,stopIntent,preparedStore]

theorem atomic_publish_example (j : Job) :
    publish j (preparedStore j) (stopCommit j) = .ok (committedStore j) := by
  simp [publish,preparedStore,stopCommit,stopIntent,committedStore]

theorem identical_view_different_commit_count (j : Job) :
    (beforeStore j).current = (committedStore j).current ∧
    (beforeStore j).next ≠ (committedStore j).next := by
  exact ⟨rfl,by change (0 : Nat) ≠ 1; decide⟩

theorem no_view_only_commit_count_decoder (j : Job) :
    ¬∃ d : StoreView → Nat,
      d (beforeStore j).current = (beforeStore j).next ∧
      d (committedStore j).current = (committedStore j).next := by
  rintro ⟨d,h0,h1⟩
  change d emptyView = 0 at h0
  change d emptyView = 1 at h1
  omega

theorem repeat_publication_example (j : Job) :
    publish j (committedStore j) (stopCommit j) =
      .error "no matching durable intent" := by
  simp [publish,committedStore]

theorem unfinished_does_not_become_report (j : Job) :
    recover j (CommitRecovery.initial j) (.unfinished (stopIntent j)) emptyView =
      .error "no durable result: do not infer a report or retry" := rfl

end Komorebi.AVOC.RecoveryExamples
