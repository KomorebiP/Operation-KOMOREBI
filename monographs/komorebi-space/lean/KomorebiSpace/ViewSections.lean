import Mathlib.CategoryTheory.Category.Basic
import Mathlib.Data.Set.Basic
import Mathlib.Logic.Equiv.Basic

set_option autoImplicit false

/-!
# Set-valued views and coherent ambient sections

This is the strict, set-valued layer of the proposed indexed realization system.
It does not assert a higher category or a stack. Arrows point from a restricted
view to a larger view; restriction of data is contravariant.
-/
universe u v w z t
namespace KomorebiSpace
open CategoryTheory

structure ViewSystem (V : Type u) [Category.{v} V] where
  Obj : V → Type w
  pull : {a b : V} → (a ⟶ b) → Obj b → Obj a
  pull_id : ∀ a (x : Obj a), pull (𝟙 a) x = x
  pull_comp : ∀ {a b c : V} (f : a ⟶ b) (g : b ⟶ c) (x : Obj c),
    pull (f ≫ g) x = pull f (pull g x)

namespace ViewSystem
variable {V : Type u} [Category.{v} V]

/-- Coherent data at every view, not a choice of one preferred view. -/
def Ambient (F : ViewSystem.{u,v,w} V) :=
  {x : ∀ a, F.Obj a // ∀ a b (f : a ⟶ b), F.pull f (x b) = x a}

@[ext] theorem Ambient.ext {F : ViewSystem.{u,v,w} V} {x y : F.Ambient}
    (h : ∀ a, x.val a = y.val a) : x = y := Subtype.ext (funext h)

/-- Evaluation need not be individually injective or surjective. -/
def evaluate (F : ViewSystem.{u,v,w} V) (a : V) : F.Ambient → F.Obj a :=
  fun x => x.val a

theorem evaluations_jointly_injective (F : ViewSystem.{u,v,w} V)
    {x y : F.Ambient} (h : ∀ a, F.evaluate a x = F.evaluate a y) : x = y :=
  Ambient.ext h

@[simp] theorem evaluation_coherent (F : ViewSystem.{u,v,w} V)
    (x : F.Ambient) {a b : V} (f : a ⟶ b) :
    F.pull f (F.evaluate b x) = F.evaluate a x := x.property a b f

/-- A family of maps which commutes with restriction. -/
structure Morphism (F : ViewSystem.{u,v,w} V) (G : ViewSystem.{u,v,z} V) where
  app : ∀ a, F.Obj a → G.Obj a
  natural : ∀ {a b : V} (f : a ⟶ b) (x : F.Obj b),
    G.pull f (app b x) = app a (F.pull f x)

namespace Morphism
variable {F : ViewSystem.{u,v,w} V} {G : ViewSystem.{u,v,z} V}

def onAmbient (f : Morphism F G) (x : F.Ambient) : G.Ambient :=
  ⟨fun a => f.app a (x.val a), by
    intro a b e
    rw [f.natural, x.property a b e]⟩

@[simp] theorem onAmbient_evaluate (f : Morphism F G) (x : F.Ambient) (a : V) :
    G.evaluate a (f.onAmbient x) = f.app a (F.evaluate a x) := rfl

def id (F : ViewSystem.{u,v,w} V) : Morphism F F where
  app := fun _ x => x
  natural := by intros; rfl

def comp {H : ViewSystem.{u,v,t} V} (f : Morphism F G) (g : Morphism G H) :
    Morphism F H where
  app := fun a x => g.app a (f.app a x)
  natural := by intros; rw [g.natural, f.natural]

@[simp] theorem onAmbient_id (x : F.Ambient) : (id F).onAmbient x = x := rfl

@[simp] theorem onAmbient_comp {H : ViewSystem.{u,v,t} V}
    (f : Morphism F G) (g : Morphism G H) (x : F.Ambient) :
    (comp f g).onAmbient x = g.onAmbient (f.onAmbient x) := rfl
end Morphism

/-- The usual set-level limit universal property, with legs and coherence explicit. -/
structure Cone (F : ViewSystem.{u,v,w} V) (T : Type z) where
  leg : ∀ a, T → F.Obj a
  coherent : ∀ a b (f : a ⟶ b) x, F.pull f (leg b x) = leg a x

namespace Cone
variable {F : ViewSystem.{u,v,w} V} {T : Type z}

def lift (c : Cone F T) (x : T) : F.Ambient :=
  ⟨fun a => c.leg a x, fun a b f => c.coherent a b f x⟩

@[simp] theorem lift_evaluate (c : Cone F T) (x : T) (a : V) :
    F.evaluate a (c.lift x) = c.leg a x := rfl

theorem lift_unique (c : Cone F T) (g : T → F.Ambient)
    (h : ∀ x a, F.evaluate a (g x) = c.leg a x) : g = c.lift := by
  funext x
  exact Ambient.ext (h x)

theorem exists_unique_lift (c : Cone F T) :
    ∃! g : T → F.Ambient, ∀ x a, F.evaluate a (g x) = c.leg a x := by
  refine ⟨c.lift, by intro x a; rfl, ?_⟩
  intro g h
  exact c.lift_unique g h
end Cone

/-- A partial section includes every transition with both endpoints in its domain. -/
def Partial (F : ViewSystem.{u,v,w} V) (U : Set V) :=
  {x : ∀ a : U, F.Obj a.val //
    ∀ (a b : U) (f : a.val ⟶ b.val), F.pull f (x b) = x a}

@[ext] theorem Partial.ext {F : ViewSystem.{u,v,w} V} {U : Set V}
    {x y : F.Partial U} (h : ∀ a, x.val a = y.val a) : x = y :=
  Subtype.ext (funext h)

def restrict (F : ViewSystem.{u,v,w} V) (U : Set V) (x : F.Ambient) : F.Partial U :=
  ⟨fun a => x.val a.val, fun a b f => x.property a.val b.val f⟩

def restrictPartial (F : ViewSystem.{u,v,w} V) {U W : Set V} (h : U ⊆ W)
    (x : F.Partial W) : F.Partial U :=
  ⟨fun a => x.val ⟨a.val, h a.property⟩, fun a b f => x.property ⟨a.val, h a.property⟩ ⟨b.val, h b.property⟩ f⟩

@[simp] theorem restrictPartial_refl (F : ViewSystem.{u,v,w} V) (U : Set V)
    (x : F.Partial U) : F.restrictPartial (Set.Subset.refl U) x = x := rfl

@[simp] theorem restrictPartial_comp (F : ViewSystem.{u,v,w} V)
    {U W Z : Set V} (h : U ⊆ W) (k : W ⊆ Z) (x : F.Partial Z) :
    F.restrictPartial h (F.restrictPartial k x) = F.restrictPartial (h.trans k) x := rfl

/-- The extension space can be empty, singleton, or contain multiple choices. -/
def Extensions (F : ViewSystem.{u,v,w} V) (U : Set V) (x : F.Partial U) :=
  {s : F.Ambient // F.restrict U s = x}

theorem extension_nonempty_iff (F : ViewSystem.{u,v,w} V) (U : Set V)
    (x : F.Partial U) :
    Nonempty (F.Extensions U x) ↔ ∃ s : F.Ambient, F.restrict U s = x := by
  constructor
  · rintro ⟨⟨s, h⟩⟩; exact ⟨s, h⟩
  · rintro ⟨s, h⟩; exact ⟨⟨s, h⟩⟩

/-- Including a terminal global view makes evaluation at that view an equivalence.
This does not prove that observations on a smaller view domain extend to it. -/
def terminalEvaluationEquiv (F : ViewSystem.{u,v,w} V) (t : V)
    (toTop : ∀ a, a ⟶ t) (ht : toTop t = 𝟙 t)
    (hn : ∀ a b (f : a ⟶ b), f ≫ toTop b = toTop a) :
    F.Ambient ≃ F.Obj t where
  toFun := F.evaluate t
  invFun := fun x => ⟨fun a => F.pull (toTop a) x, by
    intro a b f
    rw [← F.pull_comp, hn]⟩
  left_inv := by
    intro x
    apply Ambient.ext
    intro a
    exact x.property a t (toTop a)
  right_inv := by
    intro x
    change F.pull (toTop t) x = x
    rw [ht, F.pull_id]

@[simp] theorem terminalEvaluation_coordinate (F : ViewSystem.{u,v,w} V) (t : V)
    (toTop : ∀ a, a ⟶ t) (ht : toTop t = 𝟙 t)
    (hn : ∀ a b (f : a ⟶ b), f ≫ toTop b = toTop a) (x : F.Obj t) (a : V) :
    ((F.terminalEvaluationEquiv t toTop ht hn).symm x).val a = F.pull (toTop a) x := rfl

/-- The constant view system is useful for explicit boundary examples. -/
def constant (V : Type u) [Category.{v} V] (T : Type w) : ViewSystem V where
  Obj := fun _ => T
  pull := fun _ x => x
  pull_id := by intros; rfl
  pull_comp := by intros; rfl

def constantSection (V : Type u) [Category.{v} V] {T : Type w} (x : T) :
    (constant V T).Ambient := ⟨fun _ => x, by intros; rfl⟩

end ViewSystem
end KomorebiSpace
