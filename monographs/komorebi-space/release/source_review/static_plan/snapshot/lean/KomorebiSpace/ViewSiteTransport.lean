import KomorebiSpace.CompositionSite
import KomorebiSpace.ViewEquivalence

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# Composition covers under a change of view category

Inverse image preserves composition covers for any functor. Reflection under
an equivalence requires patches closed under isomorphism. Raw subsets are not
silently treated as equivalence-invariant patches.
-/
universe u₁ u₂ v₁ v₂ z
namespace KomorebiSpace
open CategoryTheory
namespace CompositionSite
variable {V : Type u₁} [Category.{v₁} V]
variable {W : Type u₂} [Category.{v₂} W]

/-- A patch closed under replacing a view by an isomorphic view. -/
def IsoClosed (S : Set V) : Prop :=
  ∀ ⦃a b : V⦄, (a ≅ b) → a ∈ S → b ∈ S

theorem mem_iff_of_iso {S : Set V} (h : IsoClosed S) {a b : V} (i : a ≅ b) :
    a ∈ S ↔ b ∈ S := ⟨h i, h i.symm⟩

/-- No fullness or equivalence is needed for preservation of covers. -/
theorem familyCovers_preimage (H : V ⥤ W) {I : Type z}
    {S : Set W} {U : I → Set W} (h : FamilyCovers S U) :
    FamilyCovers (H.obj ⁻¹' S) (fun i => H.obj ⁻¹' U i) := by
  intro q hq
  let t : Triangle W := ⟨H.obj q.a, H.obj q.b, H.obj q.c,
    H.map q.first, H.map q.second⟩
  have ht : t.support ⊆ S := (t.support_le_iff S).mpr
    ⟨hq q.a_mem, hq q.b_mem, hq q.c_mem⟩
  obtain ⟨i, hi⟩ := h t ht
  exact ⟨i, (q.support_le_iff _).mpr ⟨hi t.a_mem, hi t.b_mem, hi t.c_mem⟩⟩

/-- Reflection uses isomorphism closure of the original patch and cover members. -/
theorem familyCovers_reflect (e : V ≌ W) {I : Type z}
    {S : Set W} {U : I → Set W} (hS : IsoClosed S) (hU : ∀ i, IsoClosed (U i))
    (h : FamilyCovers (e.functor.obj ⁻¹' S) (fun i => e.functor.obj ⁻¹' U i)) :
    FamilyCovers S U := by
  intro q hq
  let t : Triangle V := ⟨e.inverse.obj q.a, e.inverse.obj q.b, e.inverse.obj q.c,
    e.inverse.map q.first, e.inverse.map q.second⟩
  have ht : t.support ⊆ e.functor.obj ⁻¹' S := (t.support_le_iff _).mpr
    ⟨hS (e.counitIso.app q.a).symm (hq q.a_mem),
     hS (e.counitIso.app q.b).symm (hq q.b_mem),
     hS (e.counitIso.app q.c).symm (hq q.c_mem)⟩
  obtain ⟨i, hi⟩ := h t ht
  exact ⟨i, (q.support_le_iff _).mpr
    ⟨hU i (e.counitIso.app q.a) (hi t.a_mem),
     hU i (e.counitIso.app q.b) (hi t.b_mem),
     hU i (e.counitIso.app q.c) (hi t.c_mem)⟩⟩

/-- The exact cover comparison, without an unsupported claim about all subsets. -/
theorem familyCovers_preimage_iff (e : V ≌ W) {I : Type z}
    {S : Set W} {U : I → Set W} (hS : IsoClosed S) (hU : ∀ i, IsoClosed (U i)) :
    FamilyCovers (e.functor.obj ⁻¹' S) (fun i => e.functor.obj ⁻¹' U i) ↔
      FamilyCovers S U :=
  ⟨familyCovers_reflect e hS hU, familyCovers_preimage e.functor⟩

theorem isoClosed_preimage (H : V ⥤ W) {S : Set W} (h : IsoClosed S) :
    IsoClosed (H.obj ⁻¹' S) := by
  intro a b i hi
  exact h (H.mapIso i) hi

/-- An isomorphism-closed patch, with its inherited inclusion order. -/
def SaturatedPatch (V : Type u₁) [Category.{v₁} V] := {S : Set V // IsoClosed S}

instance : PartialOrder (SaturatedPatch V) := inferInstanceAs (PartialOrder {S : Set V // IsoClosed S})

/-- On isomorphism-closed patches, inverse image is an actual order isomorphism. -/
def saturatedPatchEquiv (e : V ≌ W) : SaturatedPatch W ≃o SaturatedPatch V where
  toFun S := ⟨e.functor.obj ⁻¹' S.val, isoClosed_preimage e.functor S.property⟩
  invFun S := ⟨e.inverse.obj ⁻¹' S.val, isoClosed_preimage e.inverse S.property⟩
  left_inv S := by
    apply Subtype.ext
    ext w
    exact mem_iff_of_iso S.property (e.counitIso.app w)
  right_inv S := by
    apply Subtype.ext
    ext v
    exact mem_iff_of_iso S.property (e.unitIso.app v).symm
  map_rel_iff' := by
    intro S T
    constructor
    · intro h w hw
      exact T.property (e.counitIso.app w)
        (h (S.property (e.counitIso.app w).symm hw))
    · intro h v hv
      exact h hv

@[simp] theorem saturatedPatchEquiv_value (e : V ≌ W) (S : SaturatedPatch W) :
    (saturatedPatchEquiv e S).val = e.functor.obj ⁻¹' S.val := rfl

end CompositionSite
end KomorebiSpace
