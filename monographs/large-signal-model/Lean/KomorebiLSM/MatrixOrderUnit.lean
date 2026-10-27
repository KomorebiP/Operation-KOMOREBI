import Mathlib.Analysis.Matrix.Order
import Mathlib.Analysis.CStarAlgebra.ContinuousFunctionalCalculus.Order
import Mathlib.Algebra.Order.Star.Real
import Mathlib.Tactic

/-! A positive definite finite real matrix is an order unit for the full
symmetric matrix space. The bound is derived from its positive spectrum. -/
set_option autoImplicit false
namespace Komorebi.LSM.MatrixOrderUnit
open scoped Matrix MatrixOrder Matrix.Norms.L2Operator

/-- No order-unit hypothesis is assumed: positive definiteness supplies a
strict scalar lower bound, which dominates any symmetric perturbation. -/
theorem exists_nonnegative_bound {D : Type*} [Fintype D] [DecidableEq D]
    (A X : Matrix D D ℝ) (hA : A.PosDef) (hX : X.IsHermitian) :
    ∃ a : ℝ, 0 ≤ a ∧ (a • A + X).PosSemidef ∧ (a • A - X).PosSemidef := by
  rcases isEmpty_or_nonempty D with hD | hD
  · let := hD
    refine ⟨0,le_rfl,?_,?_⟩
    all_goals
      convert (Matrix.PosSemidef.zero : (0 : Matrix D D ℝ).PosSemidef) using 1
      exact Subsingleton.elim _ _
  · let := hD
    have hsa : IsSelfAdjoint A := hA.isHermitian
    have hxsa : IsSelfAdjoint X := hX
    obtain ⟨r,hr,hrA⟩ := (CFC.exists_pos_algebraMap_le_iff A hsa).mpr
      (fun x hx => hA.isStrictlyPositive.spectrum_pos hx)
    have ha : 0 ≤ ‖X‖/r := div_nonneg (norm_nonneg X) hr.le
    have hsmall := Matrix.PosSemidef.smul (Matrix.le_iff.mp hrA) ha
    rw [smul_sub,Algebra.algebraMap_eq_smul_one,smul_smul,div_mul_cancel₀ _ hr.ne'] at hsmall
    have upper (Y : Matrix D D ℝ) (hY : IsSelfAdjoint Y) :
        Y ≤ algebraMap ℝ (Matrix D D ℝ) ‖Y‖ := by
      apply (le_algebraMap_iff_spectrum_le hY).mpr
      intro t ht
      exact (Real.le_norm_self t).trans (spectrum.norm_le_norm_of_mem ht)
    have hup : (‖X‖ • (1 : Matrix D D ℝ)-X).PosSemidef := by
      simpa only [Algebra.algebraMap_eq_smul_one] using Matrix.le_iff.mp (upper X hxsa)
    have hdown : (‖X‖ • (1 : Matrix D D ℝ)+X).PosSemidef := by
      simpa only [norm_neg,Algebra.algebraMap_eq_smul_one,sub_neg_eq_add] using
        Matrix.le_iff.mp (upper (-X) hxsa.neg)
    refine ⟨‖X‖/r,ha,?_,?_⟩
    · have he : (‖X‖/r) • A+X=
          ((‖X‖/r) • A-‖X‖ • (1 : Matrix D D ℝ))+(‖X‖ • (1 : Matrix D D ℝ)+X) := by abel
      rw [he]
      exact hsmall.add hdown
    · have he : (‖X‖/r) • A-X=
          ((‖X‖/r) • A-‖X‖ • (1 : Matrix D D ℝ))+(‖X‖ • (1 : Matrix D D ℝ)-X) := by abel
      rw [he]
      exact hsmall.add hup

end Komorebi.LSM.MatrixOrderUnit
