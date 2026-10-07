import KomorebiPadic.CheckpointReplayBudget

/-!
# Globally budgeted validation streams

This new API processes every supplied snapshot, recording each verdict. Rejected
and deferred candidates do not overwrite the last valid anchor. Later candidates
use the same remaining quota. The old Block18 stop-on-failure chain is unchanged.
-/
namespace KomorebiPadic

structure CheckpointReplayStreamResult (p : ℕ) (b : ParameterBox) where
  session : CheckpointReplaySession p b
  receipts : List CheckpointReplayReceipt

/-- Total actual attempted visits, whether the candidate was accepted or rejected. -/
def receiptReplaySum : List CheckpointReplayReceipt → ℕ
  | [] => 0
  | x :: xs => x.replayVisits + receiptReplaySum xs

/-- Visits whose resulting snapshot was installed. -/
def receiptAcceptedReplaySum : List CheckpointReplayReceipt → ℕ
  | [] => 0
  | x :: xs => (if x.verdict = .accepted then x.replayVisits else 0) +
    receiptAcceptedReplaySum xs

/-- Visits spent on results not installed. Deferred attempts always contribute zero. -/
def receiptDiscardedReplaySum : List CheckpointReplayReceipt → ℕ
  | [] => 0
  | x :: xs => (if x.verdict = .accepted then 0 else x.replayVisits) +
    receiptDiscardedReplaySum xs

def receiptAcceptedCount : List CheckpointReplayReceipt → ℕ
  | [] => 0
  | x :: xs => (if x.verdict = .accepted then 1 else 0) + receiptAcceptedCount xs

/-- Finite-input stream, not an unbounded server loop or message-rate limit. -/
def runCheckpointReplayStream {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) : List RectangleCheckpoint → CheckpointReplayStreamResult p b
  | [] => ⟨s, []⟩
  | c :: cs =>
    let step := stepCheckpointReplaySession s c
    let rest := runCheckpointReplayStream step.session cs
    ⟨rest.session, step.receipt :: rest.receipts⟩

