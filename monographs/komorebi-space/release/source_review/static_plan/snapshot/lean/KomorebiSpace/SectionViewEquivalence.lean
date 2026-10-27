import KomorebiSpace.ViewEquivalence

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# Coherent section spaces under an equivalent view presentation

This is the existing subtype of coherent families. No new definition of a
section is introduced. Both directions preserve the prescribed evaluations.
-/
universe u₁ u₂ v₁ v₂ w
namespace KomorebiSpace
open CategoryTheory
namespace ViewSystem
variable {V : Type u₁} [Category.{v₁} V]
variable {W : Type u₂} [Category.{v₂} W]
variable (F : ViewSystem.{u₂,v₂,w} W)

/-- Reindex the actual set-valued view system. -/
def reindex (H : V ⥤ W) : ViewSystem V where
  Obj := fun a => F.Obj (H.obj a)
  pull := fun f => F.pull (H.map f)
  pull_id := by intro a x; rw [H.map_id, F.pull_id]
  pull_comp := by intro a b c f g x; rw [H.map_comp, F.pull_comp]

/-- Read a coherent family at the image views. -/
def reindexSection (H : V ⥤ W) (x : F.Ambient) : (F.reindex H).Ambient :=
  ⟨fun v => x.val (H.obj v), by intro a b f; exact x.property _ _ (H.map f)⟩

@[simp] theorem reindexSection_coordinate (H : V ⥤ W) (x : F.Ambient) (v : V) :
    (F.reindexSection H x).val v = x.val (H.obj v) := rfl

/-- Recover all view coordinates using the actual inverse counit restrictions. -/
def recoverSection (e : V ≌ W) (x : (F.reindex e.functor).Ambient) : F.Ambient :=
  ⟨fun w => F.pull (GroupViewSystem.returnArrow e w) (x.val (e.inverse.obj w)), by
    intro a b f
    change F.pull f (F.pull (GroupViewSystem.returnArrow e b) (x.val (e.inverse.obj b))) =
      F.pull (GroupViewSystem.returnArrow e a) (x.val (e.inverse.obj a))
    have hn : f ≫ GroupViewSystem.returnArrow e b =
        GroupViewSystem.returnArrow e a ≫ e.functor.map (e.inverse.map f) :=
      e.counitIso.inv.naturality f
    rw [← F.pull_comp, hn, F.pull_comp]
    have h := x.property (e.inverse.obj a) (e.inverse.obj b) (e.inverse.map f)
    exact congrArg (F.pull (GroupViewSystem.returnArrow e a)) h⟩

@[simp] theorem recover_reindex (e : V ≌ W) (x : F.Ambient) :
    F.recoverSection e (F.reindexSection e.functor x) = x := by
  apply Ambient.ext
  intro w
  exact x.property _ _ (GroupViewSystem.returnArrow e w)

@[simp] theorem reindex_recover (e : V ≌ W) (x : (F.reindex e.functor).Ambient) :
    F.reindexSection e.functor (F.recoverSection e x) = x := by
  apply Ambient.ext
  intro v
  change F.pull (GroupViewSystem.returnArrow e (e.functor.obj v))
    (x.val (e.inverse.obj (e.functor.obj v))) = x.val v
  rw [← GroupViewSystem.mapped_unit_eq_return e v]
  exact x.property _ _ (e.unitIso.hom.app v)

/-- Ambient realization is invariant under equivalent view presentations. -/
def viewEquivalence (e : V ≌ W) : F.Ambient ≃ (F.reindex e.functor).Ambient where
  toFun := F.reindexSection e.functor
  invFun := F.recoverSection e
  left_inv := F.recover_reindex e
  right_inv := F.reindex_recover e

@[simp] theorem viewEquivalence_coordinate (e : V ≌ W) (x : F.Ambient) (v : V) :
    (F.viewEquivalence e x).val v = x.val (e.functor.obj v) := rfl

/-- Existence is preserved; equivalent views cannot create a missing coherent section. -/
theorem ambient_nonempty_iff (e : V ≌ W) :
    Nonempty F.Ambient ↔ Nonempty (F.reindex e.functor).Ambient :=
  (F.viewEquivalence e).nonempty_congr

/-- The same comparison also preserves uniqueness of a section when one exists. -/
theorem ambient_subsingleton_iff (e : V ≌ W) :
    Subsingleton F.Ambient ↔ Subsingleton (F.reindex e.functor).Ambient :=
  (F.viewEquivalence e).subsingleton_congr

end ViewSystem

namespace GroupViewSystem
variable {V : Type u₁} [Category.{v₁} V]
variable {W : Type u₂} [Category.{v₂} W]
variable {G : W → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem W G) (e : V ≌ W)

/-- Twisted sections are also the previously defined ambient types. -/
def reindexTwistedSections (c : F.Cocycle) :
    (F.twistedViews c).Ambient ≃
      ((F.reindex e.functor).twistedViews (F.reindexCocycle e.functor c)).Ambient :=
  (F.twistedViews c).viewEquivalence e

@[simp] theorem reindexTwistedSections_coordinate (c : F.Cocycle)
    (x : (F.twistedViews c).Ambient) (v : V) :
    (F.reindexTwistedSections e c x).val v = x.val (e.functor.obj v) := rfl

end GroupViewSystem
end KomorebiSpace
