import KomorebiSpace.ViewSections
import KomorebiSpace.Correction
import Mathlib.Algebra.Group.Pi.Basic
import Mathlib.Tactic.Abel

set_option autoImplicit false

/-!
# An actual obstruction to extending a partial additive section

The defect compares transported data to the chosen data at every arrow.
Allowed corrections vanish on the prescribed view domain. The quotient by
these allowed defects is independent of a raw extension, and its vanishing
is equivalent to existence of a genuinely coherent extension.
-/
universe u v w
namespace KomorebiSpace
open CategoryTheory

structure AdditiveViewSystem (V : Type u) [Category.{v} V]
    (A : V → Type w) [∀ a, AddCommGroup (A a)] where
  pull : {a b : V} → (a ⟶ b) → (A b →+ A a)
  pull_id : ∀ a (x : A a), pull (𝟙 a) x = x
  pull_comp : ∀ {a b c : V} (f : a ⟶ b) (g : b ⟶ c) (x : A c),
    pull (f ≫ g) x = pull f (pull g x)

namespace AdditiveViewSystem
variable {V : Type u} [Category.{v} V]
variable {A : V → Type w} [∀ a, AddCommGroup (A a)]
variable (F : AdditiveViewSystem V A)

def views : ViewSystem V where
  Obj := A
  pull := fun f => F.pull f
  pull_id := F.pull_id
  pull_comp := F.pull_comp

/-- Arrow-indexed additive compatibility defects. -/
abbrev Residual := ∀ a b : V, (a ⟶ b) → A a

def differential : (∀ a, A a) →+ Residual (V := V) (A := A) where
  toFun x := fun a b f => F.pull f (x b) - x a
  map_zero' := by funext a b f; simp
  map_add' := by
    intro x y
    funext a b f
    simp only [Pi.add_apply, map_add]
    abel

@[simp] theorem differential_apply (x : ∀ a, A a) (a b : V) (f : a ⟶ b) :
    F.differential x a b f = F.pull f (x b) - x a := rfl

@[simp] theorem differential_id (x : ∀ a, A a) (a : V) :
    F.differential x a a (𝟙 a) = 0 := by
  rw [differential_apply, F.pull_id, sub_self]

/-- The actual defects obey the transported additive cocycle identity. -/
theorem differential_comp (x : ∀ a, A a) {a b c : V} (f : a ⟶ b) (g : b ⟶ c) :
    F.differential x a c (f ≫ g) =
      F.pull f (F.differential x b c g) + F.differential x a b f := by
  simp only [differential_apply, F.pull_comp, map_sub]
  abel

theorem differential_zero_iff (x : ∀ a, A a) :
    F.differential x = 0 ↔ ∀ a b (f : a ⟶ b), F.pull f (x b) = x a := by
  constructor
  · intro h a b f
    exact sub_eq_zero.mp (congrFun (congrFun (congrFun h a) b) f)
  · intro h
    funext a b f
    exact sub_eq_zero.mpr (h a b f)

/-- The prescribed observations, without declaring them complete semantics. -/
def observation (_F : AdditiveViewSystem V A) (U : Set V) :
    (∀ a, A a) →+ (∀ a : U, A a.val) where
  toFun x := fun a => x a.val
  map_zero' := rfl
  map_add' := by intros; rfl

def problem (U : Set V) :
    CorrectionProblem (∀ a, A a) (Residual (V := V) (A := A)) (∀ a : U, A a.val) where
  residual := F.differential
  semantics := F.observation U

/-- The old constrained-correction theorem now applies to actual view coherence. -/
theorem obstruction_zero_iff_section (U : Set V) (x : ∀ a, A a) :
    (F.problem U).obstruction x = 0 ↔
      ∃ s : F.views.Ambient, ∀ a : U, s.val a.val = x a.val := by
  rw [(F.problem U).flatten_iff]
  constructor
  · rintro ⟨y, hy, hp⟩
    refine ⟨⟨y, (F.differential_zero_iff y).mp hy⟩, ?_⟩
    intro a
    exact congrFun hp a
  · rintro ⟨s, hs⟩
    refine ⟨s.val, (F.differential_zero_iff s.val).mpr s.property, ?_⟩
    exact funext hs

/-- Equal prescribed data give the same obstruction, independent of raw extension. -/
theorem obstruction_same_observation (U : Set V) (x y : ∀ a, A a)
    (h : F.observation U x = F.observation U y) :
    (F.problem U).obstruction x = (F.problem U).obstruction y := by
  have hz : (F.problem U).semantics (x - y) = 0 := by
    change F.observation U (x - y) = 0
    rw [map_sub, h, sub_self]
  have he := (F.problem U).obstruction_invariant x (x - y) hz
  have hxy : x - (x - y) = y := by abel
  rw [hxy] at he
  exact he.symm

/-- Zero outside the prescribed domain is one raw extension, not a coherent one. -/
noncomputable def rawExtension (U : Set V) (s : F.views.Partial U) : ∀ a, A a :=
  by
  classical
  exact fun a => if h : a ∈ U then s.val ⟨a, h⟩ else 0

@[simp] theorem rawExtension_observed (U : Set V) (s : F.views.Partial U) (a : U) :
    F.rawExtension U s a.val = s.val a := by
  rcases a with ⟨a, ha⟩
  exact dite_eq_left ha

/-- An explicitly presented quotient class, not a flag defined by solvability. -/
noncomputable def extensionClass (U : Set V) (s : F.views.Partial U) :
    (F.problem U).Obstruction := (F.problem U).obstruction (F.rawExtension U s)

theorem extensionClass_zero_iff (U : Set V) (s : F.views.Partial U) :
    F.extensionClass U s = 0 ↔ Nonempty (F.views.Extensions U s) := by
  change (F.problem U).obstruction (F.rawExtension U s) = 0 ↔ _
  rw [F.obstruction_zero_iff_section]
  constructor
  · rintro ⟨x, hx⟩
    refine ⟨⟨x, ?_⟩⟩
    apply ViewSystem.Partial.ext
    intro a
    exact (hx a).trans (F.rawExtension_observed U s a)
  · rintro ⟨⟨x, hx⟩⟩
    refine ⟨x, ?_⟩
    intro a
    have he := congrArg (fun y : F.views.Partial U => y.val a) hx
    exact he.trans (F.rawExtension_observed U s a).symm

theorem extensionClass_independent (U : Set V) (s : F.views.Partial U)
    (x : ∀ a, A a) (hx : ∀ a : U, x a.val = s.val a) :
    (F.problem U).obstruction x = F.extensionClass U s := by
  apply F.obstruction_same_observation
  funext a
  exact (hx a).trans (F.rawExtension_observed U s a).symm

end AdditiveViewSystem
end KomorebiSpace
