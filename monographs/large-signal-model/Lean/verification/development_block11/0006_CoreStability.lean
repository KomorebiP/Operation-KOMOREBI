import KomorebiLSM.IdentificationBound

set_option autoImplicit false
set_option maxHeartbeats 400000
namespace Komorebi.LSM.Identification
variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [FiniteDimensional ℝ E]

/-- The fitted core uses the constructed Moore--Penrose inverse. The two-sided
inverse laws below identify it with the ordinary square inverse. -/
@[irreducible] noncomputable def coreFit (H E' F' B : E →L[ℝ] E) : E →L[ℝ] E :=
  (B.comp H + F').comp (pinvL (H+E'))

theorem core_perturbed_surjective (H E' : E →L[ℝ] E) (hE : ‖E'‖ < rowGain H) :
    Function.Surjective (H+E') :=
  surjective_of_adjoint_lower (H+E') (rowGain H-‖E'‖) (sub_pos.mpr hE)
    (rowGain_perturbation H E')

theorem square_pinv_left (H : E →L[ℝ] E) (hs : Function.Surjective H) (x : E) :
    pinvL H (H x) = x := by
  have hi : Function.Injective H := (LinearMap.injective_iff_surjective (f := H.toLinearMap)).mpr hs
  apply hi
  exact pinvL_right H hs (H x)

theorem core_inverse_laws (H E' : E →L[ℝ] E) (hE : ‖E'‖ < rowGain H) :
    (∀ x, (H+E') (pinvL (H+E') x) = x) ∧
    (∀ x, pinvL (H+E') ((H+E') x) = x) := by
  have hs := core_perturbed_surjective H E' hE
  exact ⟨pinvL_right _ hs, square_pinv_left _ hs⟩

theorem core_error_identity (H E' F' B : E →L[ℝ] E) (hE : ‖E'‖ < rowGain H) :
    coreFit H E' F' B - B = (F'-B.comp E').comp (pinvL (H+E')) := by
  simpa [coreFit] using noisy_identification_identity H 0 E' F' B hE

theorem core_error_bound (H E' F' B : E →L[ℝ] E) (hE : ‖E'‖ < rowGain H) :
    ‖coreFit H E' F' B - B‖ ≤
      (‖F'‖+‖B‖*‖E'‖)/(rowGain H-‖E'‖) := by
  simpa [coreFit] using noisy_identification_bound H 0 E' F' B hE

theorem core_fitted_residual (H E' F' B : E →L[ℝ] E) (hE : ‖E'‖ < rowGain H) :
    (coreFit H E' F' B-B).comp H = F'-(coreFit H E' F' B).comp E' := by
  apply ContinuousLinearMap.ext
  intro x
  have he : coreFit H E' F' B ((H+E') x) = B (H x)+F' x := by
    simp only [coreFit, ContinuousLinearMap.comp_apply]
    rw [square_pinv_left _ (core_perturbed_surjective H E' hE)]
    rfl
  simp only [add_apply, map_add] at he
  simp only [ContinuousLinearMap.comp_apply, sub_apply]
  exact sub_eq_sub_iff_add_eq_add.mpr (by simpa [add_comm] using he)

theorem core_fitted_identity (H E' F' B : E →L[ℝ] E) (hE : ‖E'‖ < rowGain H) :
    coreFit H E' F' B-B = (F'-(coreFit H E' F' B).comp E').comp (pinvL H) := by
  have hs := surjective_of_adjoint_lower H (rowGain H)
    (lt_of_le_of_lt (norm_nonneg E') hE) (rowGain_lower H)
  rw [← core_fitted_residual H E' F' B hE]
  ext x
  simp only [ContinuousLinearMap.comp_apply]
  rw [pinvL_right H hs]

theorem core_fitted_bound (H E' F' B : E →L[ℝ] E) (hE : ‖E'‖ < rowGain H) :
    ‖coreFit H E' F' B-B‖ ≤ (‖F'‖+‖coreFit H E' F' B‖*‖E'‖)/rowGain H := by
  have hs : 0 < rowGain H := lt_of_le_of_lt (norm_nonneg E') hE
  have hn : ‖F'-(coreFit H E' F' B).comp E'‖ ≤ ‖F'‖+‖coreFit H E' F' B‖*‖E'‖ :=
    (norm_sub_le _ _).trans (add_le_add_left (ContinuousLinearMap.opNorm_comp_le _ _) _)
  rw [core_fitted_identity H E' F' B hE]
  calc
    _ ≤ ‖F'-(coreFit H E' F' B).comp E'‖ * ‖pinvL H‖ := ContinuousLinearMap.opNorm_comp_le _ _
    _ ≤ (‖F'‖+‖coreFit H E' F' B‖*‖E'‖) * (rowGain H)⁻¹ :=
      mul_le_mul hn (pinvL_bound H (rowGain H) hs (rowGain_lower H)) (norm_nonneg _) (by positivity)
    _ = _ := (div_eq_mul_inv _ _).symm

theorem core_checked_fitted_bound (H E' F' B : E →L[ℝ] E)
    (hE : ‖E'‖ < rowGain H) (e : ℝ) (he : ‖E'‖ ≤ e)
    (hgap : e < rowGain (H+E')) :
    ‖coreFit H E' F' B-B‖ ≤
      (‖F'‖+‖coreFit H E' F' B‖*‖E'‖)/(rowGain (H+E')-e) := by
  have hl : ∀ v, (rowGain (H+E')-e)*‖v‖ ≤ ‖H.adjoint v‖ := by
    intro v
    have h := rowGain_perturbation (H+E') (-E') v
    simp only [norm_neg, add_neg_cancel_right] at h
    exact (mul_le_mul_of_nonneg_right (sub_le_sub_left he _) (norm_nonneg v)).trans h
  have hn : ‖F'-(coreFit H E' F' B).comp E'‖ ≤ ‖F'‖+‖coreFit H E' F' B‖*‖E'‖ :=
    (norm_sub_le _ _).trans (add_le_add_left (ContinuousLinearMap.opNorm_comp_le _ _) _)
  rw [core_fitted_identity H E' F' B hE]
  calc
    _ ≤ ‖F'-(coreFit H E' F' B).comp E'‖ * ‖pinvL H‖ := ContinuousLinearMap.opNorm_comp_le _ _
    _ ≤ (‖F'‖+‖coreFit H E' F' B‖*‖E'‖) * (rowGain (H+E')-e)⁻¹ :=
      mul_le_mul hn (pinvL_bound H _ (sub_pos.mpr hgap) hl) (norm_nonneg _) (by positivity)
    _ = _ := (div_eq_mul_inv _ _).symm

end Komorebi.LSM.Identification
