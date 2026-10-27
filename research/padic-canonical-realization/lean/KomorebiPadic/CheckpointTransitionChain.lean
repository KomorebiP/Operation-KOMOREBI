import KomorebiPadic.IncrementalCheckpointImporter

/-!
# Proof-carrying incremental checkpoint chains

Validation halts at the first rejected or deferred successor. The returned anchor
is always the last certified state. `acceptedVisitDelta` counts only committed
successful increments, not work spent parsing or rejecting a later candidate.
-/
namespace KomorebiPadic

structure CheckpointTransitionChainResult (p : ℕ) (b : ParameterBox) where
  anchor : ValidatedRectangleCheckpoint p b
  acceptedCount : ℕ
  acceptedVisitDelta : ℕ
  verdict : CheckpointVerdict

/-- No root replay is executed between successive candidates. -/
def runCheckpointTransitionChain {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (deltaLimit : ℕ) :
    List RectangleCheckpoint → CheckpointTransitionChainResult p b
  | [] => ⟨a, 0, 0, .accepted⟩
  | c :: cs =>
    let verdict := validateCheckpointTransition a deltaLimit c
    if hc : verdict = .accepted then
      let rest := runCheckpointTransitionChain (advanceValidatedCheckpoint a c hc) deltaLimit cs
      ⟨rest.anchor, rest.acceptedCount + 1,
        checkpointTransitionDelta a c + rest.acceptedVisitDelta, rest.verdict⟩
    else ⟨a, 0, 0, verdict⟩

/-- Exact telescoping of successful increments, and a per-success quota bound.
Failed-attempt work is deliberately not included in acceptedVisitDelta. -/
theorem runCheckpointTransitionChain_accounting {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (cs : List RectangleCheckpoint) :
    let out := runCheckpointTransitionChain a limit cs
    a.checkpoint.state.visited ≤ out.anchor.checkpoint.state.visited ∧
    out.acceptedVisitDelta = out.anchor.checkpoint.state.visited - a.checkpoint.state.visited ∧
    out.acceptedCount ≤ cs.length ∧ out.acceptedVisitDelta ≤ out.acceptedCount * limit := by
  induction cs generalizing a with
  | nil => simp [runCheckpointTransitionChain]
  | cons c cs ih =>
    by_cases hc : validateCheckpointTransition a limit c = .accepted
    · simp only [runCheckpointTransitionChain, hc, ↓reduceDIte]
      have ht := ih (advanceValidatedCheckpoint a c hc)
      have hv := validateCheckpointTransition_counter_bounds hc
      have hd := ((validateCheckpointTransition_accepted_iff a limit c).mp hc).2.1
      dsimp only [advanceValidatedCheckpoint] at ht
      simp only [List.length_cons, Nat.add_mul, Nat.one_mul]
      simp only [checkpointTransitionDelta, advanceValidatedCheckpoint] at hd ⊢
      omega
    · simp [runCheckpointTransitionChain, hc]

/-- All candidates succeeded exactly when the accepted prefix consumes the input list. -/
theorem runCheckpointTransitionChain_accepted_iff_count {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (cs : List RectangleCheckpoint) :
    (runCheckpointTransitionChain a limit cs).verdict = .accepted ↔
      (runCheckpointTransitionChain a limit cs).acceptedCount = cs.length := by
  induction cs generalizing a with
  | nil => simp [runCheckpointTransitionChain]
  | cons c cs ih =>
    by_cases hc : validateCheckpointTransition a limit c = .accepted
    · simpa only [runCheckpointTransitionChain, hc, ↓reduceDIte, List.length_cons,
        Nat.add_right_cancel_iff] using ih (advanceValidatedCheckpoint a c hc)
    · simp [runCheckpointTransitionChain, hc]

/-- A failed or deferred first candidate cannot overwrite the certified anchor. -/
theorem runCheckpointTransitionChain_stops_before_invalid {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (c : RectangleCheckpoint)
    (cs : List RectangleCheckpoint) (hc : validateCheckpointTransition a limit c ≠ .accepted) :
    (runCheckpointTransitionChain a limit (c :: cs)).anchor.checkpoint = a.checkpoint ∧
    (runCheckpointTransitionChain a limit (c :: cs)).acceptedCount = 0 ∧
    (runCheckpointTransitionChain a limit (c :: cs)).acceptedVisitDelta = 0 ∧
    (runCheckpointTransitionChain a limit (c :: cs)).verdict = validateCheckpointTransition a limit c := by
  simp [runCheckpointTransitionChain, hc]

/-- The certified prefix, even on a halted chain, validates directly from its initial anchor. -/
theorem runCheckpointTransitionChain_direct_validation {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (cs : List RectangleCheckpoint) :
    let out := runCheckpointTransitionChain a limit cs
    validateCheckpointTransition a out.acceptedVisitDelta out.anchor.checkpoint = .accepted := by
  dsimp only
  have ht := runCheckpointTransitionChain_accounting a limit cs
  apply (validateCheckpointTransition_accepted_iff_canonical _ _ _).mpr
  exact ⟨(runCheckpointTransitionChain a limit cs).anchor.metadata, ht.1,
    by simpa only [checkpointTransitionDelta] using ht.2.1.ge,
    (runCheckpointTransitionChain a limit cs).anchor.canonical⟩

/-- Exact restart is preserved after arbitrarily many accepted increments. -/
theorem runCheckpointTransitionChain_restart {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (cs : List RectangleCheckpoint)
    (extra : ℕ) :
    let out := runCheckpointTransitionChain a limit cs
    runRectangleQueue p extra out.anchor.checkpoint.state =
      budgetedDecompose p (a.checkpoint.state.visited + out.acceptedVisitDelta + extra) b := by
  dsimp only
  have ht := runCheckpointTransitionChain_accounting a limit cs
  have hn : a.checkpoint.state.visited +
      (runCheckpointTransitionChain a limit cs).acceptedVisitDelta =
      (runCheckpointTransitionChain a limit cs).anchor.checkpoint.state.visited := by omega
  rw [hn]
  exact validateRectangleCheckpoint_restart
    (runCheckpointTransitionChain a limit cs).anchor.rootAccepted extra

/-- Zero allowance accepts only repeated copies of the same anchor. -/
theorem validateCheckpointTransition_zero_limit_iff {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (c : RectangleCheckpoint) :
    validateCheckpointTransition a 0 c = .accepted ↔ c = a.checkpoint := by
  constructor
  · intro hc
    have hv := validateCheckpointTransition_counter_bounds hc
    exact (validateCheckpointTransition_same_counter_iff a c (by omega)).mp hc
  · rintro rfl
    exact validateCheckpointTransition_self a 0

end KomorebiPadic
