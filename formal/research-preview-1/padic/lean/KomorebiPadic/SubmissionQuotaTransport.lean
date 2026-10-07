import KomorebiPadic.SubmissionQuotaStream

/-!
# Typed, word, and JSON dual-quota adapters

All candidate-level behavior remains Block19 behavior on exactly the consumed
prefix. The new gate is outside the adapters. The old all-input streams remain
available and unchanged; no policy is silently replaced.
-/
namespace KomorebiPadic

def typedCheckpointInputAdapter (p : ℕ) (b : ParameterBox) :
    CheckpointInputAdapter RectangleCheckpoint p b where
  step := stepCheckpointReplaySession
  conserves := fun s c => by
    have h := stepCheckpointReplaySession_accounting s c
    exact ⟨h.1, h.2.1, h.2.2.1, h.2.2.2.1, h.2.2.2.2.1⟩

def wordCheckpointInputAdapter (p : ℕ) (b : ParameterBox) (wordLimit : ℕ) :
    CheckpointInputAdapter (List ℕ) p b where
  step := fun s words => stepCheckpointReplayWords s wordLimit words
  conserves := fun s words => stepCheckpointReplayWords_conserves s wordLimit words

def textCheckpointInputAdapter (p : ℕ) (b : ParameterBox) (byteLimit wordLimit : ℕ) :
    CheckpointInputAdapter String p b where
  step := fun s text => stepCheckpointReplayText s byteLimit wordLimit text
  conserves := fun s text => stepCheckpointReplayText_conserves s byteLimit wordLimit text

/-- Caller-selected policy is explicit; both quota ledgers live in s. -/
def runBudgetedCheckpointStream {p : ℕ} {b : ParameterBox}
    (policy : SubmissionQuotaPolicy) (s : CheckpointSubmissionSession p b)
    (inputs : List RectangleCheckpoint) :
    CheckpointSubmissionStreamResult RectangleCheckpoint p b :=
  runCheckpointSubmissionStream (typedCheckpointInputAdapter p b) policy s inputs

def runBudgetedCheckpointWordStream {p : ℕ} {b : ParameterBox}
    (policy : SubmissionQuotaPolicy) (s : CheckpointSubmissionSession p b)
    (wordLimit : ℕ) (inputs : List (List ℕ)) :
    CheckpointSubmissionStreamResult (List ℕ) p b :=
  runCheckpointSubmissionStream (wordCheckpointInputAdapter p b wordLimit) policy s inputs

def runBudgetedCheckpointTextStream {p : ℕ} {b : ParameterBox}
    (policy : SubmissionQuotaPolicy) (s : CheckpointSubmissionSession p b)
    (byteLimit wordLimit : ℕ) (inputs : List String) :
    CheckpointSubmissionStreamResult String p b :=
  runCheckpointSubmissionStream (textCheckpointInputAdapter p b byteLimit wordLimit) policy s inputs

