import KomorebiSpace.SectionViewEquivalence
import KomorebiSpace.ViewSiteTransport
import KomorebiSpace.NonabelianExtension

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# Prescribed section problems under equivalent views

The source and target are the existing section and extension types. Prescribed
values are pulled back along the actual view functor. Isomorphism closure of
the prescribed domain allows the inverse counit to recover every prescribed
coordinate. No equivalence of all based-gauge orbit sets is asserted.
-/
universe u₁ u₂ v₁ v₂ w
namespace KomorebiSpace
open CategoryTheory
namespace ViewSystem
variable {V : Type u₁} [Category.{v₁} V]
variable {W : Type u₂} [Category.{v₂} W]
variable (F : ViewSystem.{u₂,v₂,w} W)

/-- Prescribed data at image views, with the original coherence equations. -/
def reindexPartial (H : V ⥤ W) (U : Set W) (s : F.Partial U) :
    (F.reindex H).Partial (H.obj ⁻¹' U) :=
  ⟨fun v => s.val ⟨H.obj v.val, v.property⟩, by
    intro a b f
    exact s.property ⟨H.obj a.val,a.property⟩ ⟨H.obj b.val,b.property⟩ (H.map f)⟩

@[simp] theorem reindexPartial_coordinate (H : V ⥤ W) (U : Set W)
    (s : F.Partial U) (v : H.obj ⁻¹' U) :
    (F.reindexPartial H U s).val v = s.val ⟨H.obj v.val,v.property⟩ := rfl

@[simp] theorem reindex_restrict (H : V ⥤ W) (U : Set W) (x : F.Ambient) :
    (F.reindex H).restrict (H.obj ⁻¹' U) (F.reindexSection H x) =
      F.reindexPartial H U (F.restrict U x) := rfl

/-- Forward transport of an actual extension with its prescribed values. -/
def reindexExtension (H : V ⥤ W) (U : Set W) (s : F.Partial U)
    (x : F.Extensions U s) :
    (F.reindex H).Extensions (H.obj ⁻¹' U) (F.reindexPartial H U s) :=
  ⟨F.reindexSection H x.val, by rw [F.reindex_restrict, x.property]⟩

/-- The recovered global section retains every prescribed target view. -/
def recoverExtension (e : V ≌ W) (U : Set W) (hU : CompositionSite.IsoClosed U)
    (s : F.Partial U)
    (x : (F.reindex e.functor).Extensions (e.functor.obj ⁻¹' U)
      (F.reindexPartial e.functor U s)) : F.Extensions U s := by
  refine ⟨F.recoverSection e x.val, ?_⟩
  apply Partial.ext
  intro w
  have hm : e.functor.obj (e.inverse.obj w.val) ∈ U :=
    hU (e.counitIso.app w.val).symm w.property
  have hx := congrArg (fun t : (F.reindex e.functor).Partial (e.functor.obj ⁻¹' U) =>
    t.val ⟨e.inverse.obj w.val,hm⟩) x.property
  change x.val.val (e.inverse.obj w.val) =
    s.val ⟨e.functor.obj (e.inverse.obj w.val),hm⟩ at hx
  change F.pull (GroupViewSystem.returnArrow e w.val)
    (x.val.val (e.inverse.obj w.val)) = s.val w
  rw [hx]
  exact s.property w ⟨e.functor.obj (e.inverse.obj w.val),hm⟩
    (GroupViewSystem.returnArrow e w.val)

/-- All global completions, not only their existence, are preserved. -/
def relativeViewEquivalence (e : V ≌ W) (U : Set W)
    (hU : CompositionSite.IsoClosed U) (s : F.Partial U) :
    F.Extensions U s ≃
      (F.reindex e.functor).Extensions (e.functor.obj ⁻¹' U)
        (F.reindexPartial e.functor U s) where
  toFun := F.reindexExtension e.functor U s
  invFun := F.recoverExtension e U hU s
  left_inv x := Subtype.ext (F.recover_reindex e x.val)
  right_inv x := Subtype.ext (F.reindex_recover e x.val)

@[simp] theorem relativeViewEquivalence_coordinate (e : V ≌ W) (U : Set W)
    (hU : CompositionSite.IsoClosed U) (s : F.Partial U) (x : F.Extensions U s) (v : V) :
    (F.relativeViewEquivalence e U hU s x).val.val v = x.val.val (e.functor.obj v) := rfl

theorem relative_nonempty_iff (e : V ≌ W) (U : Set W)
    (hU : CompositionSite.IsoClosed U) (s : F.Partial U) :
    Nonempty (F.Extensions U s) ↔
      Nonempty ((F.reindex e.functor).Extensions (e.functor.obj ⁻¹' U)
        (F.reindexPartial e.functor U s)) :=
  (F.relativeViewEquivalence e U hU s).nonempty_congr

theorem relative_subsingleton_iff (e : V ≌ W) (U : Set W)
    (hU : CompositionSite.IsoClosed U) (s : F.Partial U) :
    Subsingleton (F.Extensions U s) ↔
      Subsingleton ((F.reindex e.functor).Extensions (e.functor.obj ⁻¹' U)
        (F.reindexPartial e.functor U s)) :=
  (F.relativeViewEquivalence e U hU s).subsingleton_congr

end ViewSystem

namespace GroupViewSystem
variable {V : Type u₁} [Category.{v₁} V]
variable {W : Type u₂} [Category.{v₂} W]
variable {G : W → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem W G)

/-- The same theorem on the existing twisted section types. -/
def relativeTwistedEquivalence (e : V ≌ W) (U : Set W)
    (hU : CompositionSite.IsoClosed U) (c : F.Cocycle)
    (s : (F.twistedViews c).Partial U) :
    (F.twistedViews c).Extensions U s ≃
      ((F.reindex e.functor).twistedViews (F.reindexCocycle e.functor c)).Extensions
        (e.functor.obj ⁻¹' U) ((F.twistedViews c).reindexPartial e.functor U s) :=
  (F.twistedViews c).relativeViewEquivalence e U hU s

/-- Relative feasibility is invariant even though entire based-gauge orbit sets need not be. -/
theorem relative_neutral_iff (e : V ≌ W) (U : Set W)
    (hU : CompositionSite.IsoClosed U) (c : F.Cocycle)
    (s : (F.twistedViews c).Partial U) :
    F.extensionOrbit c U s = F.neutralClass U ↔
      (F.reindex e.functor).extensionOrbit (F.reindexCocycle e.functor c)
        (e.functor.obj ⁻¹' U) ((F.twistedViews c).reindexPartial e.functor U s) =
      (F.reindex e.functor).neutralClass (e.functor.obj ⁻¹' U) := by
  rw [F.extensionOrbit_neutral_iff, (F.reindex e.functor).extensionOrbit_neutral_iff]
  exact (F.relativeTwistedEquivalence e U hU c s).nonempty_congr

end GroupViewSystem
end KomorebiSpace
