import KomorebiPadic.ReplayBudgetTransport

/-!
# Persistent submission quota beside the replay quota

Every admitted input spends one submission, including malformed, rejected,
deferred, and zero-replay inputs. A global stop is not a candidate verdict.
No inherited replay or transport policy is changed.
-/
namespace KomorebiPadic

/-- Both policies cap submissions. The strict policy also stops before inspecting
an input when no successor replay allowance remains. -/
inductive SubmissionQuotaPolicy where
  | allowZeroReplay
  | stopAtReplayExhaustion
  deriving DecidableEq, Repr, BEq

/-- These are stream-level stop reasons, not validation verdicts. -/
inductive SubmissionStreamHalt where
  | inputExhausted
  | submissionQuota
  | replayQuota
  deriving DecidableEq, Repr, BEq

/-- The original replay ledger is retained without resetting its allowance. -/
structure CheckpointSubmissionSession (p : ℕ) (b : ParameterBox) where
  replay : CheckpointReplaySession p b
  submissionBudget : ℕ
  initialSnapshots : ℕ
  spentSubmissions : ℕ
  submission_safe : spentSubmissions ≤ submissionBudget
  snapshots_exact : replay.attemptedSnapshots = initialSnapshots + spentSubmissions

/-- Explicitly allocate a submission quota around an existing certified replay
session. This constructor does not allocate or refill replay allowance. -/
def withCheckpointSubmissionQuota {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (budget : ℕ) : CheckpointSubmissionSession p b where
  replay := s
  submissionBudget := budget
  initialSnapshots := s.attemptedSnapshots
  spentSubmissions := 0
  submission_safe := Nat.zero_le _
  snapshots_exact := (Nat.add_zero _).symm

def CheckpointSubmissionSession.remaining {p : ℕ} {b : ParameterBox}
    (s : CheckpointSubmissionSession p b) : ℕ :=
  s.submissionBudget - s.spentSubmissions

/-- Independent ledgers: messages cannot be exchanged for replay visits. -/
theorem CheckpointSubmissionSession.conservation {p : ℕ} {b : ParameterBox}
    (s : CheckpointSubmissionSession p b) :
    s.spentSubmissions + s.remaining = s.submissionBudget ∧
    s.replay.attemptedSnapshots = s.initialSnapshots + s.spentSubmissions ∧
    s.replay.acceptedVisitDelta + s.replay.discardedReplayVisits +
      s.replay.remaining = s.replay.replayBudget := by
  have hs := s.submission_safe
  have hr := s.replay.conservation
  exact ⟨by unfold remaining; omega, s.snapshots_exact, hr.2.2.2⟩

/-- A caller cannot gain allowance by changing policies mid-session. -/
def checkpointSubmissionGate {p : ℕ} {b : ParameterBox}
    (policy : SubmissionQuotaPolicy) (s : CheckpointSubmissionSession p b) :
    Option SubmissionStreamHalt :=
  if s.spentSubmissions < s.submissionBudget then
    if policy = .stopAtReplayExhaustion ∧ s.replay.remaining = 0 then
      some .replayQuota
    else none
  else some .submissionQuota

theorem checkpointSubmissionGate_available {p : ℕ} {b : ParameterBox}
    {policy : SubmissionQuotaPolicy} {s : CheckpointSubmissionSession p b}
    (hg : checkpointSubmissionGate policy s = none) :
    s.spentSubmissions < s.submissionBudget := by
  by_contra hn
  simp [checkpointSubmissionGate, hn] at hg

/-- Every adapter step is already proved to conserve the inherited replay ledger
and charge exactly one attempted snapshot. Proof fields erase at execution. -/
structure CheckpointInputAdapter (α : Type) (p : ℕ) (b : ParameterBox) where
  step : CheckpointReplaySession p b → α → CheckpointReplayStepResult p b
  conserves : ∀ s x, ReplayTransportConserves s (step s x)

structure CheckpointSubmissionStepResult (p : ℕ) (b : ParameterBox) where
  session : CheckpointSubmissionSession p b
  receipt : CheckpointReplayReceipt

/-- One adapter call; a rejected or deferred input still spends a submission. -/
def consumeCheckpointSubmission {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (s : CheckpointSubmissionSession p b)
    (x : α) (hs : s.spentSubmissions < s.submissionBudget) :
    CheckpointSubmissionStepResult p b :=
  let step := adapter.step s.replay x
  ⟨{ replay := step.session
     submissionBudget := s.submissionBudget
     initialSnapshots := s.initialSnapshots
     spentSubmissions := s.spentSubmissions + 1
     submission_safe := hs
     snapshots_exact := by
       have hc := (adapter.conserves s.replay x).2.2.2.2
       rw [hc, s.snapshots_exact]
       omega }, step.receipt⟩

theorem consumeCheckpointSubmission_accounting {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (s : CheckpointSubmissionSession p b)
    (x : α) (hs : s.spentSubmissions < s.submissionBudget) :
    let out := consumeCheckpointSubmission adapter s x hs
    out.session.submissionBudget = s.submissionBudget ∧
    out.session.initialSnapshots = s.initialSnapshots ∧
    out.session.spentSubmissions = s.spentSubmissions + 1 ∧
    out.session.remaining + 1 = s.remaining ∧
    out.session.replay.replayBudget = s.replay.replayBudget ∧
    out.session.replay.initialVisited = s.replay.initialVisited ∧
    out.session.replay.attemptedReplayVisits =
      s.replay.attemptedReplayVisits + out.receipt.replayVisits ∧
    out.session.replay.remaining + out.receipt.replayVisits = s.replay.remaining := by
  have ha := adapter.conserves s.replay x
  dsimp only [ReplayTransportConserves] at ha
  refine ⟨rfl, rfl, rfl, ?_, ha.1, ha.2.1, ha.2.2.1, ha.2.2.2.1⟩
  dsimp only [consumeCheckpointSubmission, CheckpointSubmissionSession.remaining]
  omega

/-- Ordered consumed prefix and exact original suffix. Neither list is deduplicated. -/
structure CheckpointSubmissionStreamResult (α : Type) (p : ℕ) (b : ParameterBox) where
  session : CheckpointSubmissionSession p b
  processed : List α
  receipts : List CheckpointReplayReceipt
  pending : List α
  halt : SubmissionStreamHalt

/-- Gate before the adapter. Inputs after a global stop are never sent to decoding,
metadata checking, equality, or replay by this function. -/
def runCheckpointSubmissionStream {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (policy : SubmissionQuotaPolicy)
    (s : CheckpointSubmissionSession p b) :
    List α → CheckpointSubmissionStreamResult α p b
  | [] => ⟨s, [], [], [], .inputExhausted⟩
  | x :: xs =>
    if hg : checkpointSubmissionGate policy s = none then
      let step := consumeCheckpointSubmission adapter s x
        (checkpointSubmissionGate_available hg)
      let tail := runCheckpointSubmissionStream adapter policy step.session xs
      ⟨tail.session, x :: tail.processed, step.receipt :: tail.receipts,
        tail.pending, tail.halt⟩
    else ⟨s, [], [], x :: xs,
      (checkpointSubmissionGate policy s).getD .submissionQuota⟩

/-- The quota gate leaves a blocked head and the entire suffix literally untouched. -/
theorem runCheckpointSubmissionStream_blocked {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (policy : SubmissionQuotaPolicy)
    (s : CheckpointSubmissionSession p b) (x : α) (xs : List α)
    {reason : SubmissionStreamHalt} (hg : checkpointSubmissionGate policy s = some reason) :
    runCheckpointSubmissionStream adapter policy s (x :: xs) =
      ⟨s, [], [], x :: xs, reason⟩ := by
  simp [runCheckpointSubmissionStream, hg]

/-- Lossless prefix consumption, exact submission charge, and receipt-aligned replay cost. -/
theorem runCheckpointSubmissionStream_accounting {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (policy : SubmissionQuotaPolicy)
    (s : CheckpointSubmissionSession p b) (xs : List α) :
    let out := runCheckpointSubmissionStream adapter policy s xs
    out.processed ++ out.pending = xs ∧
    out.receipts.length = out.processed.length ∧
    out.session.submissionBudget = s.submissionBudget ∧
    out.session.initialSnapshots = s.initialSnapshots ∧
    out.session.spentSubmissions = s.spentSubmissions + out.processed.length ∧
    out.session.remaining + out.processed.length = s.remaining ∧
    out.session.replay.replayBudget = s.replay.replayBudget ∧
    out.session.replay.initialVisited = s.replay.initialVisited ∧
    out.session.replay.attemptedReplayVisits =
      s.replay.attemptedReplayVisits + receiptReplaySum out.receipts ∧
    out.session.replay.remaining + receiptReplaySum out.receipts = s.replay.remaining := by
  induction xs generalizing s with
  | nil => simp [runCheckpointSubmissionStream, receiptReplaySum]
  | cons x xs ih =>
    cases hg : checkpointSubmissionGate policy s with
    | some reason => simp [runCheckpointSubmissionStream, hg, receiptReplaySum]
    | none =>
      let step := consumeCheckpointSubmission adapter s x (checkpointSubmissionGate_available hg)
      have hs := consumeCheckpointSubmission_accounting adapter s x
        (checkpointSubmissionGate_available hg)
      have ht := ih step.session
      dsimp only at hs ht
      simp only [runCheckpointSubmissionStream, hg, ↓reduceDIte]
      change (x :: (runCheckpointSubmissionStream adapter policy step.session xs).processed) ++
        (runCheckpointSubmissionStream adapter policy step.session xs).pending = x :: xs ∧ _
      refine ⟨congrArg (List.cons x) ht.1, ?_⟩
      simp only [List.length_cons, receiptReplaySum]
      dsimp only [step] at ht ⊢
      omega

/-- Exact original suffix, even with repeated or malformed inputs. -/
theorem runCheckpointSubmissionStream_prefix {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (policy : SubmissionQuotaPolicy)
    (s : CheckpointSubmissionSession p b) (xs : List α) :
    let out := runCheckpointSubmissionStream adapter policy s xs
    out.processed = xs.take out.receipts.length ∧
      out.pending = xs.drop out.receipts.length := by
  have ha := runCheckpointSubmissionStream_accounting adapter policy s xs
  dsimp only at ha ⊢
  generalize runCheckpointSubmissionStream adapter policy s xs = out at ha ⊢
  rw [← ha.1, ha.2.1]
  simp

/-- Both resources remain globally bounded, without claiming a bit or time bound. -/
theorem runCheckpointSubmissionStream_bounds {α : Type} {p : ℕ} {b : ParameterBox}
    (adapter : CheckpointInputAdapter α p b) (policy : SubmissionQuotaPolicy)
    (s : CheckpointSubmissionSession p b) (xs : List α) :
    let out := runCheckpointSubmissionStream adapter policy s xs
    out.processed.length ≤ s.remaining ∧
    receiptReplaySum out.receipts ≤ s.replay.remaining ∧
    out.session.spentSubmissions ≤ s.submissionBudget ∧
    out.session.replay.attemptedReplayVisits ≤ s.replay.replayBudget := by
  have ha := runCheckpointSubmissionStream_accounting adapter policy s xs
  have hs := (runCheckpointSubmissionStream adapter policy s xs).session.submission_safe
  have hr := (runCheckpointSubmissionStream adapter policy s xs).session.replay.budget_safe
  dsimp only at ha ⊢
  omega

end KomorebiPadic