theorem runCheckpointInputAdapter_typed {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (cs : List RectangleCheckpoint) :
    runCheckpointInputAdapter (typedCheckpointInputAdapter p b) s cs =
      runCheckpointReplayStream s cs := by
  induction cs generalizing s with
  | nil => rfl
  | cons c cs ih =>
    simp only [runCheckpointInputAdapter, runCheckpointReplayStream]
    rw [ih]
    rfl

theorem runCheckpointInputAdapter_text {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (byteLimit wordLimit : ℕ) (cs : List String) :
    runCheckpointInputAdapter (textCheckpointInputAdapter p b byteLimit wordLimit) s cs =
      runCheckpointReplayTextStream s byteLimit wordLimit cs := by
  induction cs generalizing s with
  | nil => rfl
  | cons c cs ih =>
    simp only [runCheckpointInputAdapter, runCheckpointReplayTextStream]
    rw [ih]
    rfl

/-- The old typed validator is exactly the semantics of the consumed prefix. -/
theorem runBudgetedCheckpointStream_legacy_prefix {p : ℕ} {b : ParameterBox}
    (policy : SubmissionQuotaPolicy) (s : CheckpointSubmissionSession p b)
    (cs : List RectangleCheckpoint) :
    let out := runBudgetedCheckpointStream policy s cs
    runCheckpointReplayStream s.replay out.processed = ⟨out.session.replay, out.receipts⟩ := by
  exact (runCheckpointInputAdapter_typed _ _).symm.trans
    (runCheckpointSubmissionStream_refines_prefix (typedCheckpointInputAdapter p b) policy s cs)

/-- No new JSON grammar or roundtrip assumption is introduced by the quota. -/
theorem runBudgetedCheckpointTextStream_legacy_prefix {p : ℕ} {b : ParameterBox}
    (policy : SubmissionQuotaPolicy) (s : CheckpointSubmissionSession p b)
    (byteLimit wordLimit : ℕ) (cs : List String) :
    let out := runBudgetedCheckpointTextStream policy s byteLimit wordLimit cs
    runCheckpointReplayTextStream s.replay byteLimit wordLimit out.processed =
      ⟨out.session.replay, out.receipts⟩ := by
  exact (runCheckpointInputAdapter_text _ _ _ _).symm.trans
    (runCheckpointSubmissionStream_refines_prefix
      (textCheckpointInputAdapter p b byteLimit wordLimit) policy s cs)

/-- Successful and failed replay charges are identical to the original ledger. -/
theorem runBudgetedCheckpointStream_committed_discarded {p : ℕ} {b : ParameterBox}
    (policy : SubmissionQuotaPolicy) (s : CheckpointSubmissionSession p b)
    (cs : List RectangleCheckpoint) :
    let out := runBudgetedCheckpointStream policy s cs
    out.session.replay.acceptedVisitDelta = s.replay.acceptedVisitDelta +
      receiptAcceptedReplaySum out.receipts ∧
    out.session.replay.discardedReplayVisits = s.replay.discardedReplayVisits +
      receiptDiscardedReplaySum out.receipts ∧
    out.session.replay.acceptedSnapshots = s.replay.acceptedSnapshots +
      receiptAcceptedCount out.receipts := by
  have he := runBudgetedCheckpointStream_legacy_prefix policy s cs
  dsimp only at he ⊢
  have ha := runCheckpointReplayStream_accounting s.replay
    (runBudgetedCheckpointStream policy s cs).processed
  dsimp only at ha
  rw [he] at ha
  exact ⟨ha.2.2.2.2.2.1, ha.2.2.2.2.2.2.1, ha.2.2.2.2.2.2.2.1⟩

/-- If the processed prefix contains no accepted input, the last valid checkpoint
is literally unchanged. This includes all globally stopped inputs. -/
theorem runBudgetedCheckpointStream_no_accept_retains {p : ℕ} {b : ParameterBox}
    (policy : SubmissionQuotaPolicy) (s : CheckpointSubmissionSession p b)
    (cs : List RectangleCheckpoint)
    (hc : receiptAcceptedCount (runBudgetedCheckpointStream policy s cs).receipts = 0) :
    (runBudgetedCheckpointStream policy s cs).session.replay.anchor.checkpoint =
      s.replay.anchor.checkpoint := by
  have he := runBudgetedCheckpointStream_legacy_prefix policy s cs
  dsimp only at he
  have hz : receiptAcceptedCount (runCheckpointReplayStream s.replay
      (runBudgetedCheckpointStream policy s cs).processed).receipts = 0 := by
    rw [he]
    exact hc
  have h := runCheckpointReplayStream_no_accept_retains s.replay _ hz
  rwa [he] at h

theorem runBudgetedCheckpointStream_sealed_prefix {p : ℕ} {b : ParameterBox}
    (policy : SubmissionQuotaPolicy) (s : CheckpointSubmissionSession p b)
    (cs : List RectangleCheckpoint) :
    ∃ tail, (runBudgetedCheckpointStream policy s cs).session.replay.anchor.checkpoint.state.sealed =
      s.replay.anchor.checkpoint.state.sealed ++ tail := by
  have he := runBudgetedCheckpointStream_legacy_prefix policy s cs
  dsimp only at he
  have h := runCheckpointReplayStream_sealed_prefix s.replay
    (runBudgetedCheckpointStream policy s cs).processed
  rwa [he] at h

/-- Under the permissive policy all inputs are processed exactly when the
remaining submission slots suffice, regardless of zero-replay failures. -/
theorem runCheckpointSubmissionStream_all_iff {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (s : CheckpointSubmissionSession p b)
    (xs : List α) :
    (runCheckpointSubmissionStream adapter .allowZeroReplay s xs).pending = [] ↔
      xs.length ≤ s.remaining := by
  have hn := runCheckpointSubmissionStream_allowZeroReplay_count adapter s xs
  have ha := (runCheckpointSubmissionStream_accounting adapter .allowZeroReplay s xs).1
  have hl := congrArg List.length ha
  simp only [List.length_append] at hl
  rw [List.length_eq_zero_iff.symm]
  omega

/-- The two current-state gates agree while replay allowance is positive.
There is deliberately no zero-budget equivalence claim. -/
theorem checkpointSubmissionGate_policies_eq_of_positive_replay {p : ℕ} {b : ParameterBox}
    (s : CheckpointSubmissionSession p b) (hr : 0 < s.replay.remaining) :
    checkpointSubmissionGate .stopAtReplayExhaustion s =
      checkpointSubmissionGate .allowZeroReplay s := by
  simp [checkpointSubmissionGate, Nat.ne_of_gt hr]

end KomorebiPadic
