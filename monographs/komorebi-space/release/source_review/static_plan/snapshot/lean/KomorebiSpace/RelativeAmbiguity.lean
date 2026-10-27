import KomorebiSpace.RelativeSections
import KomorebiSpace.NonabelianExtensionFibers

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# The group of invisible coherent changes under equivalent views

This is the existing ambiguity group, with its actual multiplication. The
comparison is a multiplicative equivalence, and it intertwines the previously
proved parametrization of all extensions after choosing a base extension.
-/
universe u₁ u₂ v₁ v₂ w
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem
variable {V : Type u₁} [Category.{v₁} V]
variable {W : Type u₂} [Category.{v₂} W]
variable {G : W → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem W G)

/-- Coherent invisible changes pull back without altering their group law. -/
def reindexInvisible (H : V ⥤ W) (U : Set W) (a : F.invisible U) :
    (F.reindex H).invisible (H.obj ⁻¹' U) :=
  ⟨fun v => a.val (H.obj v),
    ⟨fun v w f => a.property.1 (H.obj v) (H.obj w) (H.map f),
     fun v => a.property.2 ⟨H.obj v.val,v.property⟩⟩⟩

/-- Recover invisibility at every prescribed target view using saturation. -/
def recoverInvisible (e : V ≌ W) (U : Set W) (hU : CompositionSite.IsoClosed U)
    (a : (F.reindex e.functor).invisible (e.functor.obj ⁻¹' U)) : F.invisible U := by
  let y : (F.views.reindex e.functor).Ambient := ⟨a.val,a.property.1⟩
  let x := F.views.recoverSection e y
  refine ⟨x.val, x.property, ?_⟩
  intro w
  have hm : e.functor.obj (e.inverse.obj w.val) ∈ U :=
    hU (e.counitIso.app w.val).symm w.property
  change F.pull (returnArrow e w.val) (a.val (e.inverse.obj w.val)) = 1
  rw [a.property.2 ⟨e.inverse.obj w.val,hm⟩, map_one]

/-- The complete nonabelian ambiguity group is preserved, not just its cardinality. -/
def invisibleViewEquivalence (e : V ≌ W) (U : Set W)
    (hU : CompositionSite.IsoClosed U) :
    F.invisible U ≃* (F.reindex e.functor).invisible (e.functor.obj ⁻¹' U) where
  toFun := F.reindexInvisible e.functor U
  invFun := F.recoverInvisible e U hU
  left_inv a := by
    apply Subtype.ext
    funext w
    exact a.property.1 _ _ (returnArrow e w)
  right_inv a := by
    apply Subtype.ext
    funext v
    change F.pull (returnArrow e (e.functor.obj v))
      (a.val (e.inverse.obj (e.functor.obj v))) = a.val v
    rw [← mapped_unit_eq_return e v]
    exact a.property.1 _ _ (e.unitIso.hom.app v)
  map_mul' _ _ := rfl

@[simp] theorem invisibleViewEquivalence_coordinate (e : V ≌ W) (U : Set W)
    (hU : CompositionSite.IsoClosed U) (a : F.invisible U) (v : V) :
    (F.invisibleViewEquivalence e U hU a).val v = a.val (e.functor.obj v) := rfl

/-- The action parametrizing possible extensions agrees with view pullback. -/
theorem extensionParameters_reindex (e : V ≌ W) (U : Set W)
    (hU : CompositionSite.IsoClosed U) (c : F.Cocycle)
    (s : (F.twistedViews c).Partial U) (base : (F.twistedViews c).Extensions U s)
    (a : F.invisible U) :
    F.relativeTwistedEquivalence e U hU c s (F.extensionParameters c U s base a) =
      (F.reindex e.functor).extensionParameters (F.reindexCocycle e.functor c)
        (e.functor.obj ⁻¹' U) ((F.twistedViews c).reindexPartial e.functor U s)
        (F.relativeTwistedEquivalence e U hU c s base)
        (F.invisibleViewEquivalence e U hU a) := by
  apply Subtype.ext
  apply ViewSystem.Ambient.ext
  intro v
  rfl

/-- The full existence-and-uniqueness condition is invariant for the transported problem. -/
theorem relative_unique_iff (e : V ≌ W) (U : Set W)
    (hU : CompositionSite.IsoClosed U) (c : F.Cocycle)
    (s : (F.twistedViews c).Partial U) :
    (∃! x : (F.twistedViews c).Ambient, (F.twistedViews c).restrict U x = s) ↔
      (∃! y : ((F.reindex e.functor).twistedViews (F.reindexCocycle e.functor c)).Ambient,
        ((F.reindex e.functor).twistedViews (F.reindexCocycle e.functor c)).restrict
          (e.functor.obj ⁻¹' U) y = (F.twistedViews c).reindexPartial e.functor U s) := by
  rw [F.unique_extension_iff, (F.reindex e.functor).unique_extension_iff]
  exact and_congr (F.relative_neutral_iff e U hU c s)
    (F.invisibleViewEquivalence e U hU).toEquiv.subsingleton_congr

end GroupViewSystem
end KomorebiSpace
