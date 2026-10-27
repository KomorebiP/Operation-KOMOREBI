import KomorebiPadic.BudgetedRectangles

/-!
# Sound queue checkpoints and once-only partial coverage

Every pending box remains visible as an unresolved leaf. Labels occur only after
successful corner checks; completion is proved separately from quota exhaustion.
-/
namespace KomorebiPadic

/-- Processing one node preserves the occurrence-counting coverage function. -/
theorem rectangleQueueStep_coverCount (p : ℕ) {s : RectangleQueueState}
    (hv : s.PendingValid) (r h : ℕ) :
    leafCoverCount (rectangleQueueStep p s).leaves r h = leafCoverCount s.leaves r h := by
  rcases s with ⟨ps, ls, v⟩
  cases ps with
  | nil => rfl
  | cons b bs =>
    have hb := hv b (by simp)
    simp only [rectangleQueueStep]
    split
    · simp [RectangleQueueState.leaves, leafCoverCount_append, leafCoverCount,
        sealedPlateauLeaf, unresolvedPlateauLeaf]
    · rename_i hc
      have hs := parameterBox_span_pos_of_failed_check p hb hc
      have hp := parameterBox_split_partition hb hs r h
      simp only [RectangleQueueState.leaves, List.map_cons, leafCoverCount_append,
        leafCoverCount, unresolvedPlateauLeaf]
      by_cases h1 : b.split.1.Contains r h <;>
        by_cases h2 : b.split.2.Contains r h <;>
        by_cases h0 : b.Contains r h <;> simp_all

structure RectangleQueueInvariant (p : ℕ) (root : ParameterBox)
    (s : RectangleQueueState) : Prop where
  pending : ∀ b ∈ s.pending, b.Valid ∧ ∀ r h, b.Contains r h → root.Contains r h
  sealed : ∀ l ∈ s.sealed, l.Sound p ∧ l.label.isSome = true ∧
    ∀ r h, l.box.Contains r h → root.Contains r h
  coverage : ∀ r h, leafCoverCount s.leaves r h = if root.Contains r h then 1 else 0

theorem initialRectangleQueue_invariant (p : ℕ) {b : ParameterBox}
    (hb : b.Valid) : RectangleQueueInvariant p b (initialRectangleQueue b) := by
  constructor
  · intro c hc
    simp only [initialRectangleQueue, List.mem_singleton] at hc
    subst c
    exact ⟨hb, fun _ _ hx => hx⟩
  · intro l hl
    simp [initialRectangleQueue] at hl
  · intro r h
    simp [RectangleQueueState.leaves, initialRectangleQueue, leafCoverCount,
      unresolvedPlateauLeaf]

/-- All geometric and semantic checkpoint invariants survive one visit. -/
theorem rectangleQueueStep_invariant {p : ℕ} (hp : p.Prime)
    {root : ParameterBox} {s : RectangleQueueState}
    (hi : RectangleQueueInvariant p root s) :
    RectangleQueueInvariant p root (rectangleQueueStep p s) := by
  have hv : s.PendingValid := fun b hb => (hi.pending b hb).1
  have hcover := rectangleQueueStep_coverCount p hv
  rcases s with ⟨ps, ls, v⟩
  cases ps with
  | nil => exact hi
  | cons b bs =>
    have hb := hi.pending b (by simp)
    have htail : ∀ c ∈ bs, c.Valid ∧ ∀ r h, c.Contains r h → root.Contains r h :=
      fun c hc => hi.pending c (by simp [hc])
    by_cases hc : rectangleLayerPlateauCheck p b.rlo b.rhi b.hlo b.hhi = true
    · simp only [rectangleQueueStep, hc, ↓reduceIte] at hcover ⊢
      constructor
      · exact htail
      · intro l hl
        simp only [List.mem_append, List.mem_singleton] at hl
        rcases hl with hl | rfl
        · exact hi.sealed l hl
        · exact ⟨sealedPlateauLeaf_sound hp hb.1 hc, rfl, hb.2⟩
      · intro r h
        exact (hcover r h).trans (hi.coverage r h)
    · have hs := parameterBox_span_pos_of_failed_check p hb.1 hc
      have hvalid := parameterBox_split_valid_and_decreases hb.1 hs
      simp only [rectangleQueueStep, hc] at hcover ⊢
      constructor
      · intro c hm
        change c ∈ b.split.1 :: b.split.2 :: bs at hm
        simp only [List.mem_cons] at hm
        rcases hm with rfl | rfl | hm
        · exact ⟨hvalid.1, fun r h hx =>
            hb.2 r h ((parameterBox_split_subset hb.1 hs).1 hx)⟩
        · exact ⟨hvalid.2.1, fun r h hx =>
            hb.2 r h ((parameterBox_split_subset hb.1 hs).2 hx)⟩
        · exact htail c hm
      · exact hi.sealed
      · intro r h
        exact (hcover r h).trans (hi.coverage r h)

