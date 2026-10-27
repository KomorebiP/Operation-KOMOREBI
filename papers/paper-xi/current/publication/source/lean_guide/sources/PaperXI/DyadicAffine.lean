import Mathlib.Algebra.Module.ZMod
import Mathlib.Tactic

/-! Paper XI, Proposition 13.2: the affine space of refinements of a fixed
bilinear form over the field with two elements. No nondegeneracy is required. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DyadicAffine

variable {V : Type*} [AddCommGroup V] [Module (ZMod 2) V]

/-- A quadratic refinement is specified by its actual polar identity. -/
structure Refinement (b : V →ₗ[ZMod 2] V →ₗ[ZMod 2] ZMod 2) where
  value : V → ZMod 2
  polar : ∀ x y, value (x + y) = value x + value y + b x y

variable {b : V →ₗ[ZMod 2] V →ₗ[ZMod 2] ZMod 2}

@[ext] theorem Refinement.ext {q r : Refinement b}
    (h : ∀ x, q.value x = r.value x) : q = r := by
  cases q
  cases r
  simp_all [mk.injEq, funext_iff]

@[simp] theorem Refinement.value_zero (q : Refinement b) : q.value 0 = 0 := by
  have h := q.polar 0 0
  simp only [map_zero, add_zero] at h
  exact (add_eq_left.mp h.symm)

/-- Subtracting two refinements cancels their common polar form. -/
theorem difference_add (q r : Refinement b) (x y : V) :
    q.value (x + y) - r.value (x + y) =
      (q.value x - r.value x) + (q.value y - r.value y) := by
  rw [q.polar, r.polar]
  ring

/-- Additivity over the prime field gives an actual linear functional. -/
def linearDifference (q r : Refinement b) : V →ₗ[ZMod 2] ZMod 2 :=
  ({ toFun := fun x => q.value x - r.value x
     map_zero' := by simp
     map_add' := difference_add q r } : V →+ ZMod 2).toZModLinearMap 2

@[simp] theorem linearDifference_apply (q r : Refinement b) (x : V) :
    linearDifference q r x = q.value x - r.value x := rfl

/-- Every linear functional can be added to a refinement. -/
def addLinear (q : Refinement b) (l : V →ₗ[ZMod 2] ZMod 2) : Refinement b where
  value x := q.value x + l x
  polar x y := by
    rw [q.polar, map_add]
    ring

@[simp] theorem addLinear_apply (q : Refinement b) (l : V →ₗ[ZMod 2] ZMod 2)
    (x : V) : (addLinear q l).value x = q.value x + l x := rfl

@[simp] theorem addLinear_linearDifference (q r : Refinement b) :
    addLinear r (linearDifference q r) = q := by
  ext x
  simp

@[simp] theorem linearDifference_addLinear (q : Refinement b)
    (l : V →ₗ[ZMod 2] ZMod 2) : linearDifference (addLinear q l) q = l := by
  ext x
  simp

/-- Choosing one refinement identifies all refinements with the dual space. -/
def refinementEquiv (q₀ : Refinement b) :
    Refinement b ≃ (V →ₗ[ZMod 2] ZMod 2) where
  toFun q := linearDifference q q₀
  invFun l := addLinear q₀ l
  left_inv := fun q => addLinear_linearDifference q q₀
  right_inv := linearDifference_addLinear q₀

theorem exists_unique_linear_difference (q q₀ : Refinement b) :
    ∃! l : V →ₗ[ZMod 2] ZMod 2, addLinear q₀ l = q := by
  refine ⟨linearDifference q q₀, addLinear_linearDifference q q₀, ?_⟩
  intro l hl
  have h := congrArg (fun r => linearDifference r q₀) hl
  simpa using h

end PaperXI.DyadicAffine
