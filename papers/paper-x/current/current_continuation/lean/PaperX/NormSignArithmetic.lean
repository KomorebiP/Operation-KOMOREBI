import PaperX.NormSignFormula
import PaperX.NormSignGeometry
import Mathlib.NumberTheory.NumberField.Norm

/-! The geometric real-coordinate sign is exactly the sign of the actual field
norm and of the integral norm on the ring of integers. -/
set_option autoImplicit false
noncomputable section

namespace PaperX.NormSignArithmetic
open NumberField NumberField.InfinitePlace NumberField.mixedEmbedding
open NormSignGeometry
open scoped Classical
variable (K : Type*) [Field K] [NumberField K]

theorem field_norm_pos_iff {x : K} (hx : x ≠ 0) :
    (0 : ℝ) < Algebra.norm ℚ x ↔ 0 < realProduct K (mixedEmbedding K x) := by
  rw [field_norm_eq_real_mul_complex]
  exact mul_pos_iff_of_pos_right (complex_factor_pos K hx)

theorem field_norm_neg_iff {x : K} (hx : x ≠ 0) :
    (Algebra.norm ℚ x : ℝ) < 0 ↔ realProduct K (mixedEmbedding K x) < 0 := by
  rw [field_norm_eq_real_mul_complex]
  have hp := complex_factor_pos K hx
  unfold realProduct
  constructor
  · intro h
    nlinarith
  · intro h
    exact mul_neg_of_neg_of_pos h hp

theorem integer_norm_pos_iff {x : 𝓞 K} (hx : x ≠ 0) :
    0 < Algebra.norm ℤ x ↔ 0 < realProduct K (mixedEmbedding K (x : K)) := by
  have hn : (x : K) ≠ 0 := by exact_mod_cast hx
  have he : (Algebra.norm ℚ (x : K) : ℝ) = (Algebra.norm ℤ x : ℝ) := by
    rw [← Algebra.coe_norm_int, Rat.cast_intCast]
  rw [← Int.cast_pos (R := ℝ), ← he]
  exact field_norm_pos_iff K hn

theorem integer_norm_neg_iff {x : 𝓞 K} (hx : x ≠ 0) :
    Algebra.norm ℤ x < 0 ↔ realProduct K (mixedEmbedding K (x : K)) < 0 := by
  have hn : (x : K) ≠ 0 := by exact_mod_cast hx
  have he : (Algebra.norm ℚ (x : K) : ℝ) = (Algebra.norm ℤ x : ℝ) := by
    rw [← Algebra.coe_norm_int, Rat.cast_intCast]
  rw [← Int.cast_lt_zero (R := ℝ), ← he]
  exact field_norm_neg_iff K hn

/-- No sign assumption is added: membership in the actual positive cone forces
the integral norm to be positive. -/
theorem integer_norm_pos_of_mem_signCone {x : 𝓞 K}
    (hx : mixedEmbedding K (x : K) ∈ signCone K true) : 0 < Algebra.norm ℤ x := by
  have hne : x ≠ 0 := by
    intro he
    subst x
    have hp := fundamentalCone.normAtPlace_pos_of_mem hx.1.1
      (Classical.arbitrary (InfinitePlace K))
    simp at hp
  exact (integer_norm_pos_iff K hne).mpr hx.2

theorem integer_norm_neg_of_mem_signCone {x : 𝓞 K}
    (hx : mixedEmbedding K (x : K) ∈ signCone K false) : Algebra.norm ℤ x < 0 := by
  have hne : x ≠ 0 := by
    intro he
    subst x
    have hp := fundamentalCone.normAtPlace_pos_of_mem hx.1.1
      (Classical.arbitrary (InfinitePlace K))
    simp at hp
  exact (integer_norm_neg_iff K hne).mpr (neg_pos.mp hx.2)

end PaperX.NormSignArithmetic
