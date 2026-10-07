import KomorebiPadic.ParameterBox

/-!
# Certified adaptive parameter partitions

Depth fuel zero emits an unresolved leaf without evaluating the corner test.
Positive fuel tests the corners, seals on success, and otherwise bisects.
Coverage and disjointness include unresolved leaves. Completeness is a separate
result with an explicit sufficient fuel bound.
-/
namespace KomorebiPadic

structure PlateauLeaf where
  box : ParameterBox
  label : Option (ℕ × ℕ)
  deriving DecidableEq, Repr

/-- A positive label contains (maximum layer, stable quotient). -/
def sealedPlateauLeaf (p : ℕ) (b : ParameterBox) : PlateauLeaf :=
  let result := maximumLayerCompiler p b.rlo b.hhi
  ⟨b, some (result.layer, result.quotient)⟩

def unresolvedPlateauLeaf (b : ParameterBox) : PlateauLeaf := ⟨b, none⟩

/-- Total structural recursion. Fuel limits depth, not a global number of nodes. -/
def adaptiveDecompose (p : ℕ) : ℕ → ParameterBox → List PlateauLeaf
  | 0, b => [unresolvedPlateauLeaf b]
  | n + 1, b =>
    if rectangleLayerPlateauCheck p b.rlo b.rhi b.hlo b.hhi then
      [sealedPlateauLeaf p b]
    else
      adaptiveDecompose p n b.split.1 ++ adaptiveDecompose p n b.split.2

/-- Truthful label semantics; an unresolved leaf asserts no constancy. -/
def PlateauLeaf.Sound (p : ℕ) (l : PlateauLeaf) : Prop :=
  l.box.Valid ∧ ∀ value, l.label = some value → ∀ r h, l.box.Contains r h →
    (maximumLayerCompiler p r h).layer = value.1 ∧
    (maximumLayerCompiler p r h).quotient = value.2

/-- Coverage counts occurrences, so duplicate leaves are detected as overlaps. -/
def leafCoverCount : List PlateauLeaf → ℕ → ℕ → ℕ
  | [], _, _ => 0
  | l :: ls, r, h => (if l.box.Contains r h then 1 else 0) + leafCoverCount ls r h

theorem leafCoverCount_append (xs ys : List PlateauLeaf) (r h : ℕ) :
    leafCoverCount (xs ++ ys) r h = leafCoverCount xs r h + leafCoverCount ys r h := by
  induction xs with
  | nil => simp [leafCoverCount]
  | cons x xs ih => simp [leafCoverCount, ih, Nat.add_assoc]

theorem sealedPlateauLeaf_sound {p : ℕ} (hp : p.Prime) {b : ParameterBox}
    (hb : b.Valid)
    (hc : rectangleLayerPlateauCheck p b.rlo b.rhi b.hlo b.hhi = true) :
    (sealedPlateauLeaf p b).Sound p := by
  refine ⟨hb, ?_⟩
  intro value heq r h hx
  have hv : ((maximumLayerCompiler p b.rlo b.hhi).layer,
      (maximumLayerCompiler p b.rlo b.hhi).quotient) = value := Option.some.inj heq
  subst value
  exact rectangleLayerPlateauCheck_sound hp hb.1 hx hc

/-- Every output leaf is a valid subrectangle, regardless of available fuel. -/
theorem adaptiveDecompose_leaf_subset (p fuel : ℕ) {b : ParameterBox}
    (hb : b.Valid) {l : PlateauLeaf} (hl : l ∈ adaptiveDecompose p fuel b) :
    l.box.Valid ∧ ∀ r h, l.box.Contains r h → b.Contains r h := by
  induction fuel generalizing b with
  | zero =>
    simp only [adaptiveDecompose, List.mem_singleton] at hl
    subst l
    exact ⟨hb, fun _ _ hx => hx⟩
  | succ n ih =>
    simp only [adaptiveDecompose] at hl
    split at hl
    · simp only [List.mem_singleton] at hl
      subst l
      exact ⟨hb, fun _ _ hx => hx⟩
    · rename_i hc
      have hs := parameterBox_span_pos_of_failed_check p hb hc
      have hv := parameterBox_split_valid_and_decreases hb hs
      rcases List.mem_append.mp hl with hl | hl
      · obtain ⟨hv', hi⟩ := ih hv.1 hl
        exact ⟨hv', fun r h hx => (parameterBox_split_subset hb hs).1 (hi r h hx)⟩
      · obtain ⟨hv', hi⟩ := ih hv.2.1 hl
        exact ⟨hv', fun r h hx => (parameterBox_split_subset hb hs).2 (hi r h hx)⟩

