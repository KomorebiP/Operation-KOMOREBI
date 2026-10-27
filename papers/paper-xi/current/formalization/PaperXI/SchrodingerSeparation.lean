import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.Algebra.Group.AddChar
import Mathlib.Basic.Complex.Basic

/-! A nontrivial scalar additive character, composed with the full linear dual,
separates points of a vector space. No finiteness assumption is required. -/
set_option autoImplicit false
noncomputable section

namespace PaperXI.SchrodingerSeparation

variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]

/-- The modulation characters distinguish any two distinct points. -/
theorem exists_dual_character_ne {ψ : AddChar K ℂ} (hψ : ψ ≠ 1)
    {u v : X} (huv : u ≠ v) :
    ∃ ξ : Module.Dual K X, ψ (ξ u) ≠ ψ (ξ v) := by
  obtain ⟨a, ha⟩ := AddChar.ne_one_iff.mp hψ
  obtain ⟨ℓ, hℓ⟩ := Module.Projective.exists_dual_eq_one K (sub_ne_zero.mpr huv)
  let ξ : Module.Dual K X := a • ℓ
  have hξ : ξ (u - v) = a := by
    simp only [ξ, LinearMap.smul_apply, hℓ, smul_eq_mul, mul_one]
  refine ⟨ξ, ?_⟩
  intro h
  apply ha
  calc
    ψ a = ψ (ξ (u - v)) := congrArg ψ hξ.symm
    _ = ψ (ξ u) * ψ (-ξ v) := by rw [map_sub, sub_eq_add_neg, AddChar.map_add_eq_mul]
    _ = ψ (ξ v) * ψ (-ξ v) := by rw [h]
    _ = 1 := by rw [← AddChar.map_add_eq_mul, add_neg_cancel, AddChar.map_zero_eq_one]

end PaperXI.SchrodingerSeparation
