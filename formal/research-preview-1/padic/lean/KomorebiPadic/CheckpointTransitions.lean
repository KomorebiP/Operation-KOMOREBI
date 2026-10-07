import KomorebiPadic.CheckpointImporter

/-!
# Incremental validation from a certified anchor

The anchor carries mathematical context and canonical-state proofs. A candidate
is checked by replaying only its claimed visit increment. The counter-order guard
rejects rollback before using truncated natural subtraction. Proof fields are erased;
constructing or promoting an anchor does not execute a root replay.
-/
namespace KomorebiPadic

/-- A trust anchor is evidence, not a Boolean flag or unverified serialized field. -/
structure ValidatedRectangleCheckpoint (p : ℕ) (b : ParameterBox) where
  checkpoint : RectangleCheckpoint
  metadata : checkpoint.MetadataValid p b
  canonical : checkpoint.Canonical p b

/-- Bootstrap from the previously checked root importer. -/
def validatedRectangleCheckpointOfAccepted {p limit : ℕ} {b : ParameterBox}
    {c : RectangleCheckpoint} (hc : validateRectangleCheckpoint p b limit c = .accepted) :
    ValidatedRectangleCheckpoint p b where
  checkpoint := c
  metadata := ((validateRectangleCheckpoint_accepted_iff _ _ _ _).mp hc).1
  canonical := ((validateRectangleCheckpoint_accepted_iff _ _ _ _).mp hc).2.2

/-- A certified anchor satisfies the old root criterion at its actual visit count. -/
theorem ValidatedRectangleCheckpoint.rootAccepted {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) :
    validateRectangleCheckpoint p b a.checkpoint.state.visited a.checkpoint = .accepted := by
  exact (validateRectangleCheckpoint_accepted_iff _ _ _ _).mpr
    ⟨a.metadata, le_rfl, a.canonical⟩

