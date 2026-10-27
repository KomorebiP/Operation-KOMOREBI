import KomorebiPadic.MeteredCheckpointTransitions

/-!
# Persistent global replay quota

Attempted visits are never refunded after replay rejection. The last accepted
anchor stays certified. Proof fields are not external file fields and erase at
execution. Bootstrap work is outside the caller's successor-session quota.
-/
namespace KomorebiPadic

structure CheckpointReplaySession (p : ℕ) (b : ParameterBox) where
  anchor : ValidatedRectangleCheckpoint p b
  initialVisited : ℕ
  replayBudget : ℕ
  attemptedReplayVisits : ℕ
  acceptedVisitDelta : ℕ
  discardedReplayVisits : ℕ
  attemptedSnapshots : ℕ
  acceptedSnapshots : ℕ
  budget_safe : attemptedReplayVisits ≤ replayBudget
  counter_exact : anchor.checkpoint.state.visited = initialVisited + acceptedVisitDelta
  spending_exact : attemptedReplayVisits = acceptedVisitDelta + discardedReplayVisits

/-- Remaining successor allowance; never reset by a failed submission. -/
def CheckpointReplaySession.remaining {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) : ℕ := s.replayBudget - s.attemptedReplayVisits

/-- Start explicitly with an already validated anchor and a new caller-selected budget. -/
def startCheckpointReplaySession {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (budget : ℕ) : CheckpointReplaySession p b where
  anchor := a
  initialVisited := a.checkpoint.state.visited
  replayBudget := budget
  attemptedReplayVisits := 0
  acceptedVisitDelta := 0
  discardedReplayVisits := 0
  attemptedSnapshots := 0
  acceptedSnapshots := 0
  budget_safe := Nat.zero_le _
  counter_exact := (Nat.add_zero _).symm
  spending_exact := rfl

/-- Session construction enforces all budget and committed-counter identities. -/
theorem CheckpointReplaySession.conservation {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) :
    s.attemptedReplayVisits + s.remaining = s.replayBudget ∧
    s.acceptedVisitDelta ≤ s.attemptedReplayVisits ∧
    s.acceptedVisitDelta = s.anchor.checkpoint.state.visited - s.initialVisited ∧
    s.acceptedVisitDelta + s.discardedReplayVisits + s.remaining = s.replayBudget := by
  have h1 := s.budget_safe
  have h2 := s.counter_exact
  have h3 := s.spending_exact
  unfold CheckpointReplaySession.remaining
  omega

structure CheckpointReplayStepResult (p : ℕ) (b : ParameterBox) where
  session : CheckpointReplaySession p b
  receipt : CheckpointReplayReceipt

/-- Exactly one metered validation is executed. Acceptance promotes its candidate;
nonacceptance retains the anchor but preserves every actual replay charge. -/
def stepCheckpointReplaySession {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (c : RectangleCheckpoint) :
    CheckpointReplayStepResult p b :=
  let receipt := meterCheckpointTransition s.anchor s.remaining c
  have hbound : s.attemptedReplayVisits + receipt.replayVisits ≤ s.replayBudget := by
    have hv := meterCheckpointTransition_visits_le s.anchor s.remaining c
    have hb := s.conservation.1
    change s.attemptedReplayVisits +
      (meterCheckpointTransition s.anchor s.remaining c).replayVisits ≤ _
    omega
  if hc : receipt.verdict = .accepted then
    have hv : validateCheckpointTransition s.anchor s.remaining c = .accepted :=
      (meterCheckpointTransition_verdict _ _ _).symm.trans hc
    have hm := meterCheckpointTransition_accepted_visits s.anchor c hc
    have ho := (validateCheckpointTransition_counter_bounds hv).1
    ⟨{ anchor := advanceValidatedCheckpoint s.anchor c hv
       initialVisited := s.initialVisited
       replayBudget := s.replayBudget
       attemptedReplayVisits := s.attemptedReplayVisits + receipt.replayVisits
       acceptedVisitDelta := s.acceptedVisitDelta + checkpointTransitionDelta s.anchor c
       discardedReplayVisits := s.discardedReplayVisits
       attemptedSnapshots := s.attemptedSnapshots + 1
       acceptedSnapshots := s.acceptedSnapshots + 1
       budget_safe := hbound
       counter_exact := by
         have hs := s.counter_exact
         change c.state.visited = _
         unfold checkpointTransitionDelta
         omega
       spending_exact := by
         have hs := s.spending_exact
         change s.attemptedReplayVisits +
           (meterCheckpointTransition s.anchor s.remaining c).replayVisits = _
         omega }, receipt⟩
  else
    ⟨{ anchor := s.anchor
       initialVisited := s.initialVisited
       replayBudget := s.replayBudget
       attemptedReplayVisits := s.attemptedReplayVisits + receipt.replayVisits
       acceptedVisitDelta := s.acceptedVisitDelta
       discardedReplayVisits := s.discardedReplayVisits + receipt.replayVisits
       attemptedSnapshots := s.attemptedSnapshots + 1
       acceptedSnapshots := s.acceptedSnapshots
       budget_safe := hbound
       counter_exact := s.counter_exact
       spending_exact := by rw [s.spending_exact]; omega }, receipt⟩

/-- The displayed receipt belongs to the single validation at the current remainder. -/
theorem stepCheckpointReplaySession_receipt {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (c : RectangleCheckpoint) :
    (stepCheckpointReplaySession s c).receipt =
      meterCheckpointTransition s.anchor s.remaining c := by
  unfold stepCheckpointReplaySession
  dsimp only
  split <;> rfl

/-- Exact per-candidate charge, budget conservation, and successful-visit accounting. -/
theorem stepCheckpointReplaySession_accounting {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (c : RectangleCheckpoint) :
    let out := stepCheckpointReplaySession s c
    out.session.replayBudget = s.replayBudget ∧
    out.session.initialVisited = s.initialVisited ∧
    out.session.attemptedReplayVisits = s.attemptedReplayVisits + out.receipt.replayVisits ∧
    out.session.remaining + out.receipt.replayVisits = s.remaining ∧
    out.session.attemptedSnapshots = s.attemptedSnapshots + 1 ∧
    out.session.acceptedVisitDelta = s.acceptedVisitDelta +
      (if out.receipt.verdict = .accepted then out.receipt.replayVisits else 0) ∧
    out.session.discardedReplayVisits = s.discardedReplayVisits +
      (if out.receipt.verdict = .accepted then 0 else out.receipt.replayVisits) ∧
    out.session.acceptedSnapshots = s.acceptedSnapshots +
      (if out.receipt.verdict = .accepted then 1 else 0) := by
  have hr := meterCheckpointTransition_visits_le s.anchor s.remaining c
  unfold stepCheckpointReplaySession
  dsimp only
  split
  · rename_i hc
    have hv := meterCheckpointTransition_accepted_visits s.anchor c hc
    simp only [CheckpointReplaySession.remaining] at *
    refine ⟨trivial, trivial, trivial, ?_, trivial, ?_, rfl, trivial⟩
    · simpa only [Nat.sub_sub] using (Nat.sub_add_cancel hr)
    · exact congrArg (s.acceptedVisitDelta + ·) hv.symm
  · rename_i hc
    simp only [CheckpointReplaySession.remaining] at *
    refine ⟨trivial, trivial, trivial, ?_, trivial, rfl, trivial, rfl⟩
    simpa only [Nat.sub_sub] using (Nat.sub_add_cancel hr)

/-- No rejected or deferred candidate is installed, even if its replay spent quota. -/
theorem stepCheckpointReplaySession_retains_anchor {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (c : RectangleCheckpoint)
    (hc : (meterCheckpointTransition s.anchor s.remaining c).verdict ≠ .accepted) :
    (stepCheckpointReplaySession s c).session.anchor = s.anchor ∧
    (stepCheckpointReplaySession s c).session.acceptedVisitDelta = s.acceptedVisitDelta ∧
    (stepCheckpointReplaySession s c).session.discardedReplayVisits =
      s.discardedReplayVisits + (meterCheckpointTransition s.anchor s.remaining c).replayVisits := by
  simp [stepCheckpointReplaySession, hc]

/-- An accepted candidate is installed exactly, not replaced by an unlabelled substitute. -/
theorem stepCheckpointReplaySession_accepts_candidate {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (c : RectangleCheckpoint)
    (hc : (meterCheckpointTransition s.anchor s.remaining c).verdict = .accepted) :
    (stepCheckpointReplaySession s c).session.anchor.checkpoint = c := by
  simp [stepCheckpointReplaySession, hc, advanceValidatedCheckpoint]

/-- Remaining quota can only decrease; failures cannot replenish it. -/
theorem stepCheckpointReplaySession_remaining_le {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (c : RectangleCheckpoint) :
    (stepCheckpointReplaySession s c).session.remaining ≤ s.remaining := by
  have h := stepCheckpointReplaySession_accounting s c
  omega

/-- At zero remainder only an exact repeated anchor can be accepted. -/
theorem stepCheckpointReplaySession_zero_remaining {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (c : RectangleCheckpoint) (hz : s.remaining = 0) :
    (stepCheckpointReplaySession s c).receipt.verdict = .accepted ↔ c = s.anchor.checkpoint := by
  rw [stepCheckpointReplaySession_receipt, meterCheckpointTransition_verdict, hz]
  exact validateCheckpointTransition_zero_limit_iff s.anchor c

end KomorebiPadic
