module
public import KnillLaflammeSufficiency
import all KnillLaflammeSufficiency
public import Mathlib.LinearAlgebra.Matrix.Single
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII fifth block.
Necessity via a rank-one Gram rigidity argument on actual finite Kraus maps.
-/
public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
namespace KomorebiPaperVII.KnillLaflamme
open scoped BigOperators ComplexOrder
open Matrix

/-- Every row of a matrix with a rank-one Gram matrix is proportional to its generator. -/
theorem rank_one_gram_rigidity {q J : Type*} [Fintype q] [DecidableEq q]
    [Fintype J] [DecidableEq J] (A : Matrix J q ℂ) (p : q → ℂ)
    (hgram : star A*A = Matrix.vecMulVec (star p) p) :
    ∃ z : J → ℂ, ∀ j t, A j t = z j*p t := by
  by_cases hp : p=0
  · have hA : A=0 := Matrix.conjTranspose_mul_self_eq_zero.mp (by simpa [hp] using hgram)
    exact ⟨fun _ => 0, by simp [hA]⟩
  · obtain ⟨t,ht⟩ : ∃ t, p t ≠ 0 := Function.ne_iff.mp hp
    refine ⟨fun j => A j t / p t, ?_⟩
    intro j s
    let v : q → ℂ := Pi.single s (p t) - Pi.single t (p s)
    have hpv : p ⬝ᵥ v = 0 := by
      simp [v, dotProduct_sub, dotProduct_single, mul_comm]
    have hav : A *ᵥ v=0 := by
      apply (Matrix.conjTranspose_mul_self_mulVec_eq_zero A v).mp
      rw [hgram]
      ext u
      simp [Matrix.mulVec, dotProduct, Matrix.vecMulVec, ← Finset.mul_sum, ← dotProduct, hpv]
    have heq : A j s*p t - A j t*p s=0 := by
      simpa [v, Matrix.mulVec_sub, Matrix.mulVec_single] using congrFun hav j
    apply (eq_div_iff ht).mp
    field_simp
    linear_combination heq

end KomorebiPaperVII.KnillLaflamme
