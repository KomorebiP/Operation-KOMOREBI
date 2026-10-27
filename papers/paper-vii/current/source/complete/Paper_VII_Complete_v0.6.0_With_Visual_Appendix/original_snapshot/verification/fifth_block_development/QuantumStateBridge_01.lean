module
public import KnillLaflammeNecessity
import all KnillLaflammeNecessity
import all KnillLaflammeSufficiency
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII fifth block.
State-space versus operator-space exact correction: polarization and normalization.
-/
public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
namespace KomorebiPaperVII.KnillLaflamme
open scoped BigOperators ComplexOrder
open Matrix
variable {n : Type*} [Fintype n] [DecidableEq n]

def pure (x : n → ℂ) : Matrix n n ℂ := Matrix.vecMulVec x (star x)

theorem outer_polarization (x y : n → ℂ) :
    (4 : ℂ) • Matrix.vecMulVec x (star y) =
      pure (x+y) - pure (x-y) + Complex.I • (pure (x+Complex.I • y) - pure (x-Complex.I • y)) := by
  ext i j
  simp [pure, Matrix.vecMulVec, star_add, star_sub, star_smul, Complex.star_def]
  ring_nf
  simp [Complex.I_sq]

theorem linearMap_eq_of_pure (f g : Matrix n n ℂ →ₗ[ℂ] Matrix n n ℂ)
    (h : ∀ x, f (pure x)=g (pure x)) : f=g := by
  have outer (x y : n → ℂ) : f (Matrix.vecMulVec x (star y))=g (Matrix.vecMulVec x (star y)) := by
    apply (smul_right_injective (M := Matrix n n ℂ) (by norm_num : (4 : ℂ) ≠ 0))
    rw [← map_smul, ← map_smul, outer_polarization]
    simp only [map_add, map_sub, map_smul, h]
  have single (i j : n) (c : ℂ) : f (Matrix.single i j c)=g (Matrix.single i j c) := by
    have hh := outer (Pi.single i c) (Pi.single j 1)
    simpa [Matrix.vecMulVec, pure, Matrix.single_apply, Pi.single_apply, apply_ite, ite_and] using hh
  ext rho i j
  have heq : f rho=g rho := by
    conv_lhs => rw [Matrix.matrix_eq_sum_single rho]
    conv_rhs => rw [Matrix.matrix_eq_sum_single rho]
    simp only [map_sum, single]
  exact congrArg (fun M : Matrix n n ℂ => M i j) heq

end KomorebiPaperVII.KnillLaflamme
