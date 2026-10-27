import PaperXI.SchrodingerOperator
import Mathlib.NumberTheory.GaussSum
import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic

/-! The literal Schrödinger operators preserve the usual finite sum Hermitian pairing. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SchrodingerUnitary
open scoped Classical

variable {K : Type*} [Field K] [Fintype K]

/-- Finite-field additive characters take values on the unit circle. -/
theorem conjugate_character (ψ : AddChar K ℂ) (a : K) :
    star (ψ a) = ψ (-a) := by
  simpa only [AddChar.inv_apply, starRingEnd_apply] using
    AddChar.starComp_apply (Nat.pos_of_ne_zero (CharP.ringChar_ne_zero_of_finite K)) a

/-- The phase factor contributes one to the Hermitian pairing. -/
theorem conjugate_mul_character (ψ : AddChar K ℂ) (a : K) :
    star (ψ a) * ψ a = 1 := by
  rw [conjugate_character, ← ψ.map_add_eq_mul]
  simp

variable {X : Type*} [AddCommGroup X] [Module K X] [Fintype X]

/-- Every literal Schrödinger operator preserves the finite sum Hermitian pairing. -/
theorem pairing_invariant (ψ : AddChar K ℂ) (x : X) (ξ : X →ₗ[K] K)
    (z : K) (f g : X → ℂ) :
    (∑ u : X, star (Schrodinger.operator ψ x ξ z f u) *
      Schrodinger.operator ψ x ξ z g u) = ∑ u : X, star (f u) * g u := by
  calc
    _ = ∑ u : X, star (f (u + x)) * g (u + x) := by
      apply Finset.sum_congr rfl
      intro u _
      simp only [Schrodinger.operator_apply, star_mul]
      calc
        _ = (star (ψ (z + ξ u + (2 : K)⁻¹ * ξ x)) *
          ψ (z + ξ u + (2 : K)⁻¹ * ξ x)) *
          (star (f (u + x)) * g (u + x)) := by ring
        _ = _ := by rw [conjugate_mul_character, one_mul]
    _ = _ := Fintype.sum_bijective _ (AddGroup.addRight_bijective x) _ _ (fun _ => rfl)

end PaperXI.SchrodingerUnitary
