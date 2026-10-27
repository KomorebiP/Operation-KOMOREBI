import KomorebiSpace.ViewSections
import Mathlib.Algebra.Group.Pi.Basic
import Mathlib.Algebra.Group.Subgroup.Basic
import Mathlib.Tactic.Group

set_option autoImplicit false

/-!
# Group-valued views and nonabelian coherence

Groups need not commute. Cocycle labels obey a transported multiplication law.
The associated twisted set-valued system and its sections are constructed from
these labels. No site, stackification or higher category is asserted here.
-/
universe u v w
namespace KomorebiSpace
open CategoryTheory

structure GroupViewSystem (V : Type u) [Category.{v} V]
    (G : V → Type w) [∀ a, Group (G a)] where
  pull : {a b : V} → (a ⟶ b) → (G b →* G a)
  pull_id : ∀ a (x : G a), pull (𝟙 a) x = x
  pull_comp : ∀ {a b c : V} (f : a ⟶ b) (g : b ⟶ c) (x : G c),
    pull (f ≫ g) x = pull f (pull g x)

namespace GroupViewSystem
variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem V G)

/-- Underlying strict set-valued view system. -/
abbrev views : ViewSystem V where
  Obj := G
  pull := fun f => F.pull f
  pull_id := F.pull_id
  pull_comp := F.pull_comp

/-- Multiplicative transition data, including normalization and all composable pairs. -/
structure Cocycle where
  edge : ∀ {a b : V}, (a ⟶ b) → G a
  edge_id : ∀ a, edge (𝟙 a) = 1
  edge_comp : ∀ {a b c : V} (f : a ⟶ b) (g : b ⟶ c),
    edge (f ≫ g) = edge f * F.pull f (edge g)

namespace Cocycle
variable {F}
@[ext] theorem ext {c d : F.Cocycle}
    (h : ∀ a b (f : a ⟶ b), c.edge f = d.edge f) : c = d := by
  cases c with
  | mk ce ci cc =>
    cases d with
    | mk de di dc =>
      have he : @ce = @de := by funext a b f; exact h a b f
      cases he
      rfl
end Cocycle

/-- Trivial transition labels, not an assumed preferred trivialization. -/
def trivial : F.Cocycle where
  edge := fun _ => 1
  edge_id := by intros; rfl
  edge_comp := by intros; simp

/-- A raw viewwise change of trivialization acts on a cocycle. -/
def gauge (a : ∀ v, G v) (c : F.Cocycle) : F.Cocycle where
  edge := fun {v w} f => a v * c.edge f * (F.pull f (a w))⁻¹
  edge_id := by intro v; rw [c.edge_id, F.pull_id]; simp
  edge_comp := by
    intro v w z f g
    simp only [c.edge_comp, F.pull_comp, map_mul, map_inv]
    group

@[simp] theorem gauge_edge (a : ∀ v, G v) (c : F.Cocycle)
    {v w : V} (f : v ⟶ w) :
    (F.gauge a c).edge f = a v * c.edge f * (F.pull f (a w))⁻¹ := rfl

@[simp] theorem gauge_one (c : F.Cocycle) : F.gauge 1 c = c := by
  apply Cocycle.ext
  intro v w f
  simp [gauge]

theorem gauge_mul (a b : ∀ v, G v) (c : F.Cocycle) :
    F.gauge a (F.gauge b c) = F.gauge (a * b) c := by
  apply Cocycle.ext
  intro v w f
  simp only [gauge_edge, Pi.mul_apply, map_mul]
  group

@[simp] theorem gauge_inv_gauge (a : ∀ v, G v) (c : F.Cocycle) :
    F.gauge a⁻¹ (F.gauge a c) = c := by rw [F.gauge_mul]; simp

@[simp] theorem gauge_gauge_inv (a : ∀ v, G v) (c : F.Cocycle) :
    F.gauge a (F.gauge a⁻¹ c) = c := by rw [F.gauge_mul]; simp

