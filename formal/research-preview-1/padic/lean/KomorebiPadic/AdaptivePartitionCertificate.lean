import KomorebiPadic.AdaptiveRectangles

/-!
# Exact partition certificates and restartable refinement

Certificates separate geometric coverage, checked plateau labels, and the
existing per-point compiler envelope. They do not identify labels with all
internal edge data, and do not assume monotonic adaptive work.
-/
namespace KomorebiPadic

/-- Distinct positions in the returned list cannot cover the same point. -/
theorem adaptiveDecompose_pairwise_disjoint (p fuel : ℕ) {b : ParameterBox}
    (hb : b.Valid) :
    (adaptiveDecompose p fuel b).Pairwise
      (fun x y => ∀ r h, ¬ (x.box.Contains r h ∧ y.box.Contains r h)) := by
  induction fuel generalizing b with
  | zero => simp [adaptiveDecompose]
  | succ n ih =>
    simp only [adaptiveDecompose]
    split
    · simp
    · rename_i hc
      have hs := parameterBox_span_pos_of_failed_check p hb hc
      have hv := parameterBox_split_valid_and_decreases hb hs
      apply List.pairwise_append.mpr
      refine ⟨ih hv.1, ih hv.2.1, ?_⟩
      intro x hx y hy r h hboth
      have hxl := (adaptiveDecompose_leaf_subset p n hv.1 hx).2 r h hboth.1
      have hyr := (adaptiveDecompose_leaf_subset p n hv.2.1 hy).2 r h hboth.2
      exact (parameterBox_split_partition hb hs r h).2 ⟨hxl, hyr⟩

/-- Every partial leaf inherits the adverse-corner work envelope of the parent. -/
theorem adaptiveDecompose_uniform_envelope {p fuel : ℕ} (hp : p.Prime)
    {b : ParameterBox} (hb : b.Valid) {l : PlateauLeaf}
    (hl : l ∈ adaptiveDecompose p fuel b) {r h : ℕ} (hx : l.box.Contains r h) :
    maximumLayerCompilerTotalTests p r h ≤
      maximumLayerCompilerParameterEnvelopeBound p b.rhi b.hlo := by
  have hy := (adaptiveDecompose_leaf_subset p fuel hb hl).2 r h hx
  exact maximumLayerCompilerTotalTests_le_parameterRegionEnvelope hp
    (parameterBox_precision_pos hb hy) hy.2.1 hy.2.2.1

/-- Resume only unresolved leaves; previously sealed leaves are retained literally. -/
def refinePlateauLeaves (p extra : ℕ) (ls : List PlateauLeaf) : List PlateauLeaf :=
  ls.flatMap fun l => if l.label.isSome then [l] else adaptiveDecompose p extra l.box

/-- Exact restart law, including list order and labels, not merely set equality. -/
theorem refinePlateauLeaves_adaptiveDecompose (p fuel extra : ℕ) (b : ParameterBox) :
    refinePlateauLeaves p extra (adaptiveDecompose p fuel b) =
      adaptiveDecompose p (fuel + extra) b := by
  induction fuel generalizing b with
  | zero => simp [refinePlateauLeaves, adaptiveDecompose, unresolvedPlateauLeaf]
  | succ n ih =>
    rw [Nat.succ_add]
    simp only [adaptiveDecompose]
    split
    · simp [refinePlateauLeaves, sealedPlateauLeaf]
    · simp only [refinePlateauLeaves, List.flatMap_append]
      exact congrArg₂ (· ++ ·) (ih b.split.1) (ih b.split.2)

/-- Resuming a completed partial result preserves exact coverage. -/
theorem refinePlateauLeaves_exact_coverage (p fuel extra : ℕ) {b : ParameterBox}
    (hb : b.Valid) (r h : ℕ) :
    leafCoverCount (refinePlateauLeaves p extra (adaptiveDecompose p fuel b)) r h =
      if b.Contains r h then 1 else 0 := by
  rw [refinePlateauLeaves_adaptiveDecompose]
  exact adaptiveDecompose_exact_coverage p (fuel + extra) hb r h

