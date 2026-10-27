import KomorebiLSM.SpectralPseudoinverse

set_option autoImplicit false
namespace Komorebi.LSM.Spectral
open Komorebi.LSM.Identification
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [NormedAddCommGroup F] [InnerProductSpace ℝ F]
variable [FiniteDimensional ℝ E] [FiniteDimensional ℝ F]

theorem image_basis_norm (A : E →ₗ[ℝ] F) (i : Fin (Module.finrank ℝ E)) :
    ‖A (rightBasis A i)‖ = A.singularValues i := by
  have h := image_inner A (rightBasis A i) i
  simp only [real_inner_self_eq_norm_sq, (rightBasis A).norm_eq_one, one_pow, mul_one] at h
  nlinarith [norm_nonneg (A (rightBasis A i)), A.singularValues_nonneg i]

theorem positive_mode_orthogonal (A : E →ₗ[ℝ] F) (i : Fin (Module.finrank ℝ E))
    (hi : 0 < A.singularValues i) : rightBasis A i ∈ A.kerᗮ := by
  apply (A.ker.mem_orthogonal' _).mpr
  intro y hy
  have h := image_inner A y i
  have hz : A y = 0 := hy
  rw [hz, inner_zero_right] at h
  exact (mul_eq_zero.mp h.symm).resolve_left (pow_ne_zero _ (ne_of_gt hi))

theorem exists_unit_minimizer (A : E →ₗ[ℝ] F)
    (hr : 0 < Module.finrank ℝ A.range) :
    ∃ v : E, v ∈ A.kerᗮ ∧ ‖v‖ = 1 ∧ ‖A v‖ = leastPositive A := by
  have hd := LinearMap.finrank_range_le A
  let i : Fin (Module.finrank ℝ E) := ⟨Module.finrank ℝ A.range-1, by omega⟩
  refine ⟨rightBasis A i, positive_mode_orthogonal A i (leastPositive_pos A hr),
    (rightBasis A).norm_eq_one i, ?_⟩
  exact image_basis_norm A i

/-- Sharp operator norm for the actual orthogonal pseudoinverse. -/
theorem pinv_operator_norm_eq (A : E →L[ℝ] F)
    (hr : 0 < Module.finrank ℝ A.toLinearMap.range) :
    ‖pinvL A‖ = (leastPositive A.toLinearMap)⁻¹ := by
  apply le_antisymm (pinv_operator_bound A hr)
  obtain ⟨v,hv,hn,ha⟩ := exists_unit_minimizer A.toLinearMap hr
  have he : pinvL A (A v) = v := by
    change pinv A.toLinearMap (A.toLinearMap v) = v
    rw [pinv_apply_image]
    exact A.toLinearMap.kerᗮ.starProjection_eq_self_iff.mpr hv
  change ‖A v‖ = leastPositive A.toLinearMap at ha
  have h := (pinvL A).le_opNorm (A v)
  rw [he, hn, ha] at h
  rw [inv_eq_one_div]
  exact (div_le_iff₀ (leastPositive_pos A.toLinearMap hr)).mpr h

/-- Restricting the pseudoinverse to its actual range keeps the sharp norm. -/
theorem rangeInverse_norm_eq (A : E →L[ℝ] F)
    (hr : 0 < Module.finrank ℝ A.toLinearMap.range) :
    ‖rangeInverse A‖ = (leastPositive A.toLinearMap)⁻¹ := by
  apply le_antisymm (rangeInverse_bound A hr)
  obtain ⟨v,hv,hn,ha⟩ := exists_unit_minimizer A.toLinearMap hr
  let y : A.toLinearMap.range := A.toLinearMap.rangeRestrict v
  have he : rangeInverse A y = v := by
    change pinv A.toLinearMap (A.toLinearMap v) = v
    rw [pinv_apply_image]
    exact A.toLinearMap.kerᗮ.starProjection_eq_self_iff.mpr hv
  have hy : ‖y‖ = leastPositive A.toLinearMap := ha
  have h := (rangeInverse A).le_opNorm y
  rw [he, hn, hy] at h
  rw [inv_eq_one_div]
  exact (div_le_iff₀ (leastPositive_pos A.toLinearMap hr)).mpr h

end Komorebi.LSM.Spectral
