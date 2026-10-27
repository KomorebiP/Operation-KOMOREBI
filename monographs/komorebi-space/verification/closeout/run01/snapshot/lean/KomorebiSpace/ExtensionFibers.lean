import KomorebiSpace.Correction
import Mathlib.Tactic.Abel

set_option autoImplicit false

/-!
# All exact lifts of prescribed observations

A nonempty exact fiber is parametrized by the homogeneous solutions.
Choosing one lift supplies coordinates, not a preferred lift.
-/
universe u v w
namespace KomorebiSpace
namespace CorrectionProblem
variable {E : Type u} {R : Type v} {S : Type w}
variable [AddCommGroup E] [AddCommGroup R] [AddCommGroup S]
variable (P : CorrectionProblem E R S)

/-- Exact changes that leave all protected observations fixed. -/
def homogeneous : AddSubgroup E := P.residual.ker ⊓ P.semantics.ker

@[simp] theorem mem_homogeneous (x : E) :
    x ∈ P.homogeneous ↔ P.residual x = 0 ∧ P.semantics x = 0 := Iff.rfl

/-- This fiber is defined for arbitrary prescribed observations, not only liftable ones. -/
def ExactFiber (s : S) := {x : E // P.residual x = 0 ∧ P.semantics x = s}

@[ext] theorem ExactFiber.ext {s : S} {x y : P.ExactFiber s}
    (h : x.val = y.val) : x = y := Subtype.ext h

/-- Translation by a homogeneous solution preserves the exact fiber. -/
def translateFiber {s : S} (h : P.homogeneous) (x : P.ExactFiber s) : P.ExactFiber s :=
  ⟨x.val + h.val, by
    constructor
    · rw [map_add, x.property.1, h.property.1, add_zero]
    · rw [map_add, x.property.2, h.property.2, add_zero]⟩

@[simp] theorem translateFiber_val {s : S} (h : P.homogeneous) (x : P.ExactFiber s) :
    (P.translateFiber h x).val = x.val + h.val := rfl

@[simp] theorem translateFiber_zero {s : S} (x : P.ExactFiber s) :
    P.translateFiber 0 x = x := by
  apply Subtype.ext
  exact add_zero _

theorem translateFiber_add {s : S} (h k : P.homogeneous) (x : P.ExactFiber s) :
    P.translateFiber (h + k) x = P.translateFiber k (P.translateFiber h x) := by
  apply Subtype.ext
  exact (add_assoc _ _ _).symm

/-- Difference of two exact lifts with the same observations. -/
def fiberDifference {s : S} (x y : P.ExactFiber s) : P.homogeneous :=
  ⟨x.val - y.val, by
    change P.residual (x.val - y.val) = 0 ∧ P.semantics (x.val - y.val) = 0
    constructor
    · rw [map_sub, x.property.1, y.property.1, sub_self]
    · rw [map_sub, x.property.2, y.property.2, sub_self]⟩

@[simp] theorem fiberDifference_val {s : S} (x y : P.ExactFiber s) :
    (P.fiberDifference x y).val = x.val - y.val := rfl

@[simp] theorem translate_difference {s : S} (x y : P.ExactFiber s) :
    P.translateFiber (P.fiberDifference x y) y = x := by
  apply Subtype.ext
  change y.val + (x.val - y.val) = x.val
  abel

/-- The action is simply transitive whenever the fiber is nonempty. -/
theorem exists_unique_translation {s : S} (x y : P.ExactFiber s) :
    ∃! h : P.homogeneous, P.translateFiber h x = y := by
  refine ⟨P.fiberDifference y x, P.translate_difference y x, ?_⟩
  intro h hh
  apply Subtype.ext
  have he := congrArg Subtype.val hh
  change x.val + h.val = y.val at he
  change h.val = y.val - x.val
  rw [← he]
  abel

/-- Coordinates on the fiber require a supplied base solution. -/
def fiberParameters {s : S} (base : P.ExactFiber s) : P.homogeneous ≃ P.ExactFiber s where
  toFun h := P.translateFiber h base
  invFun x := P.fiberDifference x base
  left_inv h := by
    apply Subtype.ext
    change base.val + h.val - base.val = h.val
    abel
  right_inv x := P.translate_difference x base

@[simp] theorem fiberParameters_apply {s : S} (base : P.ExactFiber s) (h : P.homogeneous) :
    (P.fiberParameters base h).val = base.val + h.val := rfl

/-- Uniqueness, separately from existence, is exactly vanishing homogeneous freedom. -/
theorem fiber_subsingleton_iff {s : S} (base : P.ExactFiber s) :
    Subsingleton (P.ExactFiber s) ↔ P.homogeneous = ⊥ := by
  constructor
  · intro hsub
    apply le_antisymm
    · intro x hx
      change x = 0
      have he : P.translateFiber ⟨x,hx⟩ base = base := hsub.elim _ _
      have hv := congrArg Subtype.val he
      change base.val + x = base.val at hv
      exact add_left_cancel (hv.trans (add_zero base.val).symm)
    · exact bot_le
  · intro hz
    refine ⟨fun x y => ?_⟩
    apply Subtype.ext
    have hm : x.val - y.val ∈ P.homogeneous := (P.fiberDifference x y).property
    rw [hz] at hm
    change x.val - y.val = 0 at hm
    exact sub_eq_zero.mp hm

/-- The old obstruction criterion now records existence of the whole fiber. -/
theorem obstruction_zero_iff_fiber (x : E) :
    P.obstruction x = 0 ↔ Nonempty (P.ExactFiber (P.semantics x)) := by
  rw [P.flatten_iff]
  constructor
  · rintro ⟨y,hd,hp⟩
    exact ⟨⟨y,hd,hp⟩⟩
  · rintro ⟨⟨y,hd,hp⟩⟩
    exact ⟨y,hd,hp⟩

/-- Changing the base solution changes coordinates by a translation. -/
theorem change_base {s : S} (x y : P.ExactFiber s) (h : P.homogeneous) :
    (P.fiberParameters y).symm (P.fiberParameters x h) =
      h + P.fiberDifference x y := by
  apply Subtype.ext
  change x.val + h.val - y.val = h.val + (x.val - y.val)
  abel

end CorrectionProblem
end KomorebiSpace
