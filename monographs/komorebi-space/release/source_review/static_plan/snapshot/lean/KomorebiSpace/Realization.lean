import Mathlib.Data.Nat.Basic
import Mathlib.Logic.Equiv.Basic

set_option autoImplicit false

/-!
# Concrete inverse-limit realization

A set-valued resolution has restriction maps for all ordered pairs of levels.
Its limit consists of coherent coordinates. This is an actual construction,
not an existence axiom for a global object.
-/
universe u v w
namespace KomorebiSpace

structure Resolution where
  Obj : ℕ → Type u
  restrict : {i j : ℕ} → i ≤ j → Obj j → Obj i
  restrict_refl : ∀ n (x : Obj n), restrict (Nat.le_refl n) x = x
  restrict_trans : ∀ {i j k : ℕ} (hij : i ≤ j) (hjk : j ≤ k) (x : Obj k),
    restrict hij (restrict hjk x) = restrict (Nat.le_trans hij hjk) x

namespace Resolution

def Point (X : Resolution.{u}) :=
  {x : ∀ n, X.Obj n // ∀ i j (h : i ≤ j), X.restrict h (x j) = x i}

@[ext] theorem Point.ext {X : Resolution.{u}} {x y : X.Point}
    (h : ∀ n, x.val n = y.val n) : x = y := Subtype.ext (funext h)

structure PreMap (X : Resolution.{u}) (Y : Resolution.{v}) where
  app : ∀ n, X.Obj n → Y.Obj n

def PreMap.Exact {X : Resolution.{u}} {Y : Resolution.{v}} (f : PreMap X Y) : Prop :=
  ∀ i j (h : i ≤ j) (x : X.Obj j),
    Y.restrict h (f.app j x) = f.app i (X.restrict h x)

structure Map (X : Resolution.{u}) (Y : Resolution.{v}) extends PreMap X Y where
  exact : toPreMap.Exact

namespace Map
variable {X : Resolution.{u}} {Y : Resolution.{v}} {Z : Resolution.{w}}

def id (X : Resolution.{u}) : Map X X where
  app := fun _ x => x
  exact := by intro i j h x; rfl

def comp (f : Map X Y) (g : Map Y Z) : Map X Z where
  app := fun n x => g.app n (f.app n x)
  exact := by
    intro i j h x
    change Z.restrict h (g.app j (f.app j x)) = g.app i (f.app i (X.restrict h x))
    rw [g.exact, f.exact]

/-- Exact finite-level maps induce an actual map between the limits. -/
def onLimit (f : Map X Y) (x : X.Point) : Y.Point :=
  ⟨fun n => f.app n (x.val n), by
    intro i j h
    rw [f.exact, x.property i j h]⟩

@[simp] theorem onLimit_apply (f : Map X Y) (x : X.Point) (n : ℕ) :
    (f.onLimit x).val n = f.app n (x.val n) := rfl

@[simp] theorem onLimit_id (x : X.Point) : (id X).onLimit x = x := rfl

@[simp] theorem onLimit_comp (f : Map X Y) (g : Map Y Z) (x : X.Point) :
    (comp f g).onLimit x = g.onLimit (f.onLimit x) := rfl

/-- Uniqueness is coordinatewise, with the coordinate specification explicit. -/
theorem onLimit_unique (f : Map X Y) (g : X.Point → Y.Point)
    (hg : ∀ x n, (g x).val n = f.app n (x.val n)) : g = f.onLimit := by
  funext x
  exact Point.ext (hg x)

end Map

structure Cone (X : Resolution.{u}) (S : Type v) where
  leg : ∀ n, S → X.Obj n
  coherent : ∀ i j (h : i ≤ j) s, X.restrict h (leg j s) = leg i s

namespace Cone
variable {X : Resolution.{u}} {S : Type v}

def lift (c : Cone X S) (s : S) : X.Point :=
  ⟨fun n => c.leg n s, fun i j h => c.coherent i j h s⟩

@[simp] theorem lift_coordinate (c : Cone X S) (s : S) (n : ℕ) :
    (c.lift s).val n = c.leg n s := rfl

theorem lift_unique (c : Cone X S) (f : S → X.Point)
    (hf : ∀ s n, (f s).val n = c.leg n s) : f = c.lift := by
  funext s; exact Point.ext (hf s)

/-- Universal property of the explicitly constructed inverse limit. -/
theorem exists_unique_lift (c : Cone X S) :
    ∃! f : S → X.Point, ∀ s n, (f s).val n = c.leg n s := by
  refine ⟨c.lift, by intro s n; rfl, ?_⟩
  intro f hf; exact c.lift_unique f hf
end Cone

/-- Realization in externally supplied objects requires explicit limit equivalences. -/
def realize {X : Resolution.{u}} {Y : Resolution.{v}} {S : Type u} {T : Type v}
    (eX : S ≃ X.Point) (eY : T ≃ Y.Point) (f : Map X Y) : S → T :=
  fun s => eY.symm (f.onLimit (eX s))

theorem realize_coordinate {X : Resolution.{u}} {Y : Resolution.{v}}
    {S : Type u} {T : Type v} (eX : S ≃ X.Point) (eY : T ≃ Y.Point)
    (f : Map X Y) (s : S) (n : ℕ) :
    (eY (realize eX eY f s)).val n = f.app n ((eX s).val n) := by
  simp [realize]

end Resolution
end KomorebiSpace