/-- Exact receipt-sum and counter accounting over all attempts, not just an accepted prefix. -/
theorem runCheckpointReplayStream_accounting {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (cs : List RectangleCheckpoint) :
    let out := runCheckpointReplayStream s cs
    out.session.replayBudget = s.replayBudget ∧
    out.session.initialVisited = s.initialVisited ∧
    out.session.attemptedReplayVisits = s.attemptedReplayVisits + receiptReplaySum out.receipts ∧
    out.session.remaining + receiptReplaySum out.receipts = s.remaining ∧
    out.session.attemptedSnapshots = s.attemptedSnapshots + cs.length ∧
    out.session.acceptedVisitDelta = s.acceptedVisitDelta + receiptAcceptedReplaySum out.receipts ∧
    out.session.discardedReplayVisits = s.discardedReplayVisits + receiptDiscardedReplaySum out.receipts ∧
    out.session.acceptedSnapshots = s.acceptedSnapshots + receiptAcceptedCount out.receipts ∧
    out.receipts.length = cs.length := by
  induction cs generalizing s with
  | nil => simp [runCheckpointReplayStream, receiptReplaySum, receiptAcceptedReplaySum,
      receiptDiscardedReplaySum, receiptAcceptedCount]
  | cons c cs ih =>
    have hs := stepCheckpointReplaySession_accounting s c
    have hr := ih (stepCheckpointReplaySession s c).session
    simp only [runCheckpointReplayStream, receiptReplaySum, receiptAcceptedReplaySum,
      receiptDiscardedReplaySum, receiptAcceptedCount, List.length_cons]
    dsimp only at hs hr
    omega

/-- No finite stream can overspend its starting remainder, including hostile snapshots. -/
theorem runCheckpointReplayStream_budget_bound {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (cs : List RectangleCheckpoint) :
    receiptReplaySum (runCheckpointReplayStream s cs).receipts ≤ s.remaining ∧
    (runCheckpointReplayStream s cs).session.attemptedReplayVisits ≤ s.replayBudget := by
  have ha := runCheckpointReplayStream_accounting s cs
  have hb := (runCheckpointReplayStream s cs).session.budget_safe
  omega

/-- Splitting a stream into batches preserves the exact final session and receipt order. -/
theorem runCheckpointReplayStream_append {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (xs ys : List RectangleCheckpoint) :
    runCheckpointReplayStream s (xs ++ ys) =
      let first := runCheckpointReplayStream s xs
      let second := runCheckpointReplayStream first.session ys
      ⟨second.session, first.receipts ++ second.receipts⟩ := by
  induction xs generalizing s with
  | nil => rfl
  | cons x xs ih =>
    simp only [List.cons_append, runCheckpointReplayStream]
    rw [ih]

/-- Every deferred receipt has zero queue-visit charge. -/
theorem runCheckpointReplayStream_deferred_zero {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (cs : List RectangleCheckpoint) :
    ∀ x ∈ (runCheckpointReplayStream s cs).receipts,
      x.verdict = .deferred → x.replayVisits = 0 := by
  induction cs generalizing s with
  | nil => simp [runCheckpointReplayStream]
  | cons c cs ih =>
    intro x hx hv
    simp only [runCheckpointReplayStream, List.mem_cons] at hx
    rcases hx with rfl | hx
    · rw [stepCheckpointReplaySession_receipt] at hv ⊢
      exact meterCheckpointTransition_deferred_zero s.anchor c hv
    · exact ih (stepCheckpointReplaySession s c).session x hx hv

/-- Accepted deltas telescope through arbitrarily many rejected and deferred attempts. -/
theorem runCheckpointReplayStream_committed_delta {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (cs : List RectangleCheckpoint) :
    (runCheckpointReplayStream s cs).session.anchor.checkpoint.state.visited =
      s.anchor.checkpoint.state.visited +
        receiptAcceptedReplaySum (runCheckpointReplayStream s cs).receipts := by
  have ha := runCheckpointReplayStream_accounting s cs
  have hs := s.counter_exact
  have ht := (runCheckpointReplayStream s cs).session.counter_exact
  omega

/-- Returned anchors still have the full inherited partition certificate. -/
theorem runCheckpointReplayStream_has_certificate {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (cs : List RectangleCheckpoint) :
    ∃ cert : BudgetedPartitionCertificate p
      (runCheckpointReplayStream s cs).session.anchor.checkpoint.state.visited b,
      cert.result = (runCheckpointReplayStream s cs).session.anchor.checkpoint.state := by
  exact validateRectangleCheckpoint_has_certificate
    (runCheckpointReplayStream s cs).session.anchor.rootAccepted

/-- Further queue work is still exactly the canonical root run at the accepted counter. -/
theorem runCheckpointReplayStream_restart {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (cs : List RectangleCheckpoint) (extra : ℕ) :
    runRectangleQueue p extra (runCheckpointReplayStream s cs).session.anchor.checkpoint.state =
      budgetedDecompose p ((runCheckpointReplayStream s cs).session.anchor.checkpoint.state.visited + extra) b := by
  exact validateRectangleCheckpoint_restart
    (runCheckpointReplayStream s cs).session.anchor.rootAccepted extra

/-- An all-rejected/deferred stream keeps the initial certified checkpoint literally. -/
theorem runCheckpointReplayStream_no_accept_retains {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (cs : List RectangleCheckpoint)
    (hc : receiptAcceptedCount (runCheckpointReplayStream s cs).receipts = 0) :
    (runCheckpointReplayStream s cs).session.anchor.checkpoint = s.anchor.checkpoint := by
  induction cs generalizing s with
  | nil => rfl
  | cons c cs ih =>
    simp only [runCheckpointReplayStream, receiptAcceptedCount] at hc
    by_cases hv : (meterCheckpointTransition s.anchor s.remaining c).verdict = .accepted
    · rw [stepCheckpointReplaySession_receipt] at hc
      simp only [hv, ↓reduceIte] at hc
      omega
    · have he := (stepCheckpointReplaySession_retains_anchor s c hv).1
      have hn : receiptAcceptedCount
          (runCheckpointReplayStream (stepCheckpointReplaySession s c).session cs).receipts = 0 := by
        omega
      change (runCheckpointReplayStream (stepCheckpointReplaySession s c).session cs).session.anchor.checkpoint = _
      rw [ih _ hn, he]

/-- Existing sealed leaves survive every stream, even when later inputs are invalid. -/
theorem runCheckpointReplayStream_sealed_prefix {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (cs : List RectangleCheckpoint) :
    ∃ tail, (runCheckpointReplayStream s cs).session.anchor.checkpoint.state.sealed =
      s.anchor.checkpoint.state.sealed ++ tail := by
  induction cs generalizing s with
  | nil => exact ⟨[], (List.append_nil _).symm⟩
  | cons c cs ih =>
    obtain ⟨tail, ht⟩ := ih (stepCheckpointReplaySession s c).session
    change ∃ tail, (runCheckpointReplayStream (stepCheckpointReplaySession s c).session cs).session.anchor.checkpoint.state.sealed = _
    by_cases hv : (meterCheckpointTransition s.anchor s.remaining c).verdict = .accepted
    · have he := stepCheckpointReplaySession_accepts_candidate s c hv
      have hc := (meterCheckpointTransition_verdict _ _ _).symm.trans hv
      obtain ⟨pre, hpref⟩ := validateCheckpointTransition_sealed_prefix hc
      rw [he, hpref] at ht
      exact ⟨pre ++ tail, ht.trans (List.append_assoc _ _ _)⟩
    · rw [(stepCheckpointReplaySession_retains_anchor s c hv).1] at ht
      exact ⟨tail, ht⟩

end KomorebiPadic
