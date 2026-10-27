import KomorebiLSM.IdentificationBound
import KomorebiLSM.DefectPropagation

set_option autoImplicit false
namespace Komorebi.LSM.Filtering
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- Normalization is only used below with positive mass. -/
noncomputable def normalize (lam : E →L[ℝ] ℝ) (u : E) : E := (lam u)⁻¹ • u

theorem prediction_error (B Bhat : E →L[ℝ] E) (z zhat : E)
    (L ε R : ℝ) (hL : ‖Bhat‖ ≤ L) (hε : ‖Bhat-B‖ ≤ ε) (hR : ‖z‖ ≤ R) :
    ‖Bhat zhat - B z‖ ≤ L * ‖zhat-z‖ + ε * R := by
  have hε0 : 0 ≤ ε := (norm_nonneg _).trans hε
  have he : Bhat zhat - B z = Bhat (zhat-z) + (Bhat-B) z := by simp
  rw [he]
  calc
    _ ≤ ‖Bhat (zhat-z)‖ + ‖(Bhat-B) z‖ := norm_add_le _ _
    _ ≤ ‖Bhat‖ * ‖zhat-z‖ + ‖Bhat-B‖ * ‖z‖ := add_le_add (Bhat.le_opNorm _) ((Bhat-B).le_opNorm _)
    _ ≤ L * ‖zhat-z‖ + ε * R := add_le_add
      (mul_le_mul_of_nonneg_right hL (norm_nonneg _))
      (mul_le_mul hε hR (norm_nonneg _) hε0)

theorem mass_lower (lam : E →L[ℝ] ℝ) (u uhat : E) (η D : ℝ)
    (hp : η ≤ lam u) (hd : ‖uhat-u‖ ≤ D) :
    η - ‖lam‖ * D ≤ lam uhat := by
  have h := lam.le_opNorm (uhat-u)
  have hh := mul_le_mul_of_nonneg_left hd (norm_nonneg lam)
  rw [map_sub, Real.norm_eq_abs] at h
  have ha := neg_abs_le (lam uhat-lam u)
  linarith

theorem fitted_mass_positive (lam : E →L[ℝ] ℝ) (u uhat : E) (η D : ℝ)
    (hp : η ≤ lam u) (hd : ‖uhat-u‖ ≤ D) (hm : ‖lam‖ * D < η) :
    0 < lam uhat := lt_of_lt_of_le (sub_pos.mpr hm) (mass_lower lam u uhat η D hp hd)

theorem normalized_residual (lam : E →L[ℝ] ℝ) (u uhat : E)
    (hp : lam u ≠ 0) (hq : lam uhat ≠ 0) :
    normalize lam uhat - normalize lam u =
      (lam uhat)⁻¹ • ((uhat-u) - (lam (uhat-u)) • normalize lam u) := by
  unfold normalize
  rw [map_sub, smul_sub, smul_sub, smul_smul]
  have hc : (lam uhat)⁻¹ * (lam uhat-lam u) * (lam u)⁻¹ =
      (lam u)⁻¹ - (lam uhat)⁻¹ := by field_simp
  rw [smul_smul, hc, sub_smul]
  abel

theorem residual_numerator_bound (lam : E →L[ℝ] ℝ) (z d : E) (R D : ℝ)
    (hz : ‖z‖ ≤ R) (hd : ‖d‖ ≤ D) :
    ‖d - (lam d) • z‖ ≤ (1 + R * ‖lam‖) * D := by
  have hR : 0 ≤ R := (norm_nonneg _).trans hz
  calc
    _ ≤ ‖d‖ + ‖(lam d) • z‖ := norm_sub_le _ _
    _ = ‖d‖ + ‖lam d‖ * ‖z‖ := by rw [norm_smul]
    _ ≤ ‖d‖ + (‖lam‖ * ‖d‖) * R := add_le_add le_rfl
      (mul_le_mul (lam.le_opNorm d) hz (norm_nonneg _) (by positivity))
    _ = (1+R*‖lam‖) * ‖d‖ := by ring
    _ ≤ _ := mul_le_mul_of_nonneg_left hd (by positivity)

theorem normalized_error_checked (lam : E →L[ℝ] ℝ) (u uhat : E) (R D ηhat : ℝ)
    (hp : lam u ≠ 0) (hq : ηhat ≤ lam uhat) (hη : 0 < ηhat)
    (hz : ‖normalize lam u‖ ≤ R) (hd : ‖uhat-u‖ ≤ D) :
    ‖normalize lam uhat - normalize lam u‖ ≤ (1+R*‖lam‖)*D/ηhat := by
  have hq0 := lt_of_lt_of_le hη hq
  rw [normalized_residual lam u uhat hp (ne_of_gt hq0), norm_smul,
    Real.norm_eq_abs, abs_inv, abs_of_pos hq0]
  have hn := residual_numerator_bound lam (normalize lam u) (uhat-u) R D hz hd
  calc
    _ ≤ (lam uhat)⁻¹ * ((1+R*‖lam‖)*D) := mul_le_mul_of_nonneg_left hn (inv_nonneg.mpr hq0.le)
    _ = ((1+R*‖lam‖)*D) / lam uhat := by rw [div_eq_mul_inv]; ring
    _ ≤ _ := div_le_div_of_nonneg_left ((norm_nonneg _).trans hn) hη hq

theorem normalized_error_margin (lam : E →L[ℝ] ℝ) (u uhat : E) (R D η : ℝ)
    (hp : η ≤ lam u) (hη : 0 < η) (hz : ‖normalize lam u‖ ≤ R)
    (hd : ‖uhat-u‖ ≤ D) (hm : ‖lam‖*D < η) :
    0 < lam uhat ∧
    ‖normalize lam uhat - normalize lam u‖ ≤ (1+R*‖lam‖)*D/(η-‖lam‖*D) := by
  exact ⟨fitted_mass_positive lam u uhat η D hp hd hm,
    normalized_error_checked lam u uhat R D (η-‖lam‖*D)
      (ne_of_gt (lt_of_lt_of_le hη hp)) (mass_lower lam u uhat η D hp hd)
      (sub_pos.mpr hm) hz hd⟩

