import KomorebiSpace.InfiniteDiagonalModel
import KomorebiSpace.RegularizedHilbertRepair
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Algebra.Order.Floor.Ring
import Mathlib.Tactic

set_option autoImplicit false
noncomputable section

namespace KomorebiSpace.DiagonalRegularization

/-- The literal integer schedule in Corollary 30.3; the exponents are real. -/
def noiseSchedule (δ : ℝ) : ℕ := Nat.ceil (δ ^ (-(2 : ℝ) / 3))

/-- Positivity of the noise level makes the chosen integer positive. -/
theorem noiseSchedule_pos {δ : ℝ} (hδ : 0 < δ) : 0 < noiseSchedule δ := by
  exact Nat.ceil_pos.mpr (Real.rpow_pos_of_pos hδ _)

theorem one_le_noiseSchedule {δ : ℝ} (hδ : 0 < δ) : 1 ≤ noiseSchedule δ :=
  noiseSchedule_pos hδ

private theorem noise_rpow_mul {δ : ℝ} (hδ : 0 < δ) :
    δ * δ ^ (-(2 : ℝ) / 3) = δ ^ ((1 : ℝ) / 3) := by
  calc
    δ * δ ^ (-(2 : ℝ) / 3) =
        δ ^ (1 : ℝ) * δ ^ (-(2 : ℝ) / 3) := by rw [Real.rpow_one]
    _ = δ ^ ((1 : ℝ) + -(2 : ℝ) / 3) := (Real.rpow_add hδ _ _).symm
    _ = δ ^ ((1 : ℝ) / 3) := by norm_num

private theorem noise_rpow_sq {δ : ℝ} (hδ : 0 < δ) :
    δ ^ (-(2 : ℝ) / 3) * (δ ^ ((1 : ℝ) / 3)) ^ 2 = 1 := by
  have hs : (δ ^ ((1 : ℝ) / 3)) ^ 2 = δ ^ ((2 : ℝ) / 3) := by
    rw [← Real.rpow_natCast, ← Real.rpow_mul hδ.le]
    norm_num
  rw [hs, ← Real.rpow_add hδ]
  norm_num

/-- Both ceiling bounds retain the full rounding factor. -/
theorem noiseSchedule_bounds {δ : ℝ} (hδ : 0 < δ) (hδ₁ : δ ≤ 1) :
    δ ^ (-(2 : ℝ) / 3) ≤ (noiseSchedule δ : ℝ) ∧
      (noiseSchedule δ : ℝ) ≤ 2 * δ ^ (-(2 : ℝ) / 3) := by
  have hu : 1 ≤ δ ^ (-(2 : ℝ) / 3) := by
    exact Real.one_le_rpow_of_pos_of_le_one_of_nonpos hδ hδ₁ (by norm_num)
  constructor
  · exact Nat.le_ceil _
  · have hc := Nat.ceil_lt_add_one (show 0 ≤ δ ^ (-(2 : ℝ) / 3) from
      (Real.rpow_pos_of_pos hδ _).le)
    dsimp [noiseSchedule]
    linarith