/-- The incremental budget is derived from counters, not a separately trusted claim. -/
def checkpointTransitionDelta {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (c : RectangleCheckpoint) : ℕ :=
  c.state.visited - a.checkpoint.state.visited

/-- Context and nonrollback checks precede any queue replay. -/
def checkpointTransitionMetadata {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (c : RectangleCheckpoint) : Prop :=
  c.MetadataValid p b ∧ a.checkpoint.state.visited ≤ c.state.visited

instance {p : ℕ} {b : ParameterBox} (a : ValidatedRectangleCheckpoint p b)
    (c : RectangleCheckpoint) : Decidable (checkpointTransitionMetadata a c) :=
  inferInstanceAs (Decidable (c.MetadataValid p b ∧
    a.checkpoint.state.visited ≤ c.state.visited))

/-- The only traversal executed here starts at the supplied certified anchor. -/
def validateCheckpointTransition {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (deltaLimit : ℕ)
    (c : RectangleCheckpoint) : CheckpointVerdict :=
  if checkpointTransitionMetadata a c then
    if checkpointTransitionDelta a c ≤ deltaLimit then
      if c.state = runRectangleQueue p (checkpointTransitionDelta a c) a.checkpoint.state
      then .accepted else .rejected
    else .deferred
  else .rejected

/-- Exact operational acceptance condition, including full ordered state equality. -/
theorem validateCheckpointTransition_accepted_iff {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (c : RectangleCheckpoint) :
    validateCheckpointTransition a limit c = .accepted ↔
      checkpointTransitionMetadata a c ∧ checkpointTransitionDelta a c ≤ limit ∧
      c.state = runRectangleQueue p (checkpointTransitionDelta a c) a.checkpoint.state := by
  simp only [validateCheckpointTransition]
  split <;> simp_all
  split <;> simp_all

/-- Lack of incremental allowance does not establish candidate validity. -/
theorem validateCheckpointTransition_deferred_iff {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (c : RectangleCheckpoint) :
    validateCheckpointTransition a limit c = .deferred ↔
      checkpointTransitionMetadata a c ∧ limit < checkpointTransitionDelta a c := by
  simp only [validateCheckpointTransition]
  split <;> simp_all
  split <;> simp_all

/-- Bad context or rollback rejects before executing a replay. -/
theorem validateCheckpointTransition_bad_metadata {p limit : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (c : RectangleCheckpoint)
    (hm : ¬ checkpointTransitionMetadata a c) :
    validateCheckpointTransition a limit c = .rejected := by
  simp [validateCheckpointTransition, hm]

/-- A genuine older canonical checkpoint is still rejected relative to a newer anchor. -/
theorem validateCheckpointTransition_rollback {p limit : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (c : RectangleCheckpoint)
    (hv : c.state.visited < a.checkpoint.state.visited) :
    validateCheckpointTransition a limit c = .rejected := by
  exact validateCheckpointTransition_bad_metadata a c (fun hm => by
    have hh := hm.2
    omega)

/-- Incremental replay equality and global canonicality coincide after the order guard. -/
theorem checkpointTransition_replay_iff_canonical {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (c : RectangleCheckpoint)
    (hv : a.checkpoint.state.visited ≤ c.state.visited) :
    c.state = runRectangleQueue p (checkpointTransitionDelta a c) a.checkpoint.state ↔
      c.Canonical p b := by
  have hs : a.checkpoint.state = budgetedDecompose p a.checkpoint.state.visited b := a.canonical
  have he : runRectangleQueue p (checkpointTransitionDelta a c) a.checkpoint.state =
      budgetedDecompose p c.state.visited b := by
    rw [hs]
    change runRectangleQueue p (checkpointTransitionDelta a c)
      (runRectangleQueue p a.checkpoint.state.visited (initialRectangleQueue b)) = _
    rw [runRectangleQueue_add]
    have hn : a.checkpoint.state.visited + checkpointTransitionDelta a c = c.state.visited := by
      unfold checkpointTransitionDelta
      omega
    rw [hn]
    rfl
  rw [he]
  rfl

/-- Exact semantic equivalence: no canonical later checkpoint is lost by incremental replay. -/
theorem validateCheckpointTransition_accepted_iff_canonical {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) (c : RectangleCheckpoint) :
    validateCheckpointTransition a limit c = .accepted ↔
      c.MetadataValid p b ∧ a.checkpoint.state.visited ≤ c.state.visited ∧
      checkpointTransitionDelta a c ≤ limit ∧ c.Canonical p b := by
  rw [validateCheckpointTransition_accepted_iff]
  constructor
  · rintro ⟨hm, hl, hs⟩
    exact ⟨hm.1, hm.2, hl, (checkpointTransition_replay_iff_canonical a c hm.2).mp hs⟩
  · rintro ⟨hm, hv, hl, hs⟩
    exact ⟨⟨hm, hv⟩, hl, (checkpointTransition_replay_iff_canonical a c hv).mpr hs⟩

/-- Accepted increments are nonnegative and bounded by the caller's allowance. -/
theorem validateCheckpointTransition_counter_bounds {p limit : ℕ} {b : ParameterBox}
    {a : ValidatedRectangleCheckpoint p b} {c : RectangleCheckpoint}
    (hc : validateCheckpointTransition a limit c = .accepted) :
    a.checkpoint.state.visited ≤ c.state.visited ∧
      c.state.visited ≤ a.checkpoint.state.visited + limit := by
  obtain ⟨_, hv, hl, _⟩ := (validateCheckpointTransition_accepted_iff_canonical a limit c).mp hc
  unfold checkpointTransitionDelta at hl
  omega

/-- Incremental acceptance yields the full root certificate for the supplied state. -/
theorem validateCheckpointTransition_has_certificate {p limit : ℕ} {b : ParameterBox}
    {a : ValidatedRectangleCheckpoint p b} {c : RectangleCheckpoint}
    (hc : validateCheckpointTransition a limit c = .accepted) :
    ∃ cert : BudgetedPartitionCertificate p c.state.visited b, cert.result = c.state := by
  obtain ⟨hm, _, _, hs⟩ := (validateCheckpointTransition_accepted_iff_canonical a limit c).mp hc
  exact validateRectangleCheckpoint_has_certificate
    ((validateRectangleCheckpoint_accepted_iff _ _ _ _).mpr ⟨hm, le_rfl, hs⟩)

/-- Promote checked data without rerunning its already established prefix. -/
def advanceValidatedCheckpoint {p limit : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (c : RectangleCheckpoint)
    (hc : validateCheckpointTransition a limit c = .accepted) :
    ValidatedRectangleCheckpoint p b where
  checkpoint := c
  metadata := ((validateCheckpointTransition_accepted_iff_canonical a limit c).mp hc).1
  canonical := ((validateCheckpointTransition_accepted_iff_canonical a limit c).mp hc).2.2.2

/-- Revalidation limits are monotone. -/
theorem validateCheckpointTransition_mono_limit {p lo hi : ℕ} {b : ParameterBox}
    {a : ValidatedRectangleCheckpoint p b} {c : RectangleCheckpoint}
    (hl : lo ≤ hi) (hc : validateCheckpointTransition a lo c = .accepted) :
    validateCheckpointTransition a hi c = .accepted := by
  obtain ⟨hm, hv, hd, hs⟩ := (validateCheckpointTransition_accepted_iff_canonical a lo c).mp hc
  exact (validateCheckpointTransition_accepted_iff_canonical a hi c).mpr
    ⟨hm, hv, hd.trans hl, hs⟩

/-- Replaying a checkpoint against itself costs zero additional visits. -/
theorem validateCheckpointTransition_self {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (limit : ℕ) :
    validateCheckpointTransition a limit a.checkpoint = .accepted := by
  apply (validateCheckpointTransition_accepted_iff_canonical a limit a.checkpoint).mpr
  exact ⟨a.metadata, le_rfl, by simp [checkpointTransitionDelta], a.canonical⟩

/-- Context equality and full-state equality identify a raw checkpoint. -/
theorem rectangleCheckpoint_eq_of_context_state {p : ℕ} {b : ParameterBox}
    {a c : RectangleCheckpoint} (ha : a.MetadataValid p b) (hc : c.MetadataValid p b)
    (hs : a.state = c.state) : a = c := by
  cases a
  cases c
  simp_all [RectangleCheckpoint.MetadataValid]

/-- Equal visit counts allow no changes, even if a different queue covers the same root. -/
theorem validateCheckpointTransition_same_counter_iff {p limit : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (c : RectangleCheckpoint)
    (hv : c.state.visited = a.checkpoint.state.visited) :
    validateCheckpointTransition a limit c = .accepted ↔ c = a.checkpoint := by
  constructor
  · intro hc
    obtain ⟨hm, _, hs⟩ := (validateCheckpointTransition_accepted_iff a limit c).mp hc
    have hd : checkpointTransitionDelta a c = 0 := by simp [checkpointTransitionDelta, hv]
    rw [hd] at hs
    exact rectangleCheckpoint_eq_of_context_state hm.1 a.metadata hs
  · rintro rfl
    exact validateCheckpointTransition_self a limit

/-- A completed anchor is absorbing: no changed state or inflated counter can be accepted. -/
theorem validateCheckpointTransition_completed_iff {p limit : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (c : RectangleCheckpoint)
    (he : a.checkpoint.state.pending = []) :
    validateCheckpointTransition a limit c = .accepted ↔ c = a.checkpoint := by
  constructor
  · intro hc
    obtain ⟨hm, _, hs⟩ := (validateCheckpointTransition_accepted_iff a limit c).mp hc
    rw [runRectangleQueue_empty p _ he] at hs
    exact rectangleCheckpoint_eq_of_context_state hm.1 a.metadata hs
  · rintro rfl
    exact validateCheckpointTransition_self a limit

/-- Accepted increments telescope without charging repeated prefix visits. -/
theorem checkpointTransitionDelta_add {p l₁ l₂ : ℕ} {b : ParameterBox}
    {a : ValidatedRectangleCheckpoint p b} {c d : RectangleCheckpoint}
    (hc : validateCheckpointTransition a l₁ c = .accepted)
    (hd : validateCheckpointTransition (advanceValidatedCheckpoint a c hc) l₂ d = .accepted) :
    checkpointTransitionDelta a d = checkpointTransitionDelta a c +
      checkpointTransitionDelta (advanceValidatedCheckpoint a c hc) d := by
  have h1 := (validateCheckpointTransition_counter_bounds hc).1
  have h2 := (validateCheckpointTransition_counter_bounds hd).1
  change c.state.visited ≤ d.state.visited at h2
  simp only [checkpointTransitionDelta, advanceValidatedCheckpoint]
  omega

/-- Two accepted incremental transitions compose with the sum of their allowances. -/
theorem validateCheckpointTransition_trans {p l₁ l₂ : ℕ} {b : ParameterBox}
    {a : ValidatedRectangleCheckpoint p b} {c d : RectangleCheckpoint}
    (hc : validateCheckpointTransition a l₁ c = .accepted)
    (hd : validateCheckpointTransition (advanceValidatedCheckpoint a c hc) l₂ d = .accepted) :
    validateCheckpointTransition a (l₁ + l₂) d = .accepted := by
  obtain ⟨hm1, hv1, hl1, hs1⟩ := (validateCheckpointTransition_accepted_iff_canonical a l₁ c).mp hc
  obtain ⟨hm2, hv2, hl2, hs2⟩ :=
    (validateCheckpointTransition_accepted_iff_canonical (advanceValidatedCheckpoint a c hc) l₂ d).mp hd
  change c.state.visited ≤ d.state.visited at hv2
  exact (validateCheckpointTransition_accepted_iff_canonical a (l₁ + l₂) d).mpr
    ⟨hm2, hv1.trans hv2, by rw [checkpointTransitionDelta_add hc hd]; omega, hs2⟩

/-- Accepted successors preserve all existing sealed labels as a literal prefix. -/
theorem validateCheckpointTransition_sealed_prefix {p limit : ℕ} {b : ParameterBox}
    {a : ValidatedRectangleCheckpoint p b} {c : RectangleCheckpoint}
    (hc : validateCheckpointTransition a limit c = .accepted) :
    ∃ tail, c.state.sealed = a.checkpoint.state.sealed ++ tail := by
  have hs := ((validateCheckpointTransition_accepted_iff a limit c).mp hc).2.2
  rw [hs]
  exact runRectangleQueue_sealed_prefix p _ _

/-- Later resumption is exactly the canonical root run from the accepted actual counter. -/
theorem validateCheckpointTransition_restart {p limit : ℕ} {b : ParameterBox}
    {a : ValidatedRectangleCheckpoint p b} {c : RectangleCheckpoint}
    (hc : validateCheckpointTransition a limit c = .accepted) (extra : ℕ) :
    runRectangleQueue p extra c.state = budgetedDecompose p (c.state.visited + extra) b := by
  exact validateRectangleCheckpoint_restart (advanceValidatedCheckpoint a c hc).rootAccepted extra

/-- An authentic successor stores consumed visits, never the requested extra quota. -/
def exportCheckpointSuccessor {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (extra : ℕ) : RectangleCheckpoint :=
  ⟨1, p, b, runRectangleQueue p extra a.checkpoint.state⟩

/-- Every authentic successor passes using only its actual increment as replay quota. -/
theorem validateCheckpointTransition_successor {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (extra limit : ℕ)
    (hl : checkpointTransitionDelta a (exportCheckpointSuccessor a extra) ≤ limit) :
    validateCheckpointTransition a limit (exportCheckpointSuccessor a extra) = .accepted := by
  have hr := resumeValidatedCheckpoint_revalidates a.rootAccepted extra
  change validateRectangleCheckpoint p b (a.checkpoint.state.visited + extra)
    (exportCheckpointSuccessor a extra) = .accepted at hr
  obtain ⟨hm, _, hs⟩ := (validateRectangleCheckpoint_accepted_iff _ _ _ _).mp hr
  exact (validateCheckpointTransition_accepted_iff_canonical a limit _).mpr
    ⟨hm, (runRectangleQueue_visited_bounds p extra a.checkpoint.state).1, hl, hs⟩

/-- The consumed successor increment is bounded by the requested quota. -/
theorem exportCheckpointSuccessor_delta_le {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (extra : ℕ) :
    checkpointTransitionDelta a (exportCheckpointSuccessor a extra) ≤ extra := by
  have hv := (runRectangleQueue_visited_bounds p extra a.checkpoint.state).2
  simp only [checkpointTransitionDelta, exportCheckpointSuccessor]
  omega

/-- Requesting more work than remains does not force extra validation visits. -/
theorem validateCheckpointTransition_successor_at_actual_delta {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (extra : ℕ) :
    validateCheckpointTransition a
      (checkpointTransitionDelta a (exportCheckpointSuccessor a extra))
      (exportCheckpointSuccessor a extra) = .accepted := by
  exact validateCheckpointTransition_successor a extra _ le_rfl

/-- Local no-op consistency with a raw unvalidated anchor is not provenance.
The metadata-valid forged singleton label passes a zero-step equality but fails
root validation. The public transition API cannot be given this raw anchor. -/
theorem unvalidatedAnchor_local_consistency_not_provenance :
    let b : ParameterBox := ⟨1, 1, 0, 0⟩
    let c : RectangleCheckpoint := ⟨1, 2, b, ⟨[], [⟨b, some (99, 99)⟩], 1⟩⟩
    c.MetadataValid 2 b ∧ c.state = runRectangleQueue 2 0 c.state ∧
      validateRectangleCheckpoint 2 b 1 c = .rejected := by
  decide +kernel

end KomorebiPadic
