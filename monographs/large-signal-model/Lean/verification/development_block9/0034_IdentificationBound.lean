import KomorebiLSM.Pseudoinverse

set_option autoImplicit false
namespace Komorebi.LSM.Identification
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [NormedAddCommGroup F] [InnerProductSpace ℝ F]
variable [FiniteDimensional ℝ E] [FiniteDimensional ℝ F]

noncomputable def pinvL (A : E →L[ℝ] F) : F →L[ℝ] E := (pinv A.toLinearMap).toContinuousLinearMap

/-- Variational smallest row singular value, using nonzero vectors to avoid normalization choices. -/
noncomputable def rowGain (A : E →L[ℝ] F) : ℝ :=
  sInf {r : ℝ | ∃ v : F, v ≠ 0 ∧ r = ‖A.adjoint v‖ / ‖v‖}

theorem rowGain_variational_unit (A : E →L[ℝ] F) :
    rowGain A = sInf {r : ℝ | ∃ v : F, ‖v‖ = 1 ∧ r = ‖A.adjoint v‖} := by
  unfold rowGain
  congr 1
  ext r
  constructor
  · rintro ⟨v,hv,rfl⟩
    have hn : ‖v‖ ≠ 0 := norm_ne_zero_iff.mpr hv
    refine ⟨‖v‖⁻¹ • v, ?_, ?_⟩
    · rw [norm_smul, Real.norm_eq_abs, abs_inv, abs_of_nonneg (norm_nonneg v), inv_mul_cancel₀ hn]
    · rw [map_smul, norm_smul, Real.norm_eq_abs, abs_inv, abs_of_nonneg (norm_nonneg v)]
      exact div_eq_inv_mul _ _
  · rintro ⟨v,hv,rfl⟩
    refine ⟨v, ?_, ?_⟩
    · intro hz; simp [hz] at hv
    · rw [hv, div_one]

theorem rowGain_lower (A : E →L[ℝ] F) (v : F) : rowGain A * ‖v‖ ≤ ‖A.adjoint v‖ := by
  by_cases hv : v = 0
  · simp [hv]
  · have hn : 0 < ‖v‖ := norm_pos_iff.mpr hv
    have hb : BddBelow {r : ℝ | ∃ w : F, w ≠ 0 ∧ r = ‖A.adjoint w‖ / ‖w‖} := by
      refine ⟨0, ?_⟩
      rintro r ⟨w,_,rfl⟩
      exact div_nonneg (norm_nonneg _) (norm_nonneg _)
    have hi := csInf_le hb (show ‖A.adjoint v‖ / ‖v‖ ∈
      {r : ℝ | ∃ w : F, w ≠ 0 ∧ r = ‖A.adjoint w‖ / ‖w‖} from ⟨v,hv,rfl⟩)
    exact (le_div_iff₀ hn).mp hi