/-- Combined depth suffices to seal every leaf after a restart. -/
theorem refinePlateauLeaves_complete (p fuel extra : ℕ) {b : ParameterBox}
    (hb : b.Valid) (hf : b.span < fuel + extra) {l : PlateauLeaf}
    (hl : l ∈ refinePlateauLeaves p extra (adaptiveDecompose p fuel b)) :
    l.label.isSome = true := by
  rw [refinePlateauLeaves_adaptiveDecompose] at hl
  exact adaptiveDecompose_complete p (fuel + extra) hb hf hl

/-- A checked entry point rejects composite bases, empty boxes, and precision zero.
A successful partial output is `some leaves`; unresolved status is inside each leaf. -/
def checkedAdaptiveDecompose (p fuel : ℕ) (b : ParameterBox) : Option (List PlateauLeaf) :=
  if p.Prime ∧ b.Valid then some (adaptiveDecompose p fuel b) else none

theorem checkedAdaptiveDecompose_eq_some_iff (p fuel : ℕ) (b : ParameterBox)
    (ls : List PlateauLeaf) :
    checkedAdaptiveDecompose p fuel b = some ls ↔
      p.Prime ∧ b.Valid ∧ ls = adaptiveDecompose p fuel b := by
  simp only [checkedAdaptiveDecompose]
  split <;> simp_all [eq_comm]

theorem checkedAdaptiveDecompose_eq_none_iff (p fuel : ℕ) (b : ParameterBox) :
    checkedAdaptiveDecompose p fuel b = none ↔ ¬ (p.Prime ∧ b.Valid) := by
  simp [checkedAdaptiveDecompose]

/-- Executable completion flag; it never treats fuel exhaustion as a plateau. -/
def partitionFullySealed (ls : List PlateauLeaf) : Bool :=
  ls.all fun l => l.label.isSome

theorem partitionFullySealed_eq_true_iff (ls : List PlateauLeaf) :
    partitionFullySealed ls = true ↔ ∀ l ∈ ls, l.label.isSome = true := by
  simp [partitionFullySealed]

theorem completeDecompose_fullySealed (p : ℕ) {b : ParameterBox} (hb : b.Valid) :
    partitionFullySealed (completeDecompose p b) = true := by
  exact (partitionFullySealed_eq_true_iff _).mpr fun _ hl => completeDecompose_all_sealed p hb hl

/-- On a fully sealed partial output, every original point has a certified exact label. -/
theorem adaptiveDecompose_fullySealed_pointwise {p fuel : ℕ} (hp : p.Prime)
    {b : ParameterBox} (hb : b.Valid)
    (hc : partitionFullySealed (adaptiveDecompose p fuel b) = true)
    {r h : ℕ} (hx : b.Contains r h) :
    ∃ l ∈ adaptiveDecompose p fuel b, ∃ value, l.box.Contains r h ∧
      l.label = some value ∧
      (maximumLayerCompiler p r h).layer = value.1 ∧
      (maximumLayerCompiler p r h).quotient = value.2 := by
  obtain ⟨l, hl, hxl⟩ := adaptiveDecompose_covers p fuel hb hx
  have hs := (partitionFullySealed_eq_true_iff _).mp hc l hl
  cases heq : l.label with
  | none => simp [heq] at hs
  | some value =>
    exact ⟨l, hl, value, hxl, heq, (adaptiveDecompose_sound hp fuel hb hl).2 value heq r h hxl⟩

structure AdaptivePartitionCertificate (p fuel : ℕ) (b : ParameterBox) where
  base_prime : p.Prime
  domain : MaximumLayerCompilerRectangleCertificate p b.rlo b.rhi b.hlo b.hhi
  leaves : List PlateauLeaf
  leaves_eq : leaves = adaptiveDecompose p fuel b
  coverage : ∀ r h, leafCoverCount leaves r h = if b.Contains r h then 1 else 0
  leaf_subset : ∀ l ∈ leaves, l.box.Valid ∧ ∀ r h, l.box.Contains r h → b.Contains r h
  disjoint : leaves.Pairwise (fun x y => ∀ r h, ¬ (x.box.Contains r h ∧ y.box.Contains r h))
  labels_sound : ∀ l ∈ leaves, l.Sound p
  uniform_envelope : ∀ l ∈ leaves, ∀ r h, l.box.Contains r h →
    maximumLayerCompilerTotalTests p r h ≤
      maximumLayerCompilerParameterEnvelopeBound p b.rhi b.hlo
  enough_fuel : b.span < fuel → partitionFullySealed leaves = true

