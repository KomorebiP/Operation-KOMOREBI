import Mathlib.Analysis.InnerProductSpace.Adjoint
import Mathlib.Analysis.CStarAlgebra.Spectrum
import Mathlib.Analysis.CStarAlgebra.ContinuousLinearMap

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000
open scoped ComplexConjugate

namespace ModalResolventTest
variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E] [CompleteSpace E]

theorem shifted_isUnit (A : E →L[ℂ] E) (hA : IsSelfAdjoint A)
    (z : ℂ) (hz : z.im ≠ 0) : IsUnit (A - z • (1 : E →L[ℂ] E)) := by
  have hn : z ∉ spectrum ℂ A := fun h => hz (hA.im_eq_zero_of_mem_spectrum h)
  have hu := spectrum.notMem_iff.mp hn
  simpa only [Algebra.algebraMap_eq_smul_one, neg_sub] using hu.neg

theorem shifted_lower_bound (A : E →L[ℂ] E)
    (hA : (A : E →ₗ[ℂ] E).IsSymmetric) (z : ℂ) (v : E) :
    |z.im| * ‖v‖ ≤ ‖A v - z • v‖ := by
  by_cases hv : v = 0
  · simp [hv]
  have hvp : 0 < ‖v‖ := norm_pos_iff.mpr hv
  have him : (inner ℂ v (A v - z • v)).im = -z.im * ‖v‖ ^ 2 := by
    have hr : (inner ℂ v (A v)).im = 0 := hA.im_inner_self_apply v
    rw [inner_sub_right, inner_smul_right, inner_self_eq_norm_sq_to_K]
    change (inner ℂ v (A v)).im - (z * (Complex.ofReal ‖v‖) ^ 2).im = _
    simp [hr, Complex.mul_im, pow_two]
  have hb := (Complex.abs_im_le_norm (inner ℂ v (A v - z • v))).trans
    (norm_inner_le_norm v (A v - z • v))
  rw [him, abs_mul, abs_neg, abs_pow, abs_of_nonneg (norm_nonneg v)] at hb
  nlinarith

def modalResolvent (A : E →L[ℂ] E) (z : ℂ) : E →L[ℂ] E :=
  Ring.inverse (A - z • (1 : E →L[ℂ] E))

theorem shifted_modalResolvent (A : E →L[ℂ] E) (hA : IsSelfAdjoint A)
    (z : ℂ) (hz : z.im ≠ 0) (v : E) :
    A (modalResolvent A z v) - z • modalResolvent A z v = v := by
  have h := congrArg (fun B : E →L[ℂ] E => B v)
    (Ring.mul_inverse_cancel _ (shifted_isUnit A hA z hz))
  simpa only [mul_apply_eq_comp, sub_apply,
    smul_apply, one_apply_eq_self, modalResolvent] using h

theorem modalResolvent_shifted (A : E →L[ℂ] E) (hA : IsSelfAdjoint A)
    (z : ℂ) (hz : z.im ≠ 0) (v : E) :
    modalResolvent A z (A v - z • v) = v := by
  have h := congrArg (fun B : E →L[ℂ] E => B v)
    (Ring.inverse_mul_cancel _ (shifted_isUnit A hA z hz))
  simpa only [mul_apply_eq_comp, sub_apply,
    smul_apply, one_apply_eq_self, modalResolvent] using h

theorem modalResolvent_norm_le (A : E →L[ℂ] E)
    (hA : (A : E →ₗ[ℂ] E).IsSymmetric) (z : ℂ) (hz : z.im ≠ 0) (v : E) :
    ‖modalResolvent A z v‖ ≤ |z.im|⁻¹ * ‖v‖ := by
  have h := shifted_lower_bound A hA z (modalResolvent A z v)
  rw [shifted_modalResolvent A hA.isSelfAdjoint z hz] at h
  exact (le_inv_mul_iff₀ (abs_pos.mpr hz)).mpr h

end ModalResolventTest
