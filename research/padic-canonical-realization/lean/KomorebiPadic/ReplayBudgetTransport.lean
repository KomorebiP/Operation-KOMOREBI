import KomorebiPadic.CheckpointReplayStream

/-!
# Transport into the same global replay session

Malformed or over-limit inputs do not replay and do not reset the ledger.
The existing word codec and JSON parser remain unchanged. This is not a new
JSON grammar or file-read memory bound.
-/
namespace KomorebiPadic

/-- Record an input rejected or deferred before queue replay. -/
def skipCheckpointReplayInput {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (defer : Bool) : CheckpointReplayStepResult p b :=
  ⟨{ s with attemptedSnapshots := s.attemptedSnapshots + 1 },
   ⟨if defer then .deferred else .rejected, 0⟩⟩

/-- Word framing precedes typed metered validation. Only the latter may replay. -/
def stepCheckpointReplayWords {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (wordLimit : ℕ) (words : List ℕ) :
    CheckpointReplayStepResult p b :=
  if words.length ≤ wordLimit then
    match decodeRectangleCheckpoint words with
    | none => skipCheckpointReplayInput s false
    | some c => stepCheckpointReplaySession s c
  else skipCheckpointReplayInput s true

/-- Reuse the pinned JSON transport; acceptance does not trust any session fields in the file. -/
def stepCheckpointReplayText {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (byteLimit wordLimit : ℕ) (text : String) :
    CheckpointReplayStepResult p b :=
  if text.utf8ByteSize ≤ byteLimit then
    match parseCheckpointWords text with
    | none => skipCheckpointReplayInput s false
    | some words => stepCheckpointReplayWords s wordLimit words
  else skipCheckpointReplayInput s true

/-- Transport prechecks change no spending, accepted counter, or certified anchor. -/
theorem skipCheckpointReplayInput_spec {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (defer : Bool) :
    (skipCheckpointReplayInput s defer).receipt.replayVisits = 0 ∧
    (skipCheckpointReplayInput s defer).receipt.verdict ≠ .accepted ∧
    (skipCheckpointReplayInput s defer).session.anchor = s.anchor ∧
    (skipCheckpointReplayInput s defer).session.remaining = s.remaining := by
  cases defer <;> simp [skipCheckpointReplayInput, CheckpointReplaySession.remaining]

/-- Exact accepted-word criterion uses the current global remainder. -/
theorem stepCheckpointReplayWords_accepted_iff {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (wordLimit : ℕ) (words : List ℕ) :
    (stepCheckpointReplayWords s wordLimit words).receipt.verdict = .accepted ↔
      words.length ≤ wordLimit ∧ ∃ c, decodeRectangleCheckpoint words = some c ∧
        validateCheckpointTransition s.anchor s.remaining c = .accepted := by
  unfold stepCheckpointReplayWords
  by_cases hw : words.length ≤ wordLimit
  · simp only [hw, ↓reduceIte, true_and]
    cases hd : decodeRectangleCheckpoint words with
    | none => simp [skipCheckpointReplayInput]
    | some c =>
      simp only [Option.some.injEq, exists_eq_left', stepCheckpointReplaySession_receipt,
        meterCheckpointTransition_verdict]
  · simp [hw, skipCheckpointReplayInput]

/-- Accepted words install the exact snapshot whose canonical encoding was supplied. -/
theorem stepCheckpointReplayWords_accepted_data {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (wordLimit : ℕ) (words : List ℕ)
    (hc : (stepCheckpointReplayWords s wordLimit words).receipt.verdict = .accepted) :
    encodeRectangleCheckpoint
      (stepCheckpointReplayWords s wordLimit words).session.anchor.checkpoint = words := by
  obtain ⟨hw, c, hd, hv⟩ := (stepCheckpointReplayWords_accepted_iff _ _ _).mp hc
  simp only [stepCheckpointReplayWords, hw, ↓reduceIte, hd]
  rw [stepCheckpointReplaySession_accepts_candidate s c
    ((meterCheckpointTransition_verdict _ _ _).trans hv)]
  exact decodeRectangleCheckpoint_sound words c hd

/-- The transport-level conservation relation includes zero-cost precheck exits. -/
def ReplayTransportConserves {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (out : CheckpointReplayStepResult p b) : Prop :=
  out.session.replayBudget = s.replayBudget ∧
  out.session.initialVisited = s.initialVisited ∧
  out.session.attemptedReplayVisits = s.attemptedReplayVisits + out.receipt.replayVisits ∧
  out.session.remaining + out.receipt.replayVisits = s.remaining ∧
  out.session.attemptedSnapshots = s.attemptedSnapshots + 1

theorem stepCheckpointReplayWords_conserves {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (wordLimit : ℕ) (words : List ℕ) :
    ReplayTransportConserves s (stepCheckpointReplayWords s wordLimit words) := by
  unfold stepCheckpointReplayWords
  split
  · cases decodeRectangleCheckpoint words with
    | none => simp [ReplayTransportConserves, skipCheckpointReplayInput, CheckpointReplaySession.remaining]
    | some c =>
      have h := stepCheckpointReplaySession_accounting s c
      exact ⟨h.1, h.2.1, h.2.2.1, h.2.2.2.1, h.2.2.2.2.1⟩
  · simp [ReplayTransportConserves, skipCheckpointReplayInput, CheckpointReplaySession.remaining]

theorem stepCheckpointReplayText_conserves {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (byteLimit wordLimit : ℕ) (text : String) :
    ReplayTransportConserves s (stepCheckpointReplayText s byteLimit wordLimit text) := by
  unfold stepCheckpointReplayText
  split
  · cases parseCheckpointWords text with
    | none => simp [ReplayTransportConserves, skipCheckpointReplayInput, CheckpointReplaySession.remaining]
    | some words => exact stepCheckpointReplayWords_conserves s wordLimit words
  · simp [ReplayTransportConserves, skipCheckpointReplayInput, CheckpointReplaySession.remaining]

/-- Nonacceptance at any word-import exit retains the last certified anchor literally. -/
theorem stepCheckpointReplayWords_retains {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (wordLimit : ℕ) (words : List ℕ)
    (hc : (stepCheckpointReplayWords s wordLimit words).receipt.verdict ≠ .accepted) :
    (stepCheckpointReplayWords s wordLimit words).session.anchor = s.anchor := by
  by_cases hw : words.length ≤ wordLimit
  · cases hd : decodeRectangleCheckpoint words with
    | none => simp [stepCheckpointReplayWords, hw, hd, skipCheckpointReplayInput]
    | some c =>
      simp only [stepCheckpointReplayWords, hw, ↓reduceIte, hd] at hc ⊢
      rw [stepCheckpointReplaySession_receipt] at hc
      exact (stepCheckpointReplaySession_retains_anchor s c hc).1
  · simp [stepCheckpointReplayWords, hw, skipCheckpointReplayInput]

/-- Transport rejection and deferral never install arbitrary words as the anchor. -/
theorem stepCheckpointReplayText_retains {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (byteLimit wordLimit : ℕ) (text : String)
    (hc : (stepCheckpointReplayText s byteLimit wordLimit text).receipt.verdict ≠ .accepted) :
    (stepCheckpointReplayText s byteLimit wordLimit text).session.anchor = s.anchor := by
  by_cases hb : text.utf8ByteSize ≤ byteLimit
  · cases ht : parseCheckpointWords text with
    | none => simp [stepCheckpointReplayText, hb, ht, skipCheckpointReplayInput]
    | some words =>
      simp only [stepCheckpointReplayText, hb, ↓reduceIte, ht] at hc ⊢
      exact stepCheckpointReplayWords_retains s wordLimit words hc
  · simp [stepCheckpointReplayText, hb, skipCheckpointReplayInput]

/-- Every returned transport result retains the full partition certificate. -/
theorem stepCheckpointReplayText_has_certificate {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (byteLimit wordLimit : ℕ) (text : String) :
    ∃ cert : BudgetedPartitionCertificate p
      (stepCheckpointReplayText s byteLimit wordLimit text).session.anchor.checkpoint.state.visited b,
      cert.result = (stepCheckpointReplayText s byteLimit wordLimit text).session.anchor.checkpoint.state := by
  exact validateRectangleCheckpoint_has_certificate
    (stepCheckpointReplayText s byteLimit wordLimit text).session.anchor.rootAccepted

/-- Exact accepted-text criterion; grammar/roundtrip of the parser is not assumed. -/
theorem stepCheckpointReplayText_accepted_iff {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (byteLimit wordLimit : ℕ) (text : String) :
    (stepCheckpointReplayText s byteLimit wordLimit text).receipt.verdict = .accepted ↔
      text.utf8ByteSize ≤ byteLimit ∧ ∃ words, parseCheckpointWords text = some words ∧
        words.length ≤ wordLimit ∧ ∃ c, decodeRectangleCheckpoint words = some c ∧
          validateCheckpointTransition s.anchor s.remaining c = .accepted := by
  unfold stepCheckpointReplayText
  by_cases hb : text.utf8ByteSize ≤ byteLimit
  · simp only [hb, ↓reduceIte, true_and]
    cases ht : parseCheckpointWords text with
    | none => simp [skipCheckpointReplayInput]
    | some words =>
      simpa only [Option.some.injEq, exists_eq_left'] using
        stepCheckpointReplayWords_accepted_iff s wordLimit words
  · simp [hb, skipCheckpointReplayInput]

/-- A pure finite JSON-input stream using the same proof-carrying in-memory quota. -/
def runCheckpointReplayTextStream {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (byteLimit wordLimit : ℕ) :
    List String → CheckpointReplayStreamResult p b
  | [] => ⟨s, []⟩
  | text :: rest =>
    let step := stepCheckpointReplayText s byteLimit wordLimit text
    let tail := runCheckpointReplayTextStream step.session byteLimit wordLimit rest
    ⟨tail.session, step.receipt :: tail.receipts⟩

/-- Even malformed and quota-deferred messages cannot reset or exceed the global budget. -/
theorem runCheckpointReplayTextStream_accounting {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (byteLimit wordLimit : ℕ) (texts : List String) :
    let out := runCheckpointReplayTextStream s byteLimit wordLimit texts
    out.session.replayBudget = s.replayBudget ∧
    out.session.initialVisited = s.initialVisited ∧
    out.session.attemptedReplayVisits = s.attemptedReplayVisits + receiptReplaySum out.receipts ∧
    out.session.remaining + receiptReplaySum out.receipts = s.remaining ∧
    out.session.attemptedSnapshots = s.attemptedSnapshots + texts.length ∧
    out.receipts.length = texts.length := by
  induction texts generalizing s with
  | nil => simp [runCheckpointReplayTextStream, receiptReplaySum]
  | cons t ts ih =>
    have hs := stepCheckpointReplayText_conserves s byteLimit wordLimit t
    have hr := ih (stepCheckpointReplayText s byteLimit wordLimit t).session
    dsimp only [ReplayTransportConserves] at hs
    dsimp only at hr
    simp only [runCheckpointReplayTextStream, receiptReplaySum, List.length_cons]
    omega

theorem runCheckpointReplayTextStream_budget_bound {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (byteLimit wordLimit : ℕ) (texts : List String) :
    receiptReplaySum (runCheckpointReplayTextStream s byteLimit wordLimit texts).receipts ≤ s.remaining ∧
    (runCheckpointReplayTextStream s byteLimit wordLimit texts).session.attemptedReplayVisits ≤ s.replayBudget := by
  have ha := runCheckpointReplayTextStream_accounting s byteLimit wordLimit texts
  have hb := (runCheckpointReplayTextStream s byteLimit wordLimit texts).session.budget_safe
  omega

/-- Text batching preserves the exact ledger, validated state, and ordered verdict receipts. -/
theorem runCheckpointReplayTextStream_append {p : ℕ} {b : ParameterBox}
    (s : CheckpointReplaySession p b) (byteLimit wordLimit : ℕ) (xs ys : List String) :
    runCheckpointReplayTextStream s byteLimit wordLimit (xs ++ ys) =
      let first := runCheckpointReplayTextStream s byteLimit wordLimit xs
      let second := runCheckpointReplayTextStream first.session byteLimit wordLimit ys
      ⟨second.session, first.receipts ++ second.receipts⟩ := by
  induction xs generalizing s with
  | nil => rfl
  | cons x xs ih =>
    simp only [List.cons_append, runCheckpointReplayTextStream]
    rw [ih]

/-- A checked witness that rejected replay consumes the whole one-visit allowance. -/
theorem rejectedReplay_is_not_free :
    let b : ParameterBox := ⟨1, 2, 0, 0⟩
    let c0 := exportRectangleCheckpoint 2 0 b
    let a : ValidatedRectangleCheckpoint 2 b := validatedRectangleCheckpointOfAccepted
      (by decide +kernel : validateRectangleCheckpoint 2 b 0 c0 = .accepted)
    let c := { c0 with state := { c0.state with visited := 1 } }
    let out := stepCheckpointReplaySession (startCheckpointReplaySession a 1) c
    out.receipt = ⟨.rejected, 1⟩ ∧ out.session.remaining = 0 ∧
      out.session.acceptedVisitDelta = 0 ∧ out.session.discardedReplayVisits = 1 ∧
      out.session.anchor.checkpoint = c0 := by
  decide +kernel

/-- Claiming three visits on a one-visit plateau spends only one, and is rejected. -/
theorem completionShortfall_is_not_claimed_charge :
    let b : ParameterBox := ⟨1, 2, 1, 1⟩
    let c0 := exportRectangleCheckpoint 2 0 b
    let a : ValidatedRectangleCheckpoint 2 b := validatedRectangleCheckpointOfAccepted
      (by decide +kernel : validateRectangleCheckpoint 2 b 0 c0 = .accepted)
    let c := { c0 with state := { c0.state with visited := 3 } }
    checkpointTransitionMetadata a c ∧ checkpointTransitionDelta a c = 3 ∧
      meterCheckpointTransition a 3 c = ⟨.rejected, 1⟩ := by
  decide +kernel

end KomorebiPadic
