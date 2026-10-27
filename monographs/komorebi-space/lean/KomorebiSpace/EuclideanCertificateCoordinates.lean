import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Analysis.Normed.Module.FiniteDimension
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Ring

set_option autoImplicit false

/-! Explicit Euclidean coordinates for generated exact polynomial certificates.
There is no change from the Euclidean norm to the coordinate maximum norm. -/
noncomputable section
namespace KomorebiSpace
namespace ExactCoordinates
abbrev Space (n : ℕ) := EuclideanSpace ℝ (Fin n)

def linear (n : ℕ) (a : Fin n → Fin n → ℝ) : Space n →ₗ[ℝ] Space n where
  toFun x := WithLp.toLp 2 (fun i => ∑ j, a i j*x j)
  map_add' x y := by
    ext i
    change (∑ j, a i j * (x j+y j))=(∑ j,a i j*x j)+(∑ j,a i j*y j)
    simp only [mul_add, Finset.sum_add_distrib]
  map_smul' c x := by
    ext i
    change (∑ j, a i j*(c*x j))=c*(∑ j,a i j*x j)
    rw [Finset.mul_sum]
    congr 1
    funext j
    ring

def operator (n : ℕ) (a : Fin n → Fin n → ℝ) : Space n →L[ℝ] Space n :=
  (linear n a).toContinuousLinearMap

@[simp] theorem operator_apply (n : ℕ) (a : Fin n → Fin n → ℝ)
    (x : Space n) (i : Fin n) : operator n a x i=∑ j,a i j*x j := rfl

theorem norm_squared (n : ℕ) (x : Space n) : ‖x‖^2=∑ i,(x i)^2 :=
  EuclideanSpace.real_norm_sq_eq x

theorem inner_coordinates (n : ℕ) (x y : Space n) :
    inner ℝ x y=∑ i,x i*y i := by
  simp [PiLp.inner_apply, mul_comm]

end ExactCoordinates
end KomorebiSpace
end
