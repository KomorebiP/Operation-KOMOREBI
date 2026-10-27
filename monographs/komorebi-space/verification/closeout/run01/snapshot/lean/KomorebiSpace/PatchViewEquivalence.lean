import KomorebiSpace.ViewSiteTransport
import KomorebiSpace.PatchViewSystem

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# Equivalent presentations of isomorphism-closed view patches

The equivalences use actual full subcategories and commute with restriction.
No equivalence of the posets of all raw subsets is asserted.
-/
universe u₁ u₂ v₁ v₂ w
namespace KomorebiSpace
open CategoryTheory
namespace ViewChange
variable {V : Type u₁} [Category.{v₁} V]
variable {W : Type u₂} [Category.{v₂} W]

/-- Restrict a view functor to the inverse image of a full patch. -/
def patchFunctor (H : V ⥤ W) (S : Set W) :
    PatchViews (H.obj ⁻¹' S) ⥤ PatchViews S where
  obj x := ⟨H.obj x.val, x.property⟩
  map f := InducedCategory.homMk (H.map f.hom)
  map_id := by intro x; apply InducedCategory.hom_ext; exact H.map_id x.val
  map_comp := by intro x y z f g; apply InducedCategory.hom_ext; exact H.map_comp f.hom g.hom

/-- Isomorphism closure makes the inverse representative lie in the source patch. -/
def patchInverse (e : V ≌ W) (S : Set W) (hS : CompositionSite.IsoClosed S) :
    PatchViews S ⥤ PatchViews (e.functor.obj ⁻¹' S) where
  obj x := ⟨e.inverse.obj x.val, hS (e.counitIso.app x.val).symm x.property⟩
  map f := InducedCategory.homMk (e.inverse.map f.hom)
  map_id := by intro x; apply InducedCategory.hom_ext; exact e.inverse.map_id x.val
  map_comp := by intro x y z f g; apply InducedCategory.hom_ext; exact e.inverse.map_comp f.hom g.hom

/-- Unit on the actual full subcategory. -/
def patchUnit (e : V ≌ W) (S : Set W) (hS : CompositionSite.IsoClosed S) :
    𝟭 (PatchViews (e.functor.obj ⁻¹' S)) ≅
      patchFunctor e.functor S ⋙ patchInverse e S hS :=
  NatIso.ofComponents (fun x =>
    { hom := InducedCategory.homMk (e.unitIso.hom.app x.val)
      inv := InducedCategory.homMk (e.unitIso.inv.app x.val)
      hom_inv_id := by apply InducedCategory.hom_ext; exact (e.unitIso.app x.val).hom_inv_id
      inv_hom_id := by apply InducedCategory.hom_ext; exact (e.unitIso.app x.val).inv_hom_id })
    (by intro x y f; apply InducedCategory.hom_ext; exact e.unitIso.hom.naturality f.hom)

/-- Counit on the actual full subcategory. -/
def patchCounit (e : V ≌ W) (S : Set W) (hS : CompositionSite.IsoClosed S) :
    patchInverse e S hS ⋙ patchFunctor e.functor S ≅ 𝟭 (PatchViews S) :=
  NatIso.ofComponents (fun x =>
    { hom := InducedCategory.homMk (e.counitIso.hom.app x.val)
      inv := InducedCategory.homMk (e.counitIso.inv.app x.val)
      hom_inv_id := by apply InducedCategory.hom_ext; exact (e.counitIso.app x.val).hom_inv_id
      inv_hom_id := by apply InducedCategory.hom_ext; exact (e.counitIso.app x.val).inv_hom_id })
    (by intro x y f; apply InducedCategory.hom_ext; exact e.counitIso.hom.naturality f.hom)

/-- Restriction of an equivalence to an isomorphism-closed patch. -/
def patchEquivalence (e : V ≌ W) (S : Set W) (hS : CompositionSite.IsoClosed S) :
    PatchViews (e.functor.obj ⁻¹' S) ≌ PatchViews S :=
  CategoryTheory.Equivalence.mk (patchFunctor e.functor S) (patchInverse e S hS)
    (patchUnit e S hS) (patchCounit e S hS)

@[simp] theorem patchEquivalence_functor (e : V ≌ W) (S : Set W)
    (hS : CompositionSite.IsoClosed S) :
    (patchEquivalence e S hS).functor = patchFunctor e.functor S := rfl

end ViewChange

namespace GroupViewSystem
variable {V : Type u₁} [Category.{v₁} V]
variable {W : Type u₂} [Category.{v₂} W]
variable {G : W → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem W G)

/-- The group coefficients in patch pullback are definitionally the actual restrictions. -/
def patchPullback (H : V ⥤ W) (S : Set W) :
    (F.onPatch S).GaugeObject ∅ ⥤ ((F.reindex H).onPatch (H.obj ⁻¹' S)).GaugeObject ∅ :=
  (F.onPatch S).reindexFunctor (ViewChange.patchFunctor H S)

/-- The forward patch comparisons commute strictly with subpatch restriction. -/
@[simp] theorem patchPullback_restrict (H : V ⥤ W) {S T : Set W} (h : S ⊆ T) :
    F.patchRestrict h ⋙ F.patchPullback H S =
      F.patchPullback H T ⋙ (F.reindex H).patchRestrict (Set.preimage_mono h) := rfl

/-- Existing stack values agree on corresponding isomorphism-closed patches. -/
def saturatedPatchCocycleEquivalence (e : V ≌ W) (S : Set W)
    (hS : CompositionSite.IsoClosed S) :
    (F.onPatch S).GaugeObject ∅ ≌
      ((F.reindex e.functor).onPatch (e.functor.obj ⁻¹' S)).GaugeObject ∅ :=
  (F.onPatch S).reindexEquivalence (ViewChange.patchEquivalence e S hS)

@[simp] theorem saturatedPatchCocycleEquivalence_functor (e : V ≌ W) (S : Set W)
    (hS : CompositionSite.IsoClosed S) :
    (F.saturatedPatchCocycleEquivalence e S hS).functor = F.patchPullback e.functor S := rfl

end GroupViewSystem
end KomorebiSpace
