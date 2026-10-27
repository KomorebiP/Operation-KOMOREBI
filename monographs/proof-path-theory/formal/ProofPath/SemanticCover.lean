import ProofPath.Extension

/-!
An exact semantic replacement for whole-support coverage.
No constraint is silently discarded: every discarded rule needs a derivation
of its conclusion from its premises in the retained system.
-/
namespace ProofPath
namespace Field
variable {ι J I : Type*} (F : Field ι J)

def filtered (keep : J → Prop) : Field ι J :=
  { F with certified := fun j => F.certified j ∧ keep j }

theorem filtered_model_of_model (keep : J → Prop) {x : ι → Prop}
    (hx : F.Model x) : (F.filtered keep).Model x :=
  ⟨hx.1, fun j hj hp => hx.2 j hj.1 hp⟩

/-- Retained rules suffice precisely when each original rule is entailed. -/
theorem filtered_models_iff_rule_entailment (keep : J → Prop) :
    (∀ x, (F.filtered keep).Model x → F.Model x) ↔
      ∀ j, F.certified j → F.conclusion j ∈ (F.filtered keep).closure (F.premises j) := by
  constructor
  · intro h j hc
    have hx := h _ ((F.filtered keep).closure_is_model (F.premises j))
    exact hx.2 j hc (fun v hv => (F.filtered keep).closure_contains_seed _ hv)
  · intro h x hx
    refine ⟨hx.1, ?_⟩
    intro j hc hp
    exact (F.filtered keep).closure_le_model _ hx hp _ (h j hc)

/-- A complete entailment check preserves every seeded closure, not just one goal. -/
theorem filtered_closures_iff_rule_entailment (keep : J → Prop) :
    (∀ S, (F.filtered keep).closure S = F.closure S) ↔
      ∀ j, F.certified j → F.conclusion j ∈ (F.filtered keep).closure (F.premises j) := by
  constructor
  · intro h j hc
    rw [h]
    exact Derives.step j hc (fun v hv => F.closure_contains_seed _ hv)
  · intro h S
    apply Set.Subset.antisymm
    · exact (F.filtered keep).closure_le_model S
        (F.filtered_model_of_model keep (F.closure_is_model S))
        (fun _ hv => F.closure_contains_seed S hv)
    · exact F.closure_le_model S
        ((F.filtered_models_iff_rule_entailment keep).mpr h _
          ((F.filtered keep).closure_is_model S))
        (fun _ hv => (F.filtered keep).closure_contains_seed S hv)

def visible (U : I → Set ι) : Field ι J :=
  F.filtered (fun j => ∃ i, F.support j ⊆ U i)

def SemanticCover (U : I → Set ι) : Prop :=
  ∀ j, F.certified j → F.conclusion j ∈ (F.visible U).closure (F.premises j)

theorem support_cover_is_semantic (U : I → Set ι)
    (hsup : ∀ j, F.certified j → ∃ i, F.support j ⊆ U i) :
    F.SemanticCover U := by
  intro j hc
  exact Derives.step j ⟨hc, hsup j hc⟩
    (fun v hv => (F.visible U).closure_contains_seed _ hv)

/-- Matching data already satisfy all rules whose supports the patches see. -/
theorem matching_visible_model (U : I → Set ι) (s : ∀ i, F.Local (U i))
    (hcov : ∀ v, ∃ i, v ∈ U i) (hm : F.Matching U s) :
    (F.visible U).Model (F.gluedValue U s) := by
  constructor
  · intro v hl
    obtain ⟨i, hi⟩ := hcov v
    exact ⟨i, hi, (s i).leaves v hl hi⟩
  · rintro j ⟨hc, i, hs⟩ hp
    apply (F.glued_agrees U s hm i (hs (Set.mem_insert _ _))).mpr
    apply (s i).rules j hc hs
    intro v hv
    exact (F.glued_agrees U s hm i (hs (Set.mem_insert_of_mem _ hv))).mp (hp v hv)

theorem semantic_cover_gluing (U : I → Set ι) (s : ∀ i, F.Local (U i))
    (hcov : ∀ v, ∃ i, v ∈ U i) (hsem : F.SemanticCover U)
    (hm : F.Matching U s) :
    ∃! x : ι → Prop, F.Model x ∧
      ∀ i v, v ∈ U i → (x v ↔ (s i).val v) := by
  have hx := (F.filtered_models_iff_rule_entailment _).mpr hsem _
    (F.matching_visible_model U s hcov hm)
  refine ⟨F.gluedValue U s, ⟨hx, ?_⟩, ?_⟩
  · intro i v hv
    exact F.glued_agrees U s hm i hv
  · intro y hy
    funext v
    obtain ⟨i, hi⟩ := hcov v
    exact propext ((hy.2 i v hi).trans (F.glued_agrees U s hm i hi).symm)

/-- A visible model restricts to genuine local models of the original field. -/
def visibleLocal (U : I → Set ι) (x : ι → Prop)
    (hx : (F.visible U).Model x) (i : I) : F.Local (U i) where
  val v := v ∈ U i ∧ x v
  outside _ hv h := hv h.1
  leaves _ hl hu := ⟨hu, hx.1 _ hl⟩
  rules j hc hs hp :=
    ⟨hs (Set.mem_insert _ _), hx.2 j ⟨hc, i, hs⟩ (fun v hv => (hp v hv).2)⟩

/-- With node coverage, semantic cover is necessary and sufficient for all gluing. -/
theorem universal_gluing_iff_semantic_cover (U : I → Set ι)
    (hcov : ∀ v, ∃ i, v ∈ U i) :
    (∀ (s : ∀ i, F.Local (U i)), F.Matching U s →
      ∃! x : ι → Prop, F.Model x ∧ ∀ i v, v ∈ U i → (x v ↔ (s i).val v)) ↔
      F.SemanticCover U := by
  constructor
  · intro hall
    apply (F.filtered_models_iff_rule_entailment _).mp
    intro x hx
    let s := F.visibleLocal U x hx
    have hm : F.Matching U s := by
      intro i j v hi hj
      exact ⟨fun h => ⟨hj, h.2⟩, fun h => ⟨hi, h.2⟩⟩
    obtain ⟨y, hy, _⟩ := hall s hm
    have hxy : x = y := by
      funext v
      obtain ⟨i, hi⟩ := hcov v
      apply propext
      exact ⟨fun h => (hy.2 i v hi).mpr ⟨hi, h⟩,
        fun h => ((hy.2 i v hi).mp h).2⟩
    rw [hxy]
    exact hy.1
  · intro hsem s hm
    exact F.semantic_cover_gluing U s hcov hsem hm

end Field
end ProofPath
