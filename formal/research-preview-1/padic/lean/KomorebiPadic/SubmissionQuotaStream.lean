import KomorebiPadic.SubmissionQuota

/-!
# Exact prefix, stop, batching and legacy-semantics theorems

Resumption keeps both ledgers. Global halts have no candidate receipt. Changing
the explicit stop policy can permit free inputs, but cannot replenish a quota.
-/
namespace KomorebiPadic

theorem checkpointSubmissionGate_ne_inputExhausted {p : ℕ} {b : ParameterBox}
    (policy : SubmissionQuotaPolicy) (s : CheckpointSubmissionSession p b) :
    checkpointSubmissionGate policy s ≠ some .inputExhausted := by
  unfold checkpointSubmissionGate
  split
  · split <;> simp
  · simp

/-- A nonempty remainder is blocked by the returned global reason, not by a
silently discarded or installed candidate. -/
theorem runCheckpointSubmissionStream_halt_spec {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (policy : SubmissionQuotaPolicy)
    (s : CheckpointSubmissionSession p b) (xs : List α) :
    let out := runCheckpointSubmissionStream adapter policy s xs
    (out.pending = [] ↔ out.halt = .inputExhausted) ∧
    (out.pending ≠ [] → checkpointSubmissionGate policy out.session = some out.halt) := by
  induction xs generalizing s with
  | nil => simp [runCheckpointSubmissionStream]
  | cons x xs ih =>
    cases hg : checkpointSubmissionGate policy s with
    | some reason =>
      have hn : reason ≠ .inputExhausted := by
        intro he
        subst reason
        exact checkpointSubmissionGate_ne_inputExhausted policy s hg
      simp [runCheckpointSubmissionStream, hg, hn]
    | none =>
      simpa only [runCheckpointSubmissionStream, hg, ↓reduceDIte] using
        ih (consumeCheckpointSubmission adapter s x (checkpointSubmissionGate_available hg)).session

/-- Repeating a globally blocked tail without allocating new resources is a no-op. -/
theorem runCheckpointSubmissionStream_pending_idempotent {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (policy : SubmissionQuotaPolicy)
    (s : CheckpointSubmissionSession p b) (xs : List α) :
    let out := runCheckpointSubmissionStream adapter policy s xs
    runCheckpointSubmissionStream adapter policy out.session out.pending =
      ⟨out.session, [], [], out.pending, out.halt⟩ := by
  have hh := runCheckpointSubmissionStream_halt_spec adapter policy s xs
  dsimp only at hh ⊢
  cases he : (runCheckpointSubmissionStream adapter policy s xs).pending with
  | nil =>
    have hc := hh.1.mp he
    simp [runCheckpointSubmissionStream, hc]
  | cons x tail =>
    have hg := hh.2 (by rw [he]; simp)
    exact runCheckpointSubmissionStream_blocked adapter policy _ x tail hg

/-- Exact batching: the unprocessed suffix of the first batch is prepended to the
next batch. No limit is reset and no input occurrence is lost or duplicated. -/
theorem runCheckpointSubmissionStream_append {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (policy : SubmissionQuotaPolicy)
    (s : CheckpointSubmissionSession p b) (xs ys : List α) :
    runCheckpointSubmissionStream adapter policy s (xs ++ ys) =
      let first := runCheckpointSubmissionStream adapter policy s xs
      let second := runCheckpointSubmissionStream adapter policy first.session (first.pending ++ ys)
      ⟨second.session, first.processed ++ second.processed,
        first.receipts ++ second.receipts, second.pending, second.halt⟩ := by
  induction xs generalizing s with
  | nil => simp only [List.nil_append, runCheckpointSubmissionStream]
  | cons x xs ih =>
    cases hg : checkpointSubmissionGate policy s with
    | some reason => simp [runCheckpointSubmissionStream, hg]
    | none =>
      simp only [List.cons_append, runCheckpointSubmissionStream, hg, ↓reduceDIte]
      rw [ih]

/-- With zero-replay inputs allowed, the exact processed count depends only on
available submission slots and input length, not candidate validity. -/
theorem runCheckpointSubmissionStream_allowZeroReplay_count
    {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (s : CheckpointSubmissionSession p b)
    (xs : List α) :
    (runCheckpointSubmissionStream adapter .allowZeroReplay s xs).processed.length =
      min xs.length s.remaining := by
  induction xs generalizing s with
  | nil => simp [runCheckpointSubmissionStream]
  | cons x xs ih =>
    by_cases hs : s.spentSubmissions < s.submissionBudget
    · have hg : checkpointSubmissionGate .allowZeroReplay s = none := by
        simp [checkpointSubmissionGate, hs]
      have ha := consumeCheckpointSubmission_accounting adapter s x hs
      have hi := ih (consumeCheckpointSubmission adapter s x hs).session
      simp only [runCheckpointSubmissionStream, hg, ↓reduceDIte, List.length_cons]
      dsimp only at ha
      omega
    · have hz : s.remaining = 0 := by
        unfold CheckpointSubmissionSession.remaining
        omega
      simp [runCheckpointSubmissionStream, checkpointSubmissionGate, hs, hz]

/-- Unbounded adapter execution is a specification for the consumed prefix only. -/
def runCheckpointInputAdapter {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (s : CheckpointReplaySession p b) :
    List α → CheckpointReplayStreamResult p b
  | [] => ⟨s, []⟩
  | x :: xs =>
    let one := adapter.step s x
    let tail := runCheckpointInputAdapter adapter one.session xs
    ⟨tail.session, one.receipt :: tail.receipts⟩

/-- No replay is done again by this theorem. The new stream agrees exactly with
the old per-input behavior on the admitted prefix, including failed charges. -/
theorem runCheckpointSubmissionStream_refines_prefix {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (policy : SubmissionQuotaPolicy)
    (s : CheckpointSubmissionSession p b) (xs : List α) :
    let out := runCheckpointSubmissionStream adapter policy s xs
    runCheckpointInputAdapter adapter s.replay out.processed =
      ⟨out.session.replay, out.receipts⟩ := by
  induction xs generalizing s with
  | nil => rfl
  | cons x xs ih =>
    cases hg : checkpointSubmissionGate policy s with
    | some reason => simp [runCheckpointSubmissionStream, hg, runCheckpointInputAdapter]
    | none =>
      have hi := ih (consumeCheckpointSubmission adapter s x (checkpointSubmissionGate_available hg)).session
      simp only [runCheckpointSubmissionStream, hg, ↓reduceDIte, runCheckpointInputAdapter]
      dsimp only [consumeCheckpointSubmission] at hi ⊢
      rw [hi]

/-- Every return, including a zero-slot stop, keeps full partition certification. -/
theorem runCheckpointSubmissionStream_has_certificate {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (policy : SubmissionQuotaPolicy)
    (s : CheckpointSubmissionSession p b) (xs : List α) :
    let a := (runCheckpointSubmissionStream adapter policy s xs).session.replay.anchor
    ∃ cert : BudgetedPartitionCertificate p a.checkpoint.state.visited b,
      cert.result = a.checkpoint.state := by
  exact validateRectangleCheckpoint_has_certificate
    (runCheckpointSubmissionStream adapter policy s xs).session.replay.anchor.rootAccepted

theorem runCheckpointSubmissionStream_restart {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (policy : SubmissionQuotaPolicy)
    (s : CheckpointSubmissionSession p b) (xs : List α) (extra : ℕ) :
    let a := (runCheckpointSubmissionStream adapter policy s xs).session.replay.anchor
    runRectangleQueue p extra a.checkpoint.state =
      budgetedDecompose p (a.checkpoint.state.visited + extra) b := by
  exact validateRectangleCheckpoint_restart
    (runCheckpointSubmissionStream adapter policy s xs).session.replay.anchor.rootAccepted extra

/-- A literal unchanged state at a global stop, regardless of the adapter's input type. -/
theorem runCheckpointSubmissionStream_zero_submissions {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (policy : SubmissionQuotaPolicy)
    (s : CheckpointSubmissionSession p b) (x : α) (xs : List α)
    (hz : s.remaining = 0) :
    runCheckpointSubmissionStream adapter policy s (x :: xs) =
      ⟨s, [], [], x :: xs, .submissionQuota⟩ := by
  have hn : ¬s.spentSubmissions < s.submissionBudget := by
    unfold CheckpointSubmissionSession.remaining at hz
    omega
  apply runCheckpointSubmissionStream_blocked
  simp [checkpointSubmissionGate, hn]

/-- Strict policy stops before inspecting any next candidate, even a possible
zero-cost repeat. This is deliberately more conservative than Block19. -/
theorem runCheckpointSubmissionStream_zero_replay {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b)
    (s : CheckpointSubmissionSession p b) (x : α) (xs : List α)
    (hs : 0 < s.remaining) (hz : s.replay.remaining = 0) :
    runCheckpointSubmissionStream adapter .stopAtReplayExhaustion s (x :: xs) =
      ⟨s, [], [], x :: xs, .replayQuota⟩ := by
  have hn : s.spentSubmissions < s.submissionBudget := by
    unfold CheckpointSubmissionSession.remaining at hs
    omega
  apply runCheckpointSubmissionStream_blocked
  simp [checkpointSubmissionGate, hn, hz]

end KomorebiPadic
