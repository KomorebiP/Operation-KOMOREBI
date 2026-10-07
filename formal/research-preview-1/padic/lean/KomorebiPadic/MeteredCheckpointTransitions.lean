import KomorebiPadic.CheckpointTransitionChain

/-!
# Actual attempted replay accounting

One queue run supplies both the candidate comparison and the visit charge.
Failed replay is charged; metadata rejection and quota deferral do not replay.
These are logical queue visits, not a count of all validator operations.
-/
namespace KomorebiPadic

/-- The actual visits spent by a run, even when it finishes before its allowance. -/
def checkpointReplayVisits {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (n : ℕ) : ℕ :=
  (runRectangleQueue p n a.checkpoint.state).visited - a.checkpoint.state.visited

theorem checkpointReplayVisits_le {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (n : ℕ) : checkpointReplayVisits a n ≤ n := by
  have hv := runRectangleQueue_visited_bounds p n a.checkpoint.state
  unfold checkpointReplayVisits
  omega

/-- Exact completion shortfall is inherited from the canonical queue theorem. -/
theorem checkpointReplayVisits_eq_min {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (n : ℕ) :
    checkpointReplayVisits a n =
      min n (completePartitionVisitCount p b - a.checkpoint.state.visited) := by
  have hb := a.metadata.2.2.2.2.1
  have hbound := budgetedDecompose_visited_le_total p a.checkpoint.state.visited hb
  rw [← a.canonical] at hbound
  have hv := budgetedDecompose_visited_eq_min p (a.checkpoint.state.visited + n) hb
  rw [← validateRectangleCheckpoint_restart a.rootAccepted n] at hv
  unfold checkpointReplayVisits
  omega

structure CheckpointReplayReceipt where
  verdict : CheckpointVerdict
  replayVisits : ℕ
  deriving DecidableEq, Repr

/-- A single shared replay result is compared and charged. No root replay occurs. -/
def meterCheckpointTransition {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ)
    (c : RectangleCheckpoint) : CheckpointReplayReceipt :=
  if checkpointTransitionMetadata a c then
    if checkpointTransitionDelta a c ≤ limit then
      let replay := runRectangleQueue p (checkpointTransitionDelta a c) a.checkpoint.state
      ⟨if c.state = replay then .accepted else .rejected,
        replay.visited - a.checkpoint.state.visited⟩
    else ⟨.deferred, 0⟩
  else ⟨.rejected, 0⟩

/-- Metering leaves every existing semantic verdict unchanged. -/
theorem meterCheckpointTransition_verdict {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (c : RectangleCheckpoint) :
    (meterCheckpointTransition a limit c).verdict = validateCheckpointTransition a limit c := by
  unfold meterCheckpointTransition validateCheckpointTransition
  split <;> simp_all
  split <;> simp_all

/-- The exact charge includes a replay mismatch, not just successful increments. -/
theorem meterCheckpointTransition_visits {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (c : RectangleCheckpoint) :
    (meterCheckpointTransition a limit c).replayVisits =
      if checkpointTransitionMetadata a c ∧ checkpointTransitionDelta a c ≤ limit
      then checkpointReplayVisits a (checkpointTransitionDelta a c) else 0 := by
  by_cases hm : checkpointTransitionMetadata a c
  · by_cases hl : checkpointTransitionDelta a c ≤ limit <;>
      simp [meterCheckpointTransition, hm, hl, checkpointReplayVisits]
  · simp [meterCheckpointTransition, hm]

theorem meterCheckpointTransition_visits_le {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (c : RectangleCheckpoint) :
    (meterCheckpointTransition a limit c).replayVisits ≤ limit := by
  rw [meterCheckpointTransition_visits]
  split
  · rename_i hx
    exact (checkpointReplayVisits_le a _).trans hx.2
  · exact Nat.zero_le _

/-- Successful work equals the committed counter increment exactly. -/
theorem meterCheckpointTransition_accepted_visits {p limit : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (c : RectangleCheckpoint)
    (hc : (meterCheckpointTransition a limit c).verdict = .accepted) :
    (meterCheckpointTransition a limit c).replayVisits = checkpointTransitionDelta a c := by
  have hv := (meterCheckpointTransition_verdict a limit c).symm.trans hc
  obtain ⟨hm, hl, hs⟩ := (validateCheckpointTransition_accepted_iff a limit c).mp hv
  rw [meterCheckpointTransition_visits, ite_eq_left ⟨hm, hl⟩]
  unfold checkpointReplayVisits
  rw [← hs]
  rfl

/-- Canonical-state acceptance is exactly the old criterion, with a new work receipt. -/
theorem meterCheckpointTransition_accepted_iff {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (c : RectangleCheckpoint) :
    (meterCheckpointTransition a limit c).verdict = .accepted ↔
      c.MetadataValid p b ∧ a.checkpoint.state.visited ≤ c.state.visited ∧
      checkpointTransitionDelta a c ≤ limit ∧ c.Canonical p b := by
  rw [meterCheckpointTransition_verdict, validateCheckpointTransition_accepted_iff_canonical]

theorem meterCheckpointTransition_bad_metadata {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (c : RectangleCheckpoint)
    (hm : ¬ checkpointTransitionMetadata a c) :
    meterCheckpointTransition a limit c = ⟨.rejected, 0⟩ := by
  simp [meterCheckpointTransition, hm]

theorem meterCheckpointTransition_over_limit {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (c : RectangleCheckpoint)
    (hm : checkpointTransitionMetadata a c) (hl : limit < checkpointTransitionDelta a c) :
    meterCheckpointTransition a limit c = ⟨.deferred, 0⟩ := by
  simp [meterCheckpointTransition, hm, Nat.not_le_of_gt hl]

theorem meterCheckpointTransition_deferred_zero {p limit : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (c : RectangleCheckpoint)
    (hc : (meterCheckpointTransition a limit c).verdict = .deferred) :
    (meterCheckpointTransition a limit c).replayVisits = 0 := by
  rw [meterCheckpointTransition_verdict] at hc
  obtain ⟨hm, hl⟩ := (validateCheckpointTransition_deferred_iff a limit c).mp hc
  rw [meterCheckpointTransition_over_limit a limit c hm hl]

/-- An absorbing completed anchor consumes no visits even on a rejected attempt. -/
theorem meterCheckpointTransition_completed_zero {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (c : RectangleCheckpoint)
    (he : a.checkpoint.state.pending = []) :
    (meterCheckpointTransition a limit c).replayVisits = 0 := by
  rw [meterCheckpointTransition_visits]
  split
  · simp [checkpointReplayVisits, runRectangleQueue_empty p _ he]
  · rfl

/-- A permitted replay beyond true completion rejects and charges only remaining visits. -/
theorem meterCheckpointTransition_completion_shortfall {p limit : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (c : RectangleCheckpoint)
    (hm : checkpointTransitionMetadata a c) (hl : checkpointTransitionDelta a c ≤ limit)
    (hc : completePartitionVisitCount p b < c.state.visited) :
    (meterCheckpointTransition a limit c).verdict = .rejected ∧
    (meterCheckpointTransition a limit c).replayVisits =
      completePartitionVisitCount p b - a.checkpoint.state.visited := by
  have hb := a.metadata.2.2.2.2.1
  have hbound := budgetedDecompose_visited_le_total p a.checkpoint.state.visited hb
  rw [← a.canonical] at hbound
  have hd : completePartitionVisitCount p b - a.checkpoint.state.visited ≤
      checkpointTransitionDelta a c := by unfold checkpointTransitionDelta; omega
  have hv := runRectangleQueue_visited_bounds p (checkpointTransitionDelta a c) a.checkpoint.state
  have hmin := checkpointReplayVisits_eq_min a (checkpointTransitionDelta a c)
  rw [Nat.min_eq_right hd] at hmin
  have hne : c.state ≠ runRectangleQueue p (checkpointTransitionDelta a c) a.checkpoint.state := by
    intro heq
    unfold checkpointReplayVisits at hmin
    have he := congrArg RectangleQueueState.visited heq
    omega
  constructor
  · simp [meterCheckpointTransition, hm, hl, hne]
  · rw [meterCheckpointTransition_visits, ite_eq_left ⟨hm, hl⟩, hmin]

end KomorebiPadic