/-- Every sealed label is correct at every point, including in partial outputs. -/
theorem adaptiveDecompose_sound {p : ℕ} (hp : p.Prime) (fuel : ℕ)
    {b : ParameterBox} (hb : b.Valid) {l : PlateauLeaf}
    (hl : l ∈ adaptiveDecompose p fuel b) : l.Sound p := by
  induction fuel generalizing b with
  | zero =>
    simp only [adaptiveDecompose, List.mem_singleton] at hl
    subst l
    refine ⟨hb, ?_⟩
    intro value heq
    cases heq
  | succ n ih =>
    simp only [adaptiveDecompose] at hl
    split at hl
    · rename_i hc
      simp only [List.mem_singleton] at hl
      subst l
      exact sealedPlateauLeaf_sound hp hb hc
    · rename_i hc
      have hv := parameterBox_split_valid_and_decreases hb
        (parameterBox_span_pos_of_failed_check p hb hc)
      rcases List.mem_append.mp hl with hl | hl
      · exact ih hv.1 hl
      · exact ih hv.2.1 hl

/-- Exact once-only coverage: no omissions, duplicates, or points outside the parent. -/
theorem adaptiveDecompose_exact_coverage (p fuel : ℕ) {b : ParameterBox}
    (hb : b.Valid) (r h : ℕ) :
    leafCoverCount (adaptiveDecompose p fuel b) r h =
      if b.Contains r h then 1 else 0 := by
  induction fuel generalizing b with
  | zero => simp [adaptiveDecompose, leafCoverCount, unresolvedPlateauLeaf]
  | succ n ih =>
    simp only [adaptiveDecompose]
    split
    · by_cases hx : b.Contains r h <;>
        simp [leafCoverCount, sealedPlateauLeaf, hx]
    · rename_i hc
      have hs := parameterBox_span_pos_of_failed_check p hb hc
      have hv := parameterBox_split_valid_and_decreases hb hs
      rw [leafCoverCount_append, ih hv.1, ih hv.2.1]
      have hpart := parameterBox_split_partition hb hs r h
      by_cases h1 : b.split.1.Contains r h <;>
        by_cases h2 : b.split.2.Contains r h <;>
        by_cases h0 : b.Contains r h <;> simp_all

/-- Positive cover count supplies an actual leaf occurrence. -/
theorem leafCoverCount_pos_iff (ls : List PlateauLeaf) (r h : ℕ) :
    0 < leafCoverCount ls r h ↔ ∃ l ∈ ls, l.box.Contains r h := by
  induction ls with
  | nil => simp [leafCoverCount]
  | cons l ls ih =>
    simp only [leafCoverCount, List.mem_cons]
    by_cases hx : l.box.Contains r h
    · simp [hx]
    · simp [hx, ih]

/-- Every original point belongs to a returned leaf, sealed or unresolved. -/
theorem adaptiveDecompose_covers (p fuel : ℕ) {b : ParameterBox}
    (hb : b.Valid) {r h : ℕ} (hx : b.Contains r h) :
    ∃ l ∈ adaptiveDecompose p fuel b, l.box.Contains r h := by
  apply (leafCoverCount_pos_iff _ r h).mp
  rw [adaptiveDecompose_exact_coverage p fuel hb]
  simp [hx]

/-- Explicit sufficient fuel: each split strictly decreases the sum of side spans. -/
theorem adaptiveDecompose_complete (p fuel : ℕ) {b : ParameterBox}
    (hb : b.Valid) (hf : b.span < fuel) {l : PlateauLeaf}
    (hl : l ∈ adaptiveDecompose p fuel b) : l.label.isSome = true := by
  induction fuel generalizing b with
  | zero => omega
  | succ n ih =>
    simp only [adaptiveDecompose] at hl
    split at hl
    · simp only [List.mem_singleton] at hl
      subst l
      rfl
    · rename_i hc
      have hv := parameterBox_split_valid_and_decreases hb
        (parameterBox_span_pos_of_failed_check p hb hc)
      rcases List.mem_append.mp hl with hl | hl
      · exact ih hv.1 (by omega) hl
      · exact ih hv.2.1 (by omega) hl

/-- A closed, terminating exact decomposition with no unresolved leaves. -/
def completeDecompose (p : ℕ) (b : ParameterBox) : List PlateauLeaf :=
  adaptiveDecompose p (b.span + 1) b

theorem completeDecompose_all_sealed (p : ℕ) {b : ParameterBox}
    (hb : b.Valid) {l : PlateauLeaf} (hl : l ∈ completeDecompose p b) :
    l.label.isSome = true := by
  exact adaptiveDecompose_complete p (b.span + 1) hb (by omega) hl

/-- Exhaustion is explicit: even a singleton is unresolved at depth fuel zero. -/
theorem adaptiveDecompose_zero (p : ℕ) (b : ParameterBox) :
    adaptiveDecompose p 0 b = [unresolvedPlateauLeaf b] := rfl

end KomorebiPadic