theorem runRectangleQueue_invariant {p : ℕ} (hp : p.Prime) (n : ℕ)
    {root : ParameterBox} {s : RectangleQueueState}
    (hi : RectangleQueueInvariant p root s) :
    RectangleQueueInvariant p root (runRectangleQueue p n s) := by
  induction n generalizing s with
  | zero => exact hi
  | succ n ih =>
    by_cases he : s.pending = []
    · simpa [runRectangleQueue_empty p _ he] using hi
    · simp only [runRectangleQueue, he, ↓reduceIte]
      exact ih (rectangleQueueStep_invariant hp hi)

theorem budgetedDecompose_invariant {p : ℕ} (hp : p.Prime) (n : ℕ)
    {b : ParameterBox} (hb : b.Valid) :
    RectangleQueueInvariant p b (budgetedDecompose p n b) := by
  exact runRectangleQueue_invariant hp n (initialRectangleQueue_invariant p hb)

/-- Exact coverage counts list positions, including all pending rectangles. -/
theorem budgetedDecompose_exact_coverage {p : ℕ} (hp : p.Prime) (n : ℕ)
    {b : ParameterBox} (hb : b.Valid) (r h : ℕ) :
    leafCoverCount (budgetedDecompose p n b).leaves r h =
      if b.Contains r h then 1 else 0 := by
  exact (budgetedDecompose_invariant hp n hb).coverage r h

/-- Occurrence-counting at most once implies pairwise disjointness. -/
theorem leafCoverCount_le_one_pairwise (ls : List PlateauLeaf)
    (hc : ∀ r h, leafCoverCount ls r h ≤ 1) :
    ls.Pairwise (fun x y => ∀ r h, ¬ (x.box.Contains r h ∧ y.box.Contains r h)) := by
  induction ls with
  | nil => simp
  | cons l ls ih =>
    apply List.pairwise_cons.mpr
    constructor
    · intro k hk r h hx
      have hp := (leafCoverCount_pos_iff ls r h).mpr ⟨k, hk, hx.2⟩
      have hh := hc r h
      simp only [leafCoverCount, hx.1, ↓reduceIte] at hh
      omega
    · apply ih
      intro r h
      have hh := hc r h
      simp only [leafCoverCount] at hh
      omega

theorem budgetedDecompose_pairwise_disjoint {p : ℕ} (hp : p.Prime) (n : ℕ)
    {b : ParameterBox} (hb : b.Valid) :
    (budgetedDecompose p n b).leaves.Pairwise
      (fun x y => ∀ r h, ¬ (x.box.Contains r h ∧ y.box.Contains r h)) := by
  apply leafCoverCount_le_one_pairwise
  intro r h
  rw [budgetedDecompose_exact_coverage hp n hb]
  split <;> omega