/-- The cocycle is used in the restriction functions, not hidden in a truth flag. -/
abbrev twistedViews (c : F.Cocycle) : ViewSystem V where
  Obj := G
  pull := fun f x => c.edge f * F.pull f x
  pull_id := by intro v x; rw [c.edge_id, F.pull_id, one_mul]
  pull_comp := by
    intro v w z f g x
    simp only [c.edge_comp, F.pull_comp, map_mul, mul_assoc]

@[simp] theorem twisted_pull (c : F.Cocycle) {v w : V} (f : v ⟶ w) (x : G w) :
    (F.twistedViews c).pull f x = c.edge f * F.pull f x := rfl

theorem twisted_coherent_iff (c : F.Cocycle) (x : ∀ v, G v) :
    (∀ v w (f : v ⟶ w), (F.twistedViews c).pull f (x w) = x v) ↔
      ∀ v w (f : v ⟶ w), c.edge f = x v * (F.pull f (x w))⁻¹ := by
  constructor
  · intro h v w f
    have he := h v w f
    change c.edge f * F.pull f (x w) = x v at he
    exact (eq_mul_inv_iff_mul_eq).mpr he
  · intro h v w f
    change c.edge f * F.pull f (x w) = x v
    rw [h v w f]
    group

/-- An invertible coordinate change induces an equivalence of actual section sets. -/
def gaugeSections (a : ∀ v, G v) (c : F.Cocycle) :
    (F.twistedViews c).Ambient ≃ (F.twistedViews (F.gauge a c)).Ambient where
  toFun x := ⟨fun v => a v * x.val v, by
    intro v w f
    change (a v * c.edge f * (F.pull f (a w))⁻¹) *
      F.pull f (a w * x.val w) = a v * x.val v
    rw [map_mul]
    have hx := x.property v w f
    change c.edge f * F.pull f (x.val w) = x.val v at hx
    calc
      _ = a v * (c.edge f * F.pull f (x.val w)) := by group
      _ = _ := by rw [hx]⟩
  invFun y := ⟨fun v => (a v)⁻¹ * y.val v, by
    intro v w f
    change c.edge f * F.pull f ((a w)⁻¹ * y.val w) = (a v)⁻¹ * y.val v
    have hy := y.property v w f
    change (a v * c.edge f * (F.pull f (a w))⁻¹) *
      F.pull f (y.val w) = y.val v at hy
    rw [map_mul, map_inv]
    calc
      _ = (a v)⁻¹ * ((a v * c.edge f * (F.pull f (a w))⁻¹) *
        F.pull f (y.val w)) := by group
      _ = _ := by rw [hy]⟩
  left_inv x := by apply ViewSystem.Ambient.ext; intro v; change _⁻¹ * (_ * _) = _; group
  right_inv x := by apply ViewSystem.Ambient.ext; intro v; change _ * (_⁻¹ * _) = _; group

@[simp] theorem gaugeSections_coordinate (a : ∀ v, G v) (c : F.Cocycle)
    (x : (F.twistedViews c).Ambient) (v : V) :
    ((F.gaugeSections a c) x).val v = a v * x.val v := rfl

/-- Flattening labels and solving the twisted section equations are equivalent. -/
theorem flatten_iff_section (a : ∀ v, G v) (c : F.Cocycle) :
    F.gauge a c = F.trivial ↔
      ∀ v w (f : v ⟶ w), c.edge f * F.pull f ((a w)⁻¹) = (a v)⁻¹ := by
  constructor
  · intro h v w f
    have he := congrArg (fun t : F.Cocycle => t.edge f) h
    change a v * c.edge f * (F.pull f (a w))⁻¹ = 1 at he
    rw [map_inv]
    calc
      _ = (a v)⁻¹ * (a v * c.edge f * (F.pull f (a w))⁻¹) := by group
      _ = _ := by rw [he, mul_one]
  · intro h
    apply Cocycle.ext
    intro v w f
    change a v * c.edge f * (F.pull f (a w))⁻¹ = 1
    have he := h v w f
    rw [map_inv] at he
    calc
      _ = a v * (c.edge f * (F.pull f (a w))⁻¹) := by group
      _ = _ := by rw [he]; group

end GroupViewSystem
end KomorebiSpace
