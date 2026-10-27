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

end KomorebiSpace.DiagonalRegularization