/-- Each checkpoint leaf is valid and included; sealed labels are uniformly true. -/
theorem rectangleQueueInvariant_leaf_sound_subset {p : ℕ} {root : ParameterBox}
    {s : RectangleQueueState} (hi : RectangleQueueInvariant p root s)
    {l : PlateauLeaf} (hl : l ∈ s.leaves) :
    l.Sound p ∧ ∀ r h, l.box.Contains r h → root.Contains r h := by
  rcases List.mem_append.mp hl with hl | hl
  · have hh := hi.sealed l hl
    exact ⟨hh.1, hh.2.2⟩
  · obtain ⟨b, hb, rfl⟩ := List.mem_map.mp hl
    have hh := hi.pending b hb
    refine ⟨⟨hh.1, ?_⟩, hh.2⟩
    intro value heq
    cases heq

/-- Every pointwise compiler call in a checkpoint retains the parent envelope. -/
theorem budgetedDecompose_uniform_envelope {p n : ℕ} (hp : p.Prime)
    {b : ParameterBox} (hb : b.Valid) {l : PlateauLeaf}
    (hl : l ∈ (budgetedDecompose p n b).leaves) {r h : ℕ}
    (hx : l.box.Contains r h) :
    maximumLayerCompilerTotalTests p r h ≤
      maximumLayerCompilerParameterEnvelopeBound p b.rhi b.hlo := by
  have hy := (rectangleQueueInvariant_leaf_sound_subset
    (budgetedDecompose_invariant hp n hb) hl).2 r h hx
  exact maximumLayerCompilerTotalTests_le_parameterRegionEnvelope hp
    (parameterBox_precision_pos hb hy) hy.2.1 hy.2.2.1

/-- For a sound state, every label is resolved exactly when the queue is empty. -/
theorem rectangleQueueInvariant_fullySealed_iff {p : ℕ} {root : ParameterBox}
    {s : RectangleQueueState} (hi : RectangleQueueInvariant p root s) :
    partitionFullySealed s.leaves = true ↔ s.pending = [] := by
  constructor
  · intro hall
    by_contra hn
    obtain ⟨b, bs, heq⟩ := List.exists_cons_of_ne_nil hn
    have hm : unresolvedPlateauLeaf b ∈ s.leaves := by
      simp [RectangleQueueState.leaves, heq]
    have hh := (partitionFullySealed_eq_true_iff _).mp hall _ hm
    cases hh
  · intro he
    apply (partitionFullySealed_eq_true_iff _).mpr
    intro l hl
    simp only [RectangleQueueState.leaves, he, List.map_nil, List.append_nil] at hl
    exact (hi.sealed l hl).2.1

/-- A sealed checkpoint label describes its entire terminal target interval. -/
theorem budgetedDecompose_sealed_targets_iff {p n : ℕ} (hp : p.Prime)
    {b : ParameterBox} (hb : b.Valid) {l : PlateauLeaf}
    (hl : l ∈ (budgetedDecompose p n b).leaves) {value : ℕ × ℕ}
    (hv : l.label = some value) {r h t : ℕ} (hx : l.box.Contains r h) :
    IsTarget (binomialPadicEdgeSystem p r h hp.one_lt) (stableQuotient p r h) t ↔
      1 ≤ t ∧ t ≤ value.1 := by
  have hs := (rectangleQueueInvariant_leaf_sound_subset
    (budgetedDecompose_invariant hp n hb) hl).1
  have hr := parameterBox_precision_pos hs.1 hx
  have hm := (hs.2 value hv r h hx).1
  change finalFiberBoundaryLayer p r h = value.1 at hm
  rw [finalFiberBoundaryLayer_eq_exactMaximumLayer hp hr] at hm
  rw [isTarget_iff_le_exactMaximumLayer hp hr, hm]

/-- Completed visits are exactly 2*number-of-leaves minus one. -/
theorem budgetedDecompose_complete_node_count (p n : ℕ) (b : ParameterBox)
    (he : (budgetedDecompose p n b).pending = []) :
    (budgetedDecompose p n b).visited = 2 * (budgetedDecompose p n b).leaves.length - 1 := by
  have hh := budgetedDecompose_node_identity p n b
  simp only [RectangleQueueState.leaves, he, List.map_nil, List.append_nil,
    List.length_nil] at hh ⊢
  omega

end KomorebiPadic
