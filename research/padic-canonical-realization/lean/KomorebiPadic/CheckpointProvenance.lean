import KomorebiPadic.BudgetedPartitionCertificate

/-!
# Replay-validated checkpoints

Validation binds an externally supplied state to an independently supplied base
and root. Replay is limited by a caller-selected visit allowance. Acceptance
certifies canonical mathematical provenance, not authorship or wall-clock history.
-/
namespace KomorebiPadic

/-- Version 1 fixes the split rule, traversal order, and inherited pointwise compiler. -/
structure RectangleCheckpoint where
  version : ℕ
  base : ℕ
  root : ParameterBox
  state : RectangleQueueState
  deriving DecidableEq, Repr

inductive CheckpointVerdict where
  | accepted
  | rejected
  | deferred
  deriving DecidableEq, Repr

/-- A completed or partial run can be recovered from its actual visit counter. -/
theorem budgetedDecompose_at_visited (p n : ℕ) {b : ParameterBox} (hb : b.Valid) :
    budgetedDecompose p (budgetedDecompose p n b).visited b = budgetedDecompose p n b := by
  by_cases he : (budgetedDecompose p n b).pending = []
  · have hv := budgetedDecompose_completed_visited p n hb he
    have he' := (budgetedDecompose_complete_iff p
      (budgetedDecompose p n b).visited hb).mpr (by omega)
    have hv' := budgetedDecompose_completed_visited p
      (budgetedDecompose p n b).visited hb he'
    have hl := budgetedDecompose_completed_eq_complete p n hb he
    have hl' := budgetedDecompose_completed_eq_complete p
      (budgetedDecompose p n b).visited hb he'
    simp only [RectangleQueueState.leaves, he, he', List.map_nil, List.append_nil] at hl hl'
    have hs : (budgetedDecompose p (budgetedDecompose p n b).visited b).sealed =
        (budgetedDecompose p n b).sealed := hl'.trans hl.symm
    cases h1 : budgetedDecompose p (budgetedDecompose p n b).visited b
    cases h2 : budgetedDecompose p n b
    simp_all
  · have hv := runRectangleQueue_exhausted p n (initialRectangleQueue b) he
    change (budgetedDecompose p n b).visited = 0 + n at hv
    simpa only [Nat.zero_add] using congrArg (fun v => budgetedDecompose p v b) hv

/-- Metadata is checked against caller-supplied context, not trusted file fields. -/
def RectangleCheckpoint.MetadataValid (p : ℕ) (b : ParameterBox)
    (c : RectangleCheckpoint) : Prop :=
  c.version = 1 ∧ c.base = p ∧ c.root = b ∧ p.Prime ∧ b.Valid ∧
    c.state.visited ≤ b.nodeCapacity

instance (p : ℕ) (b : ParameterBox) (c : RectangleCheckpoint) :
    Decidable (c.MetadataValid p b) :=
  inferInstanceAs (Decidable (c.version = 1 ∧ c.base = p ∧ c.root = b ∧
    p.Prime ∧ b.Valid ∧ c.state.visited ≤ b.nodeCapacity))

/-- Canonical provenance includes the exact ordered pending and sealed lists. -/
def RectangleCheckpoint.Canonical (p : ℕ) (b : ParameterBox)
    (c : RectangleCheckpoint) : Prop :=
  c.state = budgetedDecompose p c.state.visited b

instance (p : ℕ) (b : ParameterBox) (c : RectangleCheckpoint) :
    Decidable (c.Canonical p b) :=
  inferInstanceAs (Decidable (c.state = budgetedDecompose p c.state.visited b))

/-- No canonical replay is performed in the deferred or metadata-rejected branches. -/
def validateRectangleCheckpoint (p : ℕ) (b : ParameterBox) (replayLimit : ℕ)
    (c : RectangleCheckpoint) : CheckpointVerdict :=
  if c.MetadataValid p b then
    if c.state.visited ≤ replayLimit then
      if c.Canonical p b then .accepted else .rejected
    else .deferred
  else .rejected

/-- Exact acceptance specification, including the counter-provenance test. -/
theorem validateRectangleCheckpoint_accepted_iff (p : ℕ) (b : ParameterBox)
    (limit : ℕ) (c : RectangleCheckpoint) :
    validateRectangleCheckpoint p b limit c = .accepted ↔
      c.MetadataValid p b ∧ c.state.visited ≤ limit ∧ c.Canonical p b := by
  simp only [validateRectangleCheckpoint]
  split <;> simp_all
  split <;> simp_all

/-- Resource deferral is distinct from invalidity. -/
theorem validateRectangleCheckpoint_deferred_iff (p : ℕ) (b : ParameterBox)
    (limit : ℕ) (c : RectangleCheckpoint) :
    validateRectangleCheckpoint p b limit c = .deferred ↔
      c.MetadataValid p b ∧ limit < c.state.visited := by
  simp only [validateRectangleCheckpoint]
  split <;> simp_all
  split <;> simp_all

/-- Increasing the validation allowance cannot invalidate an accepted checkpoint. -/
theorem validateRectangleCheckpoint_accepted_mono_limit {p lo hi : ℕ}
    {b : ParameterBox} {c : RectangleCheckpoint} (hl : lo ≤ hi)
    (hc : validateRectangleCheckpoint p b lo c = .accepted) :
    validateRectangleCheckpoint p b hi c = .accepted := by
  obtain ⟨hm, hv, hs⟩ := (validateRectangleCheckpoint_accepted_iff p b lo c).mp hc
  exact (validateRectangleCheckpoint_accepted_iff p b hi c).mpr ⟨hm, hv.trans hl, hs⟩

/-- Export the exact state; requested fuel is not mislabeled as consumed visits. -/
def exportRectangleCheckpoint (p budget : ℕ) (b : ParameterBox) : RectangleCheckpoint :=
  ⟨1, p, b, budgetedDecompose p budget b⟩

/-- Every authentic export is accepted once its actual visits fit the allowance. -/
theorem validateRectangleCheckpoint_export {p budget limit : ℕ}
    {b : ParameterBox} (hp : p.Prime) (hb : b.Valid)
    (hl : (budgetedDecompose p budget b).visited ≤ limit) :
    validateRectangleCheckpoint p b limit (exportRectangleCheckpoint p budget b) = .accepted := by
  apply (validateRectangleCheckpoint_accepted_iff _ _ _ _).mpr
  refine ⟨⟨rfl, rfl, rfl, hp, hb, budgetedDecompose_visited_le_capacity p budget hb⟩, hl, ?_⟩
  exact (budgetedDecompose_at_visited p budget hb).symm

/-- Accepted external state has all inherited semantic and geometric invariants. -/
theorem validateRectangleCheckpoint_invariant {p limit : ℕ} {b : ParameterBox}
    {c : RectangleCheckpoint} (hc : validateRectangleCheckpoint p b limit c = .accepted) :
    RectangleQueueInvariant p b c.state := by
  obtain ⟨hm, _, hs⟩ := (validateRectangleCheckpoint_accepted_iff _ _ _ _).mp hc
  rw [RectangleCheckpoint.Canonical] at hs
  rw [hs]
  exact budgetedDecompose_invariant hm.2.2.2.1 _ hm.2.2.2.2.1

/-- A validated state resumes from its actual visit count, not the file's ancestry story. -/
theorem validateRectangleCheckpoint_restart {p limit : ℕ} {b : ParameterBox}
    {c : RectangleCheckpoint} (hc : validateRectangleCheckpoint p b limit c = .accepted)
    (extra : ℕ) :
    runRectangleQueue p extra c.state = budgetedDecompose p (c.state.visited + extra) b := by
  have hs := ((validateRectangleCheckpoint_accepted_iff _ _ _ _).mp hc).2.2
  change c.state = budgetedDecompose p c.state.visited b at hs
  conv_lhs => rw [hs]
  exact runRectangleQueue_add p c.state.visited extra (initialRectangleQueue b)

/-- Acceptance exposes the full Block16 certificate for the supplied state. -/
theorem validateRectangleCheckpoint_has_certificate {p limit : ℕ} {b : ParameterBox}
    {c : RectangleCheckpoint} (hc : validateRectangleCheckpoint p b limit c = .accepted) :
    ∃ cert : BudgetedPartitionCertificate p c.state.visited b, cert.result = c.state := by
  obtain ⟨hm, _, hs⟩ := (validateRectangleCheckpoint_accepted_iff _ _ _ _).mp hc
  exact ⟨budgetedPartitionCertificate p c.state.visited b hm.2.2.2.1 hm.2.2.2.2.1, hs.symm⟩

/-- Resume only a checkpoint accompanied by successful validation evidence. -/
def resumeValidatedCheckpoint (p : ℕ) (b : ParameterBox) (limit extra : ℕ)
    (c : RectangleCheckpoint) (_hc : validateRectangleCheckpoint p b limit c = .accepted) :
    RectangleCheckpoint := ⟨1, p, b, runRectangleQueue p extra c.state⟩

/-- The resumed state revalidates without changing base, root, or sealed labels. -/
theorem resumeValidatedCheckpoint_revalidates {p limit : ℕ} {b : ParameterBox}
    {c : RectangleCheckpoint} (hc : validateRectangleCheckpoint p b limit c = .accepted)
    (extra : ℕ) :
    validateRectangleCheckpoint p b (c.state.visited + extra)
      (resumeValidatedCheckpoint p b limit extra c hc) = .accepted := by
  have hm := ((validateRectangleCheckpoint_accepted_iff _ _ _ _).mp hc).1
  have he := validateRectangleCheckpoint_restart hc extra
  have hx : resumeValidatedCheckpoint p b limit extra c hc =
      exportRectangleCheckpoint p (c.state.visited + extra) b := by
    unfold resumeValidatedCheckpoint exportRectangleCheckpoint
    rw [he]
  rw [hx]
  exact validateRectangleCheckpoint_export hm.2.2.2.1 hm.2.2.2.2.1
    (budgetedDecompose_visited_le _ _ _)

/-- This acceptance criterion explicitly includes equality of the expected context. -/
theorem validateRectangleCheckpoint_context {p limit : ℕ} {b : ParameterBox}
    {c : RectangleCheckpoint} (hc : validateRectangleCheckpoint p b limit c = .accepted) :
    c.version = 1 ∧ c.base = p ∧ c.root = b ∧ p.Prime ∧ b.Valid := by
  have hm := ((validateRectangleCheckpoint_accepted_iff _ _ _ _).mp hc).1
  exact ⟨hm.1, hm.2.1, hm.2.2.1, hm.2.2.2.1, hm.2.2.2.2.1⟩

end KomorebiPadic