theorem rowGain_perturbation (A E' : E →L[ℝ] F) (v : F) :
    (rowGain A - ‖E'‖) * ‖v‖ ≤ ‖(A+E').adjoint v‖ := by
  have h1 := rowGain_lower A v
  have h2 := E'.adjoint.le_opNorm v
  have h3 : ‖A.adjoint v‖ ≤ ‖(A+E').adjoint v‖ + ‖E'.adjoint v‖ := by
    have he : A.adjoint v = (A+E').adjoint v - E'.adjoint v := by simp
    rw [he]
    exact norm_sub_le _ _
  simpa using (by nlinarith :
    (rowGain A - ‖E'.adjoint‖) * ‖v‖ ≤ ‖(A+E').adjoint v‖)

theorem surjective_of_adjoint_lower (A : E →L[ℝ] F) (c : ℝ) (hc : 0 < c)
    (hl : ∀ v, c * ‖v‖ ≤ ‖A.adjoint v‖) : Function.Surjective A := by
  have hk : A.toLinearMap.adjoint.ker = ⊥ := by
    apply le_antisymm _ bot_le
    intro v hv
    have h := hl v
    have hz : A.adjoint v = 0 := hv
    rw [hz, norm_zero] at h
    have hv0 : v = 0 := norm_eq_zero.mp (by nlinarith [norm_nonneg v])
    simp [hv0]
  have ho : A.toLinearMap.rangeᗮ = ⊥ := by rw [LinearMap.orthogonal_range, hk]
  have hr : A.toLinearMap.range = ⊤ := by
    have he := congrArg (fun W : Submodule ℝ F => Wᗮ) ho
    simpa using he
  exact LinearMap.range_eq_top.mp hr

theorem pinvL_right (A : E →L[ℝ] F) (hs : Function.Surjective A) (y : F) :
    A (pinvL A y) = y := by
  change A.toLinearMap (pinv A.toLinearMap y) = y
  rw [apply_pinv]
  exact A.toLinearMap.range.starProjection_eq_self_iff.mpr (hs y)

theorem pinvL_bound (A : E →L[ℝ] F) (c : ℝ) (hc : 0 < c)
    (hl : ∀ v, c * ‖v‖ ≤ ‖A.adjoint v‖) : ‖pinvL A‖ ≤ c⁻¹ := by
  apply ContinuousLinearMap.opNorm_le_bound _ (inv_nonneg.mpr hc.le)
  intro y
  have hm := pinv_apply_mem A.toLinearMap y
  rw [LinearMap.orthogonal_ker] at hm
  obtain ⟨v,hv⟩ := hm
  have hv' : A.adjoint v = pinvL A y := hv
  have he : inner ℝ (pinvL A y) (pinvL A y) = inner ℝ v y := by
    nth_rw 1 [← hv']
    rw [ContinuousLinearMap.adjoint_inner_left, pinvL_right A (surjective_of_adjoint_lower A c hc hl)]
  have hi := real_inner_le_norm v y
  rw [real_inner_self_eq_norm_sq] at he
  have hh := hl v
  rw [hv'] at hh
  have hn : c * ‖pinvL A y‖ ≤ ‖y‖ := by
    by_cases hz : ‖pinvL A y‖ = 0
    · simp [hz]
    · have hp : 0 < ‖pinvL A y‖ := lt_of_le_of_ne (norm_nonneg _) (Ne.symm hz)
      have hm := mul_le_mul_of_nonneg_right hi hc.le
      have hm2 := mul_le_mul_of_nonneg_right hh (norm_nonneg y)
      nlinarith
  rw [inv_mul_eq_div]
  exact (le_div_iff₀ hc).mpr (by nlinarith)

theorem noisy_identification_identity (A R E' F' : E →L[ℝ] F) (B : F →L[ℝ] F)
    (hE : ‖E'‖ < rowGain A) :
    ((B.comp A + R + F').comp (pinvL (A+E'))) - B =
      (R + F' - B.comp E').comp (pinvL (A+E')) := by
  have hs := surjective_of_adjoint_lower (A+E') (rowGain A - ‖E'‖)
    (sub_pos.mpr hE) (rowGain_perturbation A E')
  apply ContinuousLinearMap.ext
  intro y
  have he := pinvL_right (A+E') hs y
  simp only [add_apply] at he
  have hb := congrArg B he
  simp only [map_add] at hb
  simp only [sub_apply, ContinuousLinearMap.comp_apply,
    add_apply]
  rw [← hb]
  abel

theorem noisy_identification_bound (A R E' F' : E →L[ℝ] F) (B : F →L[ℝ] F)
    (hE : ‖E'‖ < rowGain A) :
    ‖((B.comp A + R + F').comp (pinvL (A+E'))) - B‖ ≤
      (‖R‖ + ‖F'‖ + ‖B‖ * ‖E'‖) / (rowGain A - ‖E'‖) := by
  rw [noisy_identification_identity A R E' F' B hE]
  have hn : ‖R + F' - B.comp E'‖ ≤ ‖R‖ + ‖F'‖ + ‖B‖ * ‖E'‖ :=
    (norm_sub_le _ _).trans (add_le_add (norm_add_le _ _) (ContinuousLinearMap.opNorm_comp_le _ _))
  have hj := pinvL_bound (A+E') (rowGain A - ‖E'‖) (sub_pos.mpr hE)
    (rowGain_perturbation A E')
  calc
    _ ≤ ‖R + F' - B.comp E'‖ * ‖pinvL (A+E')‖ := ContinuousLinearMap.opNorm_comp_le _ _
    _ ≤ (‖R‖ + ‖F'‖ + ‖B‖ * ‖E'‖) * (rowGain A - ‖E'‖)⁻¹ :=
      mul_le_mul hn hj (norm_nonneg _) (by positivity)
    _ = _ := div_eq_mul_inv _ _ |>.symm
end Komorebi.LSM.Identification