/-- The exact-data term after rounding. -/
theorem noiseSchedule_bias_bound {δ : ℝ} (hδ : 0 < δ) (hδ₁ : δ ≤ 1) :
    Real.sqrt (2 / (noiseSchedule δ : ℝ)) ≤
      Real.sqrt 2 * δ ^ ((1 : ℝ) / 3) := by
  have hm : 0 < (noiseSchedule δ : ℝ) := by exact_mod_cast noiseSchedule_pos hδ
  have hq : 0 < δ ^ ((1 : ℝ) / 3) := Real.rpow_pos_of_pos hδ _
  have hmul := mul_le_mul_of_nonneg_right (noiseSchedule_bounds hδ hδ₁).1
    (sq_nonneg (δ ^ ((1 : ℝ) / 3)))
  rw [noise_rpow_sq hδ] at hmul
  have hquot : 2 / (noiseSchedule δ : ℝ) ≤ 2 * (δ ^ ((1 : ℝ) / 3)) ^ 2 := by
    apply (div_le_iff₀ hm).2
    nlinarith
  have hleft := Real.sq_sqrt (show 0 ≤ 2 / (noiseSchedule δ : ℝ) by positivity)
  have hright : (Real.sqrt 2 * δ ^ ((1 : ℝ) / 3)) ^ 2 =
      2 * (δ ^ ((1 : ℝ) / 3)) ^ 2 := by
    rw [mul_pow, Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 2)]
  have hn := Real.sqrt_nonneg (2 / (noiseSchedule δ : ℝ))
  have hn' : 0 ≤ Real.sqrt 2 * δ ^ ((1 : ℝ) / 3) := by positivity
  apply (sq_le_sq₀ hn hn').mp
  rw [hleft, hright]
  exact hquot

/-- The propagated-noise term after rounding. -/
theorem noiseSchedule_noise_bound {δ : ℝ} (hδ : 0 < δ) (hδ₁ : δ ≤ 1) :
    δ * (noiseSchedule δ : ℝ) / 2 ≤ δ ^ ((1 : ℝ) / 3) := by
  have h := mul_le_mul_of_nonneg_left (noiseSchedule_bounds hδ hδ₁).2 hδ.le
  have he := noise_rpow_mul hδ
  nlinarith

/-- The scalar part of Corollary 30.3, with the literal ceiling schedule. -/
theorem noiseSchedule_rate {δ : ℝ} (hδ : 0 < δ) (hδ₁ : δ ≤ 1) :
    Real.sqrt (2 / (noiseSchedule δ : ℝ)) + δ * (noiseSchedule δ : ℝ) / 2 ≤
      (Real.sqrt 2 + 1) * δ ^ ((1 : ℝ) / 3) := by
  have hb := noiseSchedule_bias_bound hδ hδ₁
  have hn := noiseSchedule_noise_bound hδ hδ₁
  nlinarith

/-- The sharp universal noise estimate at the inverse-square parameter.
This lemma deliberately retains its exact-data bias hypothesis. -/
theorem noisy_error_of_bias_bound
    {H Y : Type*} [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
    [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
    (T : H →L[ℝ] Y) (r s : Y) (aMin : H) (m : ℕ) (hm : 1 ≤ m)
    {δ : ℝ} (hdata : ‖s - r‖ ≤ δ)
    (hα : 0 < ((m : ℝ) ^ 2)⁻¹)
    (hbias : ‖RegularizedHilbertRepair.correction T (((m : ℝ) ^ 2)⁻¹) hα r -
      aMin‖ ≤ Real.sqrt (2 / (m : ℝ))) :
    ‖RegularizedHilbertRepair.correction T (((m : ℝ) ^ 2)⁻¹) hα s - aMin‖ ≤
      Real.sqrt (2 / (m : ℝ)) + δ * (m : ℝ) / 2 := by
  have hmpos : 0 < (m : ℝ) := by exact_mod_cast (lt_of_lt_of_le Nat.zero_lt_one hm)
  have hsqrt : Real.sqrt (((m : ℝ) ^ 2)⁻¹) = (m : ℝ)⁻¹ := by
    rw [Real.sqrt_inv, Real.sqrt_sq hmpos.le]
  have hnoise := (RegularizedHilbertRepair.data_noise_bound T
    (((m : ℝ) ^ 2)⁻¹) hα s r).trans
      (div_le_div_of_nonneg_right hdata (by positivity))
  rw [hsqrt] at hnoise
  have hquot : δ / (2 * (m : ℝ)⁻¹) = δ * (m : ℝ) / 2 := by
    field_simp [ne_of_gt hmpos]
  rw [hquot] at hnoise
  have he : RegularizedHilbertRepair.correction T (((m : ℝ) ^ 2)⁻¹) hα s - aMin =
      (RegularizedHilbertRepair.correction T (((m : ℝ) ^ 2)⁻¹) hα s -
        RegularizedHilbertRepair.correction T (((m : ℝ) ^ 2)⁻¹) hα r) +
      (RegularizedHilbertRepair.correction T (((m : ℝ) ^ 2)⁻¹) hα r - aMin) := by
    abel
  rw [he]
  exact (norm_add_le _ _).trans ((add_le_add hnoise hbias).trans_eq (add_comm _ _))

/-- The ceiling schedule transfers an assumed exact-data bias bound to a noisy rate.
The concrete diagonal corollary additionally needs its proved bias identity. -/
theorem noisy_rounded_rate_of_bias_bound
    {H Y : Type*} [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
    [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
    (T : H →L[ℝ] Y) (r s : Y) (aMin : H) {δ : ℝ}
    (hδ : 0 < δ) (hδ₁ : δ ≤ 1) (hdata : ‖s - r‖ ≤ δ)
    (hα : 0 < ((noiseSchedule δ : ℝ) ^ 2)⁻¹)
    (hbias : ‖RegularizedHilbertRepair.correction T
      (((noiseSchedule δ : ℝ) ^ 2)⁻¹) hα r - aMin‖ ≤
        Real.sqrt (2 / (noiseSchedule δ : ℝ))) :
    ‖RegularizedHilbertRepair.correction T (((noiseSchedule δ : ℝ) ^ 2)⁻¹) hα s -
      aMin‖ ≤ (Real.sqrt 2 + 1) * δ ^ ((1 : ℝ) / 3) := by
  exact (noisy_error_of_bias_bound T r s aMin (noiseSchedule δ)
    (one_le_noiseSchedule hδ) hdata hα hbias).trans (noiseSchedule_rate hδ hδ₁)

/-- The concrete attainable datum has the previously estimated infinite bias. -/
theorem diagonal_bias_bound {m : ℕ} (hm : 1 ≤ m) :
    ‖RegularizedHilbertRepair.correction T (alpha m) (alpha_pos hm) b - w‖ ≤
      Real.sqrt (2 / (m : ℝ)) := by
  rw [← c_eq_correction hm]
  apply (sq_le_sq₀ (norm_nonneg _) (Real.sqrt_nonneg _)).mp
  rw [norm_bias_sq, Real.sq_sqrt (by positivity : 0 ≤ 2 / (m : ℝ))]
  exact B_upper m hm

/-- The first printed inequality for arbitrary Hilbert noise and every positive integer. -/
theorem diagonal_noisy_error (s : H) {m : ℕ} (hm : 1 ≤ m) {δ : ℝ}
    (hdata : ‖s - b‖ ≤ δ) :
    ‖RegularizedHilbertRepair.correction T (alpha m) (alpha_pos hm) s - w‖ ≤
      Real.sqrt (2 / (m : ℝ)) + δ * (m : ℝ) / 2 := by
  exact noisy_error_of_bias_bound T b s w m hm hdata (alpha_pos hm)
    (diagonal_bias_bound hm)

/-- Corollary 30.3 on the actual infinite Hilbert model.
The datum and preimage are identified by `b_apply`, `w_apply`, and
`w_minimum_norm_preimage`; no exact-data bias assumption remains. -/
theorem corollary_30_3 (s : H) {δ : ℝ} (hδ : 0 < δ) (hδ₁ : δ ≤ 1)
    (hdata : ‖s - b‖ ≤ δ) :
    let m := Nat.ceil (δ ^ (-(2 : ℝ) / 3))
    let hm : 1 ≤ m := one_le_noiseSchedule hδ
    ‖RegularizedHilbertRepair.correction T (alpha m) (alpha_pos hm) s - w‖ ≤
        Real.sqrt (2 / (m : ℝ)) + δ * (m : ℝ) / 2 ∧
      Real.sqrt (2 / (m : ℝ)) + δ * (m : ℝ) / 2 ≤
        (Real.sqrt 2 + 1) * δ ^ ((1 : ℝ) / 3) := by
  exact ⟨diagonal_noisy_error s (one_le_noiseSchedule hδ) hdata,
    noiseSchedule_rate hδ hδ₁⟩

end KomorebiSpace.DiagonalRegularization