/-- The proof fields are erased for evaluation. Existing compiler counters are not altered. -/
def adaptivePartitionCertificate (p fuel : ℕ) (b : ParameterBox)
    (hp : p.Prime) (hb : b.Valid) : AdaptivePartitionCertificate p fuel b where
  base_prime := hp
  domain := maximumLayerCompilerRectangleCertificate p b.rlo b.rhi b.hlo b.hhi hp
    hb.1 hb.2.1 hb.2.2
  leaves := adaptiveDecompose p fuel b
  leaves_eq := rfl
  coverage := adaptiveDecompose_exact_coverage p fuel hb
  leaf_subset := fun _ hl => adaptiveDecompose_leaf_subset p fuel hb hl
  disjoint := adaptiveDecompose_pairwise_disjoint p fuel hb
  labels_sound := fun _ hl => adaptiveDecompose_sound hp fuel hb hl
  uniform_envelope := fun _ hl _ _ hx => adaptiveDecompose_uniform_envelope hp hb hl hx
  enough_fuel := fun hf => (partitionFullySealed_eq_true_iff _).mpr
    fun _ hl => adaptiveDecompose_complete p fuel hb hf hl

/-- Sealed output labels describe the whole terminal target interval. -/
theorem adaptiveDecompose_sealed_targets_iff {p fuel : ℕ} (hp : p.Prime)
    {b : ParameterBox} (hb : b.Valid) {l : PlateauLeaf}
    (hl : l ∈ adaptiveDecompose p fuel b) {value : ℕ × ℕ}
    (hv : l.label = some value) {r h t : ℕ} (hx : l.box.Contains r h) :
    IsTarget (binomialPadicEdgeSystem p r h hp.one_lt) (stableQuotient p r h) t ↔
      1 ≤ t ∧ t ≤ value.1 := by
  have hs := adaptiveDecompose_sound hp fuel hb hl
  have hr := parameterBox_precision_pos hs.1 hx
  have hm := (hs.2 value hv r h hx).1
  change finalFiberBoundaryLayer p r h = value.1 at hm
  rw [finalFiberBoundaryLayer_eq_exactMaximumLayer hp hr] at hm
  rw [isTarget_iff_le_exactMaximumLayer hp hr, hm]

/-- Depth fuel controls the possible output size, even before domain validation. -/
theorem adaptiveDecompose_length_le (p fuel : ℕ) (b : ParameterBox) :
    (adaptiveDecompose p fuel b).length ≤ 2 ^ fuel := by
  induction fuel generalizing b with
  | zero => simp [adaptiveDecompose]
  | succ n ih =>
    simp only [adaptiveDecompose]
    split
    · simp only [List.length_singleton]
      exact Nat.one_le_pow _ _ (by decide)
    · rw [List.length_append, Nat.pow_succ]
      have h1 := ih b.split.1
      have h2 := ih b.split.2
      omega

/-- Any accepted public result comes with the complete dependent certificate. -/
theorem checkedAdaptiveDecompose_has_certificate (p fuel : ℕ) (b : ParameterBox)
    (ls : List PlateauLeaf) (hs : checkedAdaptiveDecompose p fuel b = some ls) :
    ∃ c : AdaptivePartitionCertificate p fuel b, c.leaves = ls := by
  obtain ⟨hp, hb, rfl⟩ := (checkedAdaptiveDecompose_eq_some_iff p fuel b ls).mp hs
  exact ⟨adaptivePartitionCertificate p fuel b hp hb, rfl⟩

end KomorebiPadic
