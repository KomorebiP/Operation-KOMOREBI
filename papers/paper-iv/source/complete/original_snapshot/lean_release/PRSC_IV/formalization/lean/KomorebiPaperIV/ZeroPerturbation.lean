/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroGeometry
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Topology.MetricSpace.Contracting

/-! # Local zeros of a perturbed two-exponential sum

The zero existence and uniqueness step is proved by contraction of the actual
complex logarithm. No zero-counting or existence certificate is assumed.
-/

namespace Komorebi.PaperIV
noncomputable section
open Metric

theorem norm_one_add_lower_half {u : ℂ} (hu : ‖u‖ ≤ 1 / 2) :
    (1 / 2 : ℝ) ≤ ‖1 + u‖ := by
  have h := norm_sub_norm_le (1 : ℂ) (-u)
  simp only [norm_one, norm_neg, sub_neg_eq_add] at h
  linarith

theorem log_one_add_lipschitz_half :
    LipschitzOnWith 2 (fun u : ℂ => Complex.log (1 + u)) (closedBall 0 (1 / 2)) := by
  apply (convex_closedBall (0 : ℂ) (1 / 2)).lipschitzOnWith_of_nnnorm_hasDerivWithin_le
    (f' := fun u => (1 + u)⁻¹)
  · intro u hu
    have hu' : ‖u‖ ≤ 1 / 2 := by simpa [mem_closedBall, dist_eq_norm] using hu
    exact ((Complex.hasDerivAt_log (Complex.mem_slitPlane_of_norm_lt_one
      (lt_of_le_of_lt hu' (by norm_num)))).comp_const_add 1 u).hasDerivWithinAt
  · intro u hu
    have hu' : ‖u‖ ≤ 1 / 2 := by simpa [mem_closedBall, dist_eq_norm] using hu
    change ‖(1 + u)⁻¹‖ ≤ (2 : ℝ)
    rw [norm_inv, inv_eq_one_div, div_le_iff₀ (lt_of_lt_of_le (by norm_num) (norm_one_add_lower_half hu'))]
    linarith [norm_one_add_lower_half hu']

/-- The actual logarithmic correction map. -/
def logarithmicZeroMap (a t : ℂ) (R : ℂ → ℂ) (z : ℂ) : ℂ :=
  t + Complex.log (1 + R z) / a

theorem logarithmicZeroMap_mapsTo {a t : ℂ} (ha : a ≠ 0) {R : ℂ → ℂ}
    (hR : ∀ z ∈ closedBall t (1 / ‖a‖), ‖R z‖ ≤ 1 / 2) :
    Set.MapsTo (logarithmicZeroMap a t R) (closedBall t (1 / ‖a‖))
      (closedBall t (1 / ‖a‖)) := by
  intro z hz
  rw [mem_closedBall, dist_eq_norm, logarithmicZeroMap, add_sub_cancel_left, norm_div]
  apply (div_le_div_iff_of_pos_right (norm_pos_iff.mpr ha)).mpr
  have h := Complex.norm_log_one_add_half_le_self (hR z hz)
  linarith [hR z hz]

theorem logarithmicZeroMap_lipschitz {a t : ℂ} (ha : a ≠ 0) {R R' : ℂ → ℂ}
    (hR : ∀ z ∈ closedBall t (1 / ‖a‖), ‖R z‖ ≤ 1 / 2)
    (hd : ∀ z ∈ closedBall t (1 / ‖a‖), HasDerivAt R (R' z) z)
    (hb : ∀ z ∈ closedBall t (1 / ‖a‖), ‖R' z‖ ≤ ‖a‖ / 4) :
    LipschitzOnWith (1 / 2) (logarithmicZeroMap a t R) (closedBall t (1 / ‖a‖)) := by
  apply LipschitzOnWith.of_dist_le_mul
  intro x hx y hy
  have hxy := (convex_closedBall t (1 / ‖a‖)).norm_image_sub_le_of_norm_hasDerivWithin_le
    (fun z hz => (hd z hz).hasDerivWithinAt) hb hy hx
  have hl := log_one_add_lipschitz_half.dist_le_mul (R x)
    (by simpa [mem_closedBall, dist_eq_norm] using hR x hx) (R y)
    (by simpa [mem_closedBall, dist_eq_norm] using hR y hy)
  simp only [NNReal.coe_ofNat, dist_eq_norm] at hl
  simp only [dist_eq_norm, logarithmicZeroMap, add_sub_add_left_eq_sub,
    ← sub_div, norm_div, NNReal.coe_div, NNReal.coe_one, NNReal.coe_ofNat]
  apply (div_le_iff₀ (norm_pos_iff.mpr ha)).mpr
  nlinarith

theorem logarithmicZeroMap_fixed_iff {a t : ℂ} (ha : a ≠ 0)
    (ht : Complex.exp (a * t) = -1) {R : ℂ → ℂ}
    (hR : ∀ z ∈ closedBall t (1 / ‖a‖), ‖R z‖ ≤ 1 / 2)
    {z : ℂ} (hz : z ∈ closedBall t (1 / ‖a‖)) :
    logarithmicZeroMap a t R z = z ↔ 1 + Complex.exp (a * z) + R z = 0 := by
  have haN := norm_pos_iff.mpr ha
  have hnorm : ‖a * (z - t)‖ ≤ 1 := by
    rw [norm_mul]
    have hz' : ‖z - t‖ ≤ 1 / ‖a‖ := by simpa [mem_closedBall, dist_eq_norm] using hz
    calc _ ≤ ‖a‖ * (1 / ‖a‖) := mul_le_mul_of_nonneg_left hz' (norm_nonneg a)
         _ = 1 := by field_simp
  have he : Complex.exp (a * z) = -Complex.exp (a * (z - t)) := by
    rw [show a * z = a * t + a * (z - t) by ring, Complex.exp_add, ht]
    ring
  have hne : 1 + R z ≠ 0 := norm_pos_iff.mp
    (lt_of_lt_of_le (by norm_num) (norm_one_add_lower_half (hR z hz)))
  constructor
  · intro hf
    have hlog : Complex.log (1 + R z) = a * (z - t) := by
      unfold logarithmicZeroMap at hf
      field_simp at hf
      linear_combination hf
    have hh := Complex.exp_log hne
    rw [hlog] at hh
    rw [he, hh]
    ring
  · intro hf
    have hh : Complex.exp (a * (z - t)) = 1 + R z := by
      rw [he] at hf
      linear_combination -hf
    have hi : |(a * (z - t)).im| ≤ 1 :=
      (Complex.abs_im_le_norm _).trans hnorm
    have hl := Complex.log_exp (x := a * (z - t))
      (by have := (abs_le.mp hi).1; linarith [Real.two_le_pi])
      (by have := (abs_le.mp hi).2; linarith [Real.two_le_pi])
    rw [hh] at hl
    unfold logarithmicZeroMap
    rw [hl]
    field_simp
    ring

/-- A small differentiable remainder creates exactly one zero in the local disk. -/
theorem perturbed_exponential_unique_zero {a t : ℂ} (ha : a ≠ 0)
    (ht : Complex.exp (a * t) = -1) {R R' : ℂ → ℂ}
    (hR : ∀ z ∈ closedBall t (1 / ‖a‖), ‖R z‖ ≤ 1 / 2)
    (hd : ∀ z ∈ closedBall t (1 / ‖a‖), HasDerivAt R (R' z) z)
    (hb : ∀ z ∈ closedBall t (1 / ‖a‖), ‖R' z‖ ≤ ‖a‖ / 4) :
    ∃! z : ℂ, z ∈ closedBall t (1 / ‖a‖) ∧ 1 + Complex.exp (a * z) + R z = 0 := by
  have hm := logarithmicZeroMap_mapsTo ha hR
  have hl := logarithmicZeroMap_lipschitz ha hR hd hb
  have hc : ContractingWith (1 / 2) (hm.restrict (logarithmicZeroMap a t R)
      (closedBall t (1 / ‖a‖)) (closedBall t (1 / ‖a‖))) :=
    ⟨by norm_num, hl.mapsToRestrict hm⟩
  obtain ⟨z, hz, hf, _⟩ := ContractingWith.exists_fixedPoint'
    isClosed_closedBall.isComplete hm hc
    (show t ∈ closedBall t (1 / ‖a‖) by simp)
    (edist_ne_top t (logarithmicZeroMap a t R t))
  refine ⟨z, ⟨hz, (logarithmicZeroMap_fixed_iff ha ht hR hz).mp hf⟩, ?_⟩
  intro y hy
  have hfy := (logarithmicZeroMap_fixed_iff ha ht hR hy.1).mpr hy.2
  have hdist := hl.dist_le_mul y hy.1 z hz
  rw [hfy, hf] at hdist
  have hzero : dist y z = 0 := by
    simp only [NNReal.coe_div, NNReal.coe_one, NNReal.coe_ofNat] at hdist
    nlinarith [dist_nonneg (x := y) (y := z)]
  exact dist_eq_zero.mp hzero

/-- An explicit displacement bound for every zero in the local disk. -/
theorem perturbed_exponential_zero_distance {a t : ℂ} (ha : a ≠ 0)
    (ht : Complex.exp (a * t) = -1) {R : ℂ → ℂ} {ε : ℝ} (hε : ε ≤ 1 / 2)
    (hR : ∀ z ∈ closedBall t (1 / ‖a‖), ‖R z‖ ≤ ε)
    {z : ℂ} (hz : z ∈ closedBall t (1 / ‖a‖))
    (hzero : 1 + Complex.exp (a * z) + R z = 0) :
    ‖z - t‖ ≤ (3 / 2 : ℝ) * ε / ‖a‖ := by
  have hf := (logarithmicZeroMap_fixed_iff ha ht (fun w hw => (hR w hw).trans hε) hz).mpr hzero
  have he : z - t = Complex.log (1 + R z) / a := by
    unfold logarithmicZeroMap at hf
    linear_combination -hf
  rw [he, norm_div]
  apply div_le_div_of_nonneg_right _ (norm_nonneg a)
  exact (Complex.norm_log_one_add_half_le_self ((hR z hz).trans hε)).trans
    (mul_le_mul_of_nonneg_left (hR z hz) (by norm_num))

/-- The displacement estimate retains the actual remainder value at the zero. -/
theorem perturbed_exponential_pointwise_distance {a t : ℂ} (ha : a ≠ 0)
    (ht : Complex.exp (a * t) = -1) {R : ℂ → ℂ}
    (hR : ∀ z ∈ closedBall t (1 / ‖a‖), ‖R z‖ ≤ 1 / 2)
    {z : ℂ} (hz : z ∈ closedBall t (1 / ‖a‖))
    (hzero : 1 + Complex.exp (a * z) + R z = 0) :
    ‖z - t‖ ≤ (3 / 2 : ℝ) * ‖R z‖ / ‖a‖ := by
  have hf := (logarithmicZeroMap_fixed_iff ha ht hR hz).mpr hzero
  have he : z - t = Complex.log (1 + R z) / a := by
    unfold logarithmicZeroMap at hf
    linear_combination -hf
  rw [he, norm_div]
  exact div_le_div_of_nonneg_right (Complex.norm_log_one_add_half_le_self (hR z hz)) (norm_nonneg a)

theorem hasDerivAt_perturbed_exponential (a : ℂ) {R : ℂ → ℂ} {z Rz' : ℂ}
    (hd : HasDerivAt R Rz' z) :
    HasDerivAt (fun w => 1 + Complex.exp (a * w) + R w)
      (a * Complex.exp (a * z) + Rz') z := by
  have h := ((((hasDerivAt_id z).const_mul a).cexp).const_add 1).add hd
  have he : Complex.exp (a * id z) * (a * 1) + Rz' = a * Complex.exp (a * z) + Rz' := by
    simp only [id_eq, mul_one]
    ring
  rw [he] at h
  convert h using 1 <;> rfl

/-- The derivative cannot vanish at the localized zero. -/
theorem perturbed_exponential_zero_derivative_lower {a : ℂ} {R : ℂ → ℂ}
    {z Rz' : ℂ} (hzero : 1 + Complex.exp (a * z) + R z = 0)
    (hR : ‖R z‖ ≤ 1 / 2) (hb : ‖Rz'‖ ≤ ‖a‖ / 4) :
    ‖a‖ / 4 ≤ ‖a * Complex.exp (a * z) + Rz'‖ := by
  have he : Complex.exp (a * z) = -(1 + R z) := by linear_combination hzero
  have hn : ‖a‖ / 2 ≤ ‖a * Complex.exp (a * z)‖ := by
    rw [he, norm_mul, norm_neg]
    have := mul_le_mul_of_nonneg_left (norm_one_add_lower_half hR) (norm_nonneg a)
    linarith
  have h := norm_sub_norm_le (a * Complex.exp (a * z)) (-Rz')
  simp only [norm_neg, sub_neg_eq_add] at h
  linarith

/-- Analytic multiplicity one follows from the quantified derivative bound. -/
theorem perturbed_exponential_zero_order_one {a : ℂ} (ha : a ≠ 0)
    {R : ℂ → ℂ} {z : ℂ} (hRanalytic : AnalyticAt ℂ R z)
    (hzero : 1 + Complex.exp (a * z) + R z = 0)
    (hR : ‖R z‖ ≤ 1 / 2) (hb : ‖deriv R z‖ ≤ ‖a‖ / 4) :
    analyticOrderAt (fun w => 1 + Complex.exp (a * w) + R w) z = 1 := by
  have hf : AnalyticAt ℂ (fun w => 1 + Complex.exp (a * w) + R w) z := by fun_prop
  apply hf.analyticOrderAt_eq_one_of_zero_deriv_ne_zero hzero
  rw [(hasDerivAt_perturbed_exponential a hRanalytic.differentiableAt.hasDerivAt).deriv]
  apply norm_pos_iff.mp
  exact lt_of_lt_of_le (div_pos (norm_pos_iff.mpr ha) (by norm_num))
    (perturbed_exponential_zero_derivative_lower hzero hR hb)

/-- The derivative asymptotic is an exact finite error estimate at a zero. -/
theorem perturbed_exponential_derivative_error {a : ℂ} {R : ℂ → ℂ}
    {z Rz' : ℂ} (hzero : 1 + Complex.exp (a * z) + R z = 0) :
    ‖(a * Complex.exp (a * z) + Rz') + a‖ ≤ ‖a‖ * ‖R z‖ + ‖Rz'‖ := by
  have he : (a * Complex.exp (a * z) + Rz') + a = -(a * R z) + Rz' := by
    linear_combination a * hzero
  rw [he]
  simpa [norm_mul] using norm_add_le (-(a * R z)) Rz'

theorem norm_log_one_add_sub_self_half {u : ℂ} (hu : ‖u‖ ≤ 1 / 2) :
    ‖Complex.log (1 + u) - u‖ ≤ ‖u‖ ^ 2 := by
  have hinv : (1 - ‖u‖)⁻¹ ≤ 2 := by
    rw [inv_eq_one_div, div_le_iff₀ (by linarith)]
    linarith
  have h := Complex.norm_log_one_add_sub_self_le (lt_of_le_of_lt hu (by norm_num))
  nlinarith [mul_le_mul_of_nonneg_left hinv (sq_nonneg ‖u‖)]

/-- The leading displacement formula with an explicit quadratic error bound. -/
theorem perturbed_exponential_first_correction {a t : ℂ} (ha : a ≠ 0)
    (ht : Complex.exp (a * t) = -1) {R R' : ℂ → ℂ} {ε L : ℝ} (hε : ε ≤ 1 / 2)
    (hR : ∀ z ∈ closedBall t (1 / ‖a‖), ‖R z‖ ≤ ε)
    (hd : ∀ z ∈ closedBall t (1 / ‖a‖), HasDerivAt R (R' z) z)
    (hb : ∀ z ∈ closedBall t (1 / ‖a‖), ‖R' z‖ ≤ L)
    {z : ℂ} (hz : z ∈ closedBall t (1 / ‖a‖))
    (hzero : 1 + Complex.exp (a * z) + R z = 0) :
    ‖z - t - R t / a‖ ≤ (ε ^ 2 + L * ((3 / 2 : ℝ) * ε / ‖a‖)) / ‖a‖ := by
  have htmem : t ∈ closedBall t (1 / ‖a‖) := by simp
  have hL : 0 ≤ L := (norm_nonneg _).trans (hb t htmem)
  have hf := (logarithmicZeroMap_fixed_iff ha ht (fun w hw => (hR w hw).trans hε) hz).mpr hzero
  have he : z - t - R t / a = (Complex.log (1 + R z) - R t) / a := by
    unfold logarithmicZeroMap at hf
    linear_combination -hf
  rw [he, norm_div]
  apply div_le_div_of_nonneg_right _ (norm_nonneg a)
  have hlog := norm_log_one_add_sub_self_half ((hR z hz).trans hε)
  have hLip := (convex_closedBall t (1 / ‖a‖)).norm_image_sub_le_of_norm_hasDerivWithin_le
    (fun w hw => (hd w hw).hasDerivWithinAt) hb htmem hz
  have hdist := perturbed_exponential_zero_distance ha ht hε hR hz hzero
  calc
    _ ≤ ‖Complex.log (1 + R z) - R z‖ + ‖R z - R t‖ := norm_sub_le_norm_sub_add_norm_sub ..
    _ ≤ ε ^ 2 + L * ((3 / 2 : ℝ) * ε / ‖a‖) := by
      apply add_le_add
      · exact hlog.trans (pow_le_pow_left₀ (norm_nonneg _) (hR z hz) 2)
      · exact hLip.trans (mul_le_mul_of_nonneg_left hdist hL)

end
end Komorebi.PaperIV