theorem filtering_step (lam : E →L[ℝ] ℝ) (B Bhat : E →L[ℝ] E) (z zhat : E)
    (R L ε ηhat : ℝ) (hL : ‖Bhat‖ ≤ L) (hε : ‖Bhat-B‖ ≤ ε)
    (hz : ‖z‖ ≤ R) (hzplus : ‖normalize lam (B z)‖ ≤ R)
    (hp : lam (B z) ≠ 0) (hq : ηhat ≤ lam (Bhat zhat)) (hη : 0 < ηhat) :
    ‖normalize lam (Bhat zhat) - normalize lam (B z)‖ ≤
      ((1+R*‖lam‖)*L/ηhat)*‖zhat-z‖ + (1+R*‖lam‖)*ε*R/ηhat := by
  have h := normalized_error_checked lam (B z) (Bhat zhat) R
    (L*‖zhat-z‖+ε*R) ηhat hp hq hη hzplus (prediction_error B Bhat z zhat L ε R hL hε hz)
  convert h using 1; ring

theorem filtering_path (lam : E →L[ℝ] ℝ) (B Bhat : ℕ → E →L[ℝ] E)
    (z zhat : ℕ → E) (R : ℝ) (L ε ηhat : ℕ → ℝ)
    (true_step : ∀ t, z (t+1) = normalize lam (B t (z t)))
    (fit_step : ∀ t, zhat (t+1) = normalize lam (Bhat t (zhat t)))
    (hL : ∀ t, ‖Bhat t‖ ≤ L t) (hε : ∀ t, ‖Bhat t-B t‖ ≤ ε t)
    (hz : ∀ t, ‖z t‖ ≤ R) (hp : ∀ t, lam (B t (z t)) ≠ 0)
    (hq : ∀ t, ηhat t ≤ lam (Bhat t (zhat t))) (hη : ∀ t, 0 < ηhat t)
    (T : ℕ) :
    ‖zhat T-z T‖ ≤ Stability.errorEnvelope
      (fun t => (1+R*‖lam‖)*L t/ηhat t)
      (fun t => (1+R*‖lam‖)*ε t*R/ηhat t) ‖zhat 0-z 0‖ T := by
  have hR : 0 ≤ R := (norm_nonneg _).trans (hz 0)
  apply Stability.recurrence_product_sum (fun t => ‖zhat t-z t‖)
    (fun t => (1+R*‖lam‖)*L t/ηhat t) (fun t => (1+R*‖lam‖)*ε t*R/ηhat t)
  · intro t
    have hLt : 0 ≤ L t := (norm_nonneg _).trans (hL t)
    exact div_nonneg (mul_nonneg (by positivity) hLt) (hη t).le
  · intro t
    rw [true_step, fit_step]
    apply filtering_step lam (B t) (Bhat t) (z t) (zhat t) R (L t) (ε t) (ηhat t)
      (hL t) (hε t) (hz t) _ (hp t) (hq t) (hη t)
    rw [← true_step]
    exact hz (t+1)

theorem filtering_uniform (lam : E →L[ℝ] ℝ) (B Bhat : ℕ → E →L[ℝ] E)
    (z zhat : ℕ → E) (R : ℝ) (L ε ηhat : ℕ → ℝ) (ρ β : ℝ)
    (true_step : ∀ t, z (t+1) = normalize lam (B t (z t)))
    (fit_step : ∀ t, zhat (t+1) = normalize lam (Bhat t (zhat t)))
    (hL : ∀ t, ‖Bhat t‖ ≤ L t) (hε : ∀ t, ‖Bhat t-B t‖ ≤ ε t)
    (hz : ∀ t, ‖z t‖ ≤ R) (hp : ∀ t, lam (B t (z t)) ≠ 0)
    (hq : ∀ t, ηhat t ≤ lam (Bhat t (zhat t))) (hη : ∀ t, 0 < ηhat t)
    (hρ : 0 ≤ ρ) (hsmall : ρ < 1) (hβ : 0 ≤ β)
    (hα : ∀ t, (1+R*‖lam‖)*L t/ηhat t ≤ ρ)
    (hforce : ∀ t, (1+R*‖lam‖)*ε t*R/ηhat t ≤ β) (T : ℕ) :
    ‖zhat T-z T‖ ≤ ρ^T*‖zhat 0-z 0‖ + β/(1-ρ) := by
  have step : ∀ t, ‖zhat (t+1)-z (t+1)‖ ≤ ρ*‖zhat t-z t‖+β := by
    intro t
    rw [true_step, fit_step]
    have hzplus : ‖normalize lam (B t (z t))‖ ≤ R := by rw [← true_step]; exact hz (t+1)
    exact (filtering_step lam (B t) (Bhat t) (z t) (zhat t) R (L t) (ε t) (ηhat t)
      (hL t) (hε t) (hz t) hzplus (hp t) (hq t) (hη t)).trans
      (add_le_add (mul_le_mul_of_nonneg_right (hα t) (norm_nonneg _)) (hforce t))
  have h := Stability.constant_gain_bound (fun t => ‖zhat t-z t‖) hρ hsmall step T
  apply h.trans
  apply add_le_add le_rfl
  rw [mul_div_assoc]
  apply (div_le_div_iff_of_pos_right (sub_pos.mpr hsmall)).mpr
  nlinarith [pow_nonneg hρ T]

end Komorebi.LSM.Filtering
