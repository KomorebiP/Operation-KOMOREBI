import KomorebiLSM.SpectralLowerBound
import KomorebiLSM.NoisySubspaceResidual

set_option autoImplicit false
namespace Komorebi.LSM.Spectral
open Komorebi.LSM.Identification
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [NormedAddCommGroup F] [InnerProductSpace ℝ F]
variable [FiniteDimensional ℝ E] [FiniteDimensional ℝ F]

theorem pinv_pointwise_bound (A : E →ₗ[ℝ] F)
    (hr : 0 < Module.finrank ℝ A.range) (y : F) :
    ‖pinv A y‖ ≤ (leastPositive A)⁻¹ * ‖y‖ := by
  have hs := leastPositive_pos A hr
  have h := lower_on_kernel_orthogonal A (pinv A y) (pinv_apply_mem A y)
  rw [apply_pinv] at h
  have h' := h.trans (A.range.norm_starProjection_apply_le y)
  rw [inv_mul_eq_div]
  exact (le_div_iff₀ hs).mpr (by simpa [mul_comm] using h')

theorem pinv_operator_bound (A : E →L[ℝ] F)
    (hr : 0 < Module.finrank ℝ A.toLinearMap.range) :
    ‖pinvL A‖ ≤ (leastPositive A.toLinearMap)⁻¹ := by
  apply ContinuousLinearMap.opNorm_le_bound _ (inv_nonneg.mpr (leastPositive_pos _ hr).le)
  exact pinv_pointwise_bound A.toLinearMap hr

/-- The inverse on the actual column space is constructed from the existing
orthogonal pseudoinverse, not postulated as input data. -/
noncomputable def rangeInverse (A : E →L[ℝ] F) : A.toLinearMap.range →L[ℝ] E :=
  (pinvL A).comp A.toLinearMap.range.subtypeL

theorem rangeInverse_right (A : E →L[ℝ] F) (x : A.toLinearMap.range) :
    A (rangeInverse A x) = (x:F) := by
  change A.toLinearMap (pinv A.toLinearMap (x:F)) = (x:F)
  rw [apply_pinv, A.toLinearMap.range.starProjection_eq_self_iff.mpr x.property]

theorem rangeInverse_bound (A : E →L[ℝ] F)
    (hr : 0 < Module.finrank ℝ A.toLinearMap.range) :
    ‖rangeInverse A‖ ≤ (leastPositive A.toLinearMap)⁻¹ := by
  apply ContinuousLinearMap.opNorm_le_bound _ (inv_nonneg.mpr (leastPositive_pos _ hr).le)
  intro x
  exact pinv_pointwise_bound A.toLinearMap hr (x:F)

/-- P32's inverse premise is now derived from the actual singular spectrum.
Only the estimated subspace's dimension and observed tail remain supplied. -/
theorem gap_from_observed_tail (X N : E →L[ℝ] F) (Q : Submodule ℝ F)
    (hr : 0 < Module.finrank ℝ X.toLinearMap.range) (ε : ℝ) (hε : 0 ≤ ε)
    (hsmall : ε < leastPositive X.toLinearMap / 2)
    (htail : ‖Qᗮ.starProjection.comp (X+N)‖ ≤ ε) (hnoise : ‖N‖ ≤ ε)
    (hdim : Module.finrank ℝ X.toLinearMap.range = Module.finrank ℝ Q) :
    ‖X.toLinearMap.range.starProjection-Q.starProjection‖ ≤
      2*ε/leastPositive X.toLinearMap ∧ 2*ε/leastPositive X.toLinearMap < 1 :=
  OneSidedSubspace.two_epsilon_gap X.toLinearMap.range Q X N (rangeInverse X)
    ε (leastPositive X.toLinearMap) hε (leastPositive_pos _ hr) hsmall htail hnoise
    (rangeInverse_bound X hr) (rangeInverse_right X) hdim

end Komorebi.LSM.Spectral
