import PaperXI.DyadicAffine
import PaperXI.DyadicGauss
import Mathlib.LinearAlgebra.Pi

/-! Every quadratic refinement in symplectic coordinates has unique linear
coefficients. This identifies all refinements, not only a chosen family. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DyadicCoordinates
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine

variable {ι : Type*} [Fintype ι]

def symplectic : (ι → F2 × F2) →ₗ[F2] (ι → F2 × F2) →ₗ[F2] F2 where
  toFun x :=
    { toFun := fun y => ∑ i, ((x i).1 * (y i).2 + (x i).2 * (y i).1)
      map_add' := by
        intro y z
        simp only [Pi.add_apply, Prod.fst_add, Prod.snd_add]
        rw [← Finset.sum_add_distrib]
        apply Finset.sum_congr rfl
        intro i hi
        ring
      map_smul' := by
        intro r y
        change (∑ i, ((x i).1 * (r * (y i).2) + (x i).2 * (r * (y i).1))) =
          r * (∑ i, ((x i).1 * (y i).2 + (x i).2 * (y i).1))
        rw [Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro i hi
        ring }
  map_add' := by
    intro x z
    apply LinearMap.ext
    intro y
    change (∑ i, (((x + z) i).1 * (y i).2 + ((x + z) i).2 * (y i).1)) =
      (∑ i, ((x i).1 * (y i).2 + (x i).2 * (y i).1)) +
      (∑ i, ((z i).1 * (y i).2 + (z i).2 * (y i).1))
    rw [← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro i hi
    simp only [Pi.add_apply, Prod.fst_add, Prod.snd_add]
    ring
  map_smul' := by
    intro r x
    apply LinearMap.ext
    intro y
    change (∑ i, ((r * (x i).1) * (y i).2 + (r * (x i).2) * (y i).1)) =
      r * (∑ i, ((x i).1 * (y i).2 + (x i).2 * (y i).1))
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i hi
    ring

@[simp] theorem symplectic_apply (x y : ι → F2 × F2) :
    symplectic x y = ∑ i, ((x i).1 * (y i).2 + (x i).2 * (y i).1) := rfl

theorem quadratic_polar (a x y : ι → F2 × F2) :
    quadratic a (x + y) = quadratic a x + quadratic a y + symplectic x y := by
  simp only [quadratic, plane, Pi.add_apply, Prod.fst_add, Prod.snd_add,
    symplectic_apply, ← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro i hi
  ring

def coordinateRefinement (a : ι → F2 × F2) : Refinement (symplectic (ι := ι)) where
  value := quadratic a
  polar := quadratic_polar a

def firstAxis (i : ι) : ι → F2 × F2 := Pi.single i (1, 0)
def secondAxis (i : ι) : ι → F2 × F2 := Pi.single i (0, 1)

omit [Fintype ι] in
theorem single_axes (i : ι) (z : F2 × F2) :
    Pi.single i z = z.1 • firstAxis i + z.2 • secondAxis i := by
  ext j <;> by_cases h : j = i <;> simp [firstAxis, secondAxis, h]

def linearCoefficients (l : (ι → F2 × F2) →ₗ[F2] F2) : ι → F2 × F2 :=
  fun i => (l (firstAxis i), l (secondAxis i))

theorem linear_coordinate_formula (l : (ι → F2 × F2) →ₗ[F2] F2)
    (x : ι → F2 × F2) :
    l x = ∑ i, ((linearCoefficients l i).1 * (x i).1 +
      (linearCoefficients l i).2 * (x i).2) := by
  conv_lhs => rw [← Finset.univ_sum_single x]
  rw [map_sum]
  apply Finset.sum_congr rfl
  intro i hi
  rw [single_axes, map_add, map_smul, map_smul]
  simp [linearCoefficients, mul_comm]

@[simp] theorem quadratic_firstAxis (a : ι → F2 × F2) (i : ι) :
    quadratic a (firstAxis i) = (a i).1 := by
  unfold quadratic
  rw [Finset.sum_eq_single i]
  · simp [plane, firstAxis]
  · intro j hj hji
    simp [plane, firstAxis, Pi.single_eq_of_ne hji]
  · simp

@[simp] theorem quadratic_secondAxis (a : ι → F2 × F2) (i : ι) :
    quadratic a (secondAxis i) = (a i).2 := by
  unfold quadratic
  rw [Finset.sum_eq_single i]
  · simp [plane, secondAxis]
  · intro j hj hji
    simp [plane, secondAxis, Pi.single_eq_of_ne hji]
  · simp

def refinementCoefficients (q : Refinement (symplectic (ι := ι))) : ι → F2 × F2 :=
  linearCoefficients (linearDifference q (coordinateRefinement 0))

theorem refinement_coordinate_formula (q : Refinement (symplectic (ι := ι)))
    (x : ι → F2 × F2) : q.value x = quadratic (refinementCoefficients q) x := by
  have h := linear_coordinate_formula (linearDifference q (coordinateRefinement 0)) x
  simp only [linearDifference_apply, coordinateRefinement] at h
  dsimp only [refinementCoefficients]
  simp only [quadratic, plane, Pi.zero_apply, Prod.fst_zero, Prod.snd_zero,
    zero_mul, add_zero] at h ⊢
  simp only [Finset.sum_add_distrib] at h ⊢
  dsimp only [coordinateRefinement] at h ⊢
  linear_combination h

@[simp] theorem refinementCoefficients_coordinateRefinement (a : ι → F2 × F2) :
    refinementCoefficients (coordinateRefinement a) = a := by
  ext i <;> simp [refinementCoefficients, linearCoefficients, coordinateRefinement]

/-- Complete parameterization of all refinements in symplectic coordinates. -/
def coordinateEquiv : (ι → F2 × F2) ≃ Refinement (symplectic (ι := ι)) where
  toFun := coordinateRefinement
  invFun := refinementCoefficients
  left_inv := refinementCoefficients_coordinateRefinement
  right_inv q := by
    ext x
    exact (refinement_coordinate_formula q x).symm

@[simp] theorem refinementCoefficients_apply
    (q : Refinement (symplectic (ι := ι))) (i : ι) :
    refinementCoefficients q i = (q.value (firstAxis i), q.value (secondAxis i)) := by
  simp [refinementCoefficients, linearCoefficients, coordinateRefinement]

/-- The coefficient Arf value is precisely the sum of products of values on
the paired symplectic basis vectors. -/
theorem arf_basis_formula (a : ι → F2 × F2) :
    arf a = ∑ i, quadratic a (firstAxis i) * quadratic a (secondAxis i) := by
  simp [arf]

theorem refinement_arf_basis_formula (q : Refinement (symplectic (ι := ι))) :
    arf (refinementCoefficients q) =
      ∑ i, q.value (firstAxis i) * q.value (secondAxis i) := by
  simp [arf]

/-- Gauss evaluation for every actual refinement of the coordinate form. -/
theorem refinement_gauss_sum (q : Refinement (symplectic (ι := ι))) :
    (∑ x, sign (q.value x)) =
      sign (∑ i, q.value (firstAxis i) * q.value (secondAxis i)) *
        2 ^ Fintype.card ι := by
  simp_rw [refinement_coordinate_formula q]
  rw [gauss_sum, arf_basis_formula]

end PaperXI.DyadicCoordinates
