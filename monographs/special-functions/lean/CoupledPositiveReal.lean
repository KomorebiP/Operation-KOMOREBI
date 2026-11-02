import CoupledCharacteristic
import Mathlib.Analysis.Complex.RealDeriv
import Mathlib.Analysis.Calculus.Deriv.MeanValue

/-! # Positive-real comparisons for the coupled canonical functions

All ordered inequalities concern real-valued restrictions. The complex
functions are identified with their embeddings on the real axis.
-/

set_option autoImplicit false
set_option maxHeartbeats 1500000

noncomputable section

open Filter Set
open scoped Topology

namespace Komorebi.SpecialFunctions.Coupled.Scales

def UReal (s : Scales) (x : ℝ) : ℝ := (s.U (x : ℂ)).re
def VReal (s : Scales) (x : ℝ) : ℝ := (s.V (x : ℂ)).re

theorem real_series_hasSum (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (x : ℝ) :
    HasSum (fun n => (s.coefficients n).1 * x ^ (2 * n + 1)) (s.UReal x) ∧
    HasSum (fun n => (s.coefficients n).2 * x ^ (2 * n + 1)) (s.VReal x) := by
  have h := s.coefficient_series_entire hs hstrict (x : ℂ)
  constructor
  · simpa only [UReal, U, oddSum, ← Complex.ofReal_pow, ← Complex.ofReal_mul, Complex.ofReal_re] using
      Complex.hasSum_re h.1.of_norm.hasSum
  · simpa only [VReal, V, oddSum, ← Complex.ofReal_pow, ← Complex.ofReal_mul, Complex.ofReal_re] using
      Complex.hasSum_re h.2.of_norm.hasSum

theorem real_axis_identification (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (x : ℝ) :
    s.U (x : ℂ) = (s.UReal x : ℂ) ∧ s.V (x : ℂ) = (s.VReal x : ℂ) := by
  have h := s.coefficient_series_entire hs hstrict (x : ℂ)
  have hr := s.real_series_hasSum hs hstrict x
  constructor
  · exact h.1.of_norm.hasSum.unique (by
      simpa only [Complex.ofReal_mul, Complex.ofReal_pow] using Complex.hasSum_ofReal.mpr hr.1)
  · exact h.2.of_norm.hasSum.unique (by
      simpa only [Complex.ofReal_mul, Complex.ofReal_pow] using Complex.hasSum_ofReal.mpr hr.2)

theorem real_axis_zero (s : Scales) : s.UReal 0 = 0 ∧ s.VReal 0 = 0 := by
  simp [UReal, VReal, U, V, oddSum]

theorem real_axis_nonneg (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {x : ℝ} (hx : 0 ≤ x) :
    0 ≤ s.UReal x ∧ 0 ≤ s.VReal x := by
  have h := s.real_series_hasSum hs hstrict x
  constructor
  · rw [← h.1.tsum_eq]
    exact tsum_nonneg fun n => mul_nonneg (s.coefficients_positive hs n).1.le (pow_nonneg hx _)
  · rw [← h.2.tsum_eq]
    exact tsum_nonneg fun n => mul_nonneg (s.coefficients_positive hs n).2.le (pow_nonneg hx _)

theorem real_axis_lower_linear (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {x : ℝ} (hx : 0 ≤ x) :
    x ≤ s.UReal x ∧ x ≤ s.VReal x := by
  have h := s.real_series_hasSum hs hstrict x
  constructor
  · simpa [coefficients_zero] using
      le_hasSum h.1 0 (fun n _ => mul_nonneg (s.coefficients_positive hs n).1.le (pow_nonneg hx _))
  · simpa [coefficients_zero] using
      le_hasSum h.2 0 (fun n _ => mul_nonneg (s.coefficients_positive hs n).2.le (pow_nonneg hx _))

theorem real_axis_hasDerivAt (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (x : ℝ) :
    HasDerivAt s.UReal (1 + s.UReal (s.q * x) * s.VReal (s.r * x)) x ∧
    HasDerivAt s.VReal (1 + s.UReal (s.a * x) * s.VReal (s.b * x)) x := by
  have h := (s.coupled_entire_solution hs hstrict).2.2 (x : ℂ)
  constructor
  · apply h.1.real_of_complex.congr_deriv
    rw [← Complex.ofReal_mul, ← Complex.ofReal_mul,
      (s.real_axis_identification hs hstrict (s.q * x)).1,
      (s.real_axis_identification hs hstrict (s.r * x)).2]
    simp
  · apply h.2.real_of_complex.congr_deriv
    rw [← Complex.ofReal_mul, ← Complex.ofReal_mul,
      (s.real_axis_identification hs hstrict (s.a * x)).1,
      (s.real_axis_identification hs hstrict (s.b * x)).2]
    simp

theorem real_axis_differentiable (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    Differentiable ℝ s.UReal ∧ Differentiable ℝ s.VReal :=
  ⟨fun x => (s.real_axis_hasDerivAt hs hstrict x).1.differentiableAt,
    fun x => (s.real_axis_hasDerivAt hs hstrict x).2.differentiableAt⟩

theorem real_axis_deriv_ge_one (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {x : ℝ} (hx : 0 ≤ x) :
    1 ≤ deriv s.UReal x ∧ 1 ≤ deriv s.VReal x := by
  rw [(s.real_axis_hasDerivAt hs hstrict x).1.deriv,
    (s.real_axis_hasDerivAt hs hstrict x).2.deriv]
  have hq := s.real_axis_nonneg hs hstrict (mul_nonneg hs.1.le hx)
  have hr := s.real_axis_nonneg hs hstrict (mul_nonneg hs.2.1.le hx)
  have ha := s.real_axis_nonneg hs hstrict (mul_nonneg hs.2.2.1.le hx)
  have hb := s.real_axis_nonneg hs hstrict (mul_nonneg hs.2.2.2.le hx)
  constructor
  · linarith [mul_nonneg hq.1 hr.2]
  · linarith [mul_nonneg ha.1 hb.2]

theorem real_axis_strictMono (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    StrictMonoOn s.UReal (Ici 0) ∧ StrictMonoOn s.VReal (Ici 0) := by
  have hd := s.real_axis_differentiable hs hstrict
  constructor
  · apply strictMonoOn_of_deriv_pos (convex_Ici 0) hd.1.continuous.continuousOn
    intro x hx
    have hx0 : 0 ≤ x := interior_subset hx
    linarith [(s.real_axis_deriv_ge_one hs hstrict hx0).1]
  · apply strictMonoOn_of_deriv_pos (convex_Ici 0) hd.2.continuous.continuousOn
    intro x hx
    have hx0 : 0 ≤ x := interior_subset hx
    linarith [(s.real_axis_deriv_ge_one hs hstrict hx0).2]

theorem real_axis_log_positive (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {x : ℝ} (hx : 1 < x) :
    0 < Real.log (s.UReal x) ∧ 0 < Real.log (s.VReal x) := by
  have h := s.real_axis_lower_linear hs hstrict (by linarith : 0 ≤ x)
  exact ⟨Real.log_pos (lt_of_lt_of_le hx h.1), Real.log_pos (lt_of_lt_of_le hx h.2)⟩

theorem odd_series_norm_le_real_sum {c : ℕ → ℝ} {z A : ℂ} {R F : ℝ}
    (hc : ∀ n, 0 ≤ c n) (hz : ‖z‖ ≤ R)
    (hA : HasSum (fun n => (c n : ℂ) * z ^ (2 * n + 1)) A)
    (hF : HasSum (fun n => c n * R ^ (2 * n + 1)) F) : ‖A‖ ≤ F := by
  apply hA.norm_le_of_bounded hF
  intro n
  rw [norm_mul, Complex.norm_of_nonneg (hc n), norm_pow]
  exact mul_le_mul_of_nonneg_left (pow_le_pow_left₀ (norm_nonneg z) hz _) (hc n)

theorem complex_norm_le_real_axis (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {z : ℂ} {R : ℝ} (hz : ‖z‖ ≤ R) :
    ‖s.U z‖ ≤ s.UReal R ∧ ‖s.V z‖ ≤ s.VReal R := by
  have h := s.coefficient_series_entire hs hstrict z
  have hr := s.real_series_hasSum hs hstrict R
  exact ⟨odd_series_norm_le_real_sum (fun n => (s.coefficients_positive hs n).1.le) hz
      h.1.of_norm.hasSum hr.1,
    odd_series_norm_le_real_sum (fun n => (s.coefficients_positive hs n).2.le) hz
      h.2.of_norm.hasSum hr.2⟩

theorem real_axis_norm (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : 0 ≤ R) :
    ‖s.U (R : ℂ)‖ = s.UReal R ∧ ‖s.V (R : ℂ)‖ = s.VReal R := by
  have he := s.real_axis_identification hs hstrict R
  have hp := s.real_axis_nonneg hs hstrict hR
  rw [he.1, he.2]
  exact ⟨Complex.norm_of_nonneg hp.1, Complex.norm_of_nonneg hp.2⟩

theorem sphere_norm_isGreatest {f : ℂ → ℂ} {R F : ℝ} (hR : 0 ≤ R)
    (he : ‖f (R : ℂ)‖ = F) (hb : ∀ z, ‖z‖ ≤ R → ‖f z‖ ≤ F) :
    IsGreatest ((fun z => ‖f z‖) '' Metric.sphere (0 : ℂ) R) F := by
  constructor
  · refine ⟨(R : ℂ), ?_, he⟩
    simpa using hR
  · rintro y ⟨z, hz, rfl⟩
    have hzR : ‖z‖ = R := by simpa only [Metric.mem_sphere, dist_zero_right] using hz
    exact hb z hzR.le

theorem maximum_modulus_real_axis (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : 0 ≤ R) :
    IsGreatest ((fun z => ‖s.U z‖) '' Metric.sphere (0 : ℂ) R) (s.UReal R) ∧
    IsGreatest ((fun z => ‖s.V z‖) '' Metric.sphere (0 : ℂ) R) (s.VReal R) := by
  have he := s.real_axis_norm hs hstrict hR
  exact ⟨sphere_norm_isGreatest hR he.1 (fun z hz => (s.complex_norm_le_real_axis hs hstrict hz).1),
    sphere_norm_isGreatest hR he.2 (fun z hz => (s.complex_norm_le_real_axis hs hstrict hz).2)⟩

/-- Mean-value comparison on a unit interval; inequalities stay in the real field. -/
theorem unit_shift_lower_from_deriv {f g h : ℝ → ℝ} {p q R : ℝ}
    (hf : Differentiable ℝ f) (hf0 : ∀ x, 0 ≤ x → 0 ≤ f x)
    (hg0 : ∀ x, 0 ≤ x → 0 ≤ g x) (hh0 : ∀ x, 0 ≤ x → 0 ≤ h x)
    (hgm : MonotoneOn g (Ici 0)) (hhm : MonotoneOn h (Ici 0))
    (hd : ∀ x, deriv f x = 1 + g (p * x) * h (q * x))
    (hp : 0 ≤ p) (hq : 0 ≤ q) (hR : 1 ≤ R) :
    g (p * (R - 1)) * h (q * (R - 1)) ≤ f R := by
  have hR0 : 0 ≤ R - 1 := by linarith
  have hbound : ∀ x ∈ interior (Icc (R - 1) R),
      g (p * (R - 1)) * h (q * (R - 1)) ≤ deriv f x := by
    intro x hx
    have hxI : x ∈ Icc (R - 1) R := interior_subset hx
    have hx0 : 0 ≤ x := le_trans hR0 hxI.1
    have hgp := hgm (mul_nonneg hp hR0) (mul_nonneg hp hx0)
      (mul_le_mul_of_nonneg_left hxI.1 hp)
    have hhq := hhm (mul_nonneg hq hR0) (mul_nonneg hq hx0)
      (mul_le_mul_of_nonneg_left hxI.1 hq)
    have hm := mul_le_mul hgp hhq (hh0 _ (mul_nonneg hq hR0)) (hg0 _ (mul_nonneg hp hx0))
    rw [hd x]
    linarith only [hm]
  have hcomp := (convex_Icc (R - 1) R).mul_sub_le_image_sub_of_le_deriv
    hf.continuous.continuousOn hf.differentiableOn hbound
    (R - 1) ⟨le_rfl, by linarith⟩ R ⟨by linarith, le_rfl⟩ (by linarith)
  have hn := hf0 (R - 1) hR0
  nlinarith only [hcomp, hn]

theorem real_axis_unit_lower (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : 1 ≤ R) :
    s.UReal (s.q * (R - 1)) * s.VReal (s.r * (R - 1)) ≤ s.UReal R ∧
    s.UReal (s.a * (R - 1)) * s.VReal (s.b * (R - 1)) ≤ s.VReal R := by
  have hd := s.real_axis_differentiable hs hstrict
  have hm := s.real_axis_strictMono hs hstrict
  have hu0 : ∀ x : ℝ, 0 ≤ x → 0 ≤ s.UReal x :=
    fun x hx => (s.real_axis_nonneg hs hstrict hx).1
  have hv0 : ∀ x : ℝ, 0 ≤ x → 0 ≤ s.VReal x :=
    fun x hx => (s.real_axis_nonneg hs hstrict hx).2
  exact ⟨unit_shift_lower_from_deriv hd.1 hu0 hu0 hv0 hm.1.monotoneOn hm.2.monotoneOn
      (fun x => (s.real_axis_hasDerivAt hs hstrict x).1.deriv) hs.1.le hs.2.1.le hR,
    unit_shift_lower_from_deriv hd.2 hv0 hu0 hv0 hm.1.monotoneOn hm.2.monotoneOn
      (fun x => (s.real_axis_hasDerivAt hs hstrict x).2.deriv) hs.2.2.1.le hs.2.2.2.le hR⟩

theorem real_axis_log_unit_lower (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : 1 < R) :
    Real.log (s.UReal (s.q * (R - 1))) + Real.log (s.VReal (s.r * (R - 1))) ≤
      Real.log (s.UReal R) ∧
    Real.log (s.UReal (s.a * (R - 1))) + Real.log (s.VReal (s.b * (R - 1))) ≤
      Real.log (s.VReal R) := by
  have hp : 0 < R - 1 := by linarith
  have hq0 := mul_pos hs.1 hp
  have hr0 := mul_pos hs.2.1 hp
  have ha0 := mul_pos hs.2.2.1 hp
  have hb0 := mul_pos hs.2.2.2 hp
  have huq := lt_of_lt_of_le hq0 (s.real_axis_lower_linear hs hstrict hq0.le).1
  have hvr := lt_of_lt_of_le hr0 (s.real_axis_lower_linear hs hstrict hr0.le).2
  have hua := lt_of_lt_of_le ha0 (s.real_axis_lower_linear hs hstrict ha0.le).1
  have hvb := lt_of_lt_of_le hb0 (s.real_axis_lower_linear hs hstrict hb0.le).2
  have hc := s.real_axis_unit_lower hs hstrict hR.le
  have h1 := Real.log_le_log (mul_pos huq hvr) hc.1
  have h2 := Real.log_le_log (mul_pos hua hvb) hc.2
  rw [Real.log_mul (ne_of_gt huq) (ne_of_gt hvr)] at h1
  rw [Real.log_mul (ne_of_gt hua) (ne_of_gt hvb)] at h2
  exact ⟨h1, h2⟩

def minScale (s : Scales) : ℝ := min (min s.q s.r) (min s.a s.b)
def lowerThreshold (s : Scales) : ℝ := 1 + 2 / s.minScale

theorem minScale_bounds (s : Scales) :
    s.minScale ≤ s.q ∧ s.minScale ≤ s.r ∧ s.minScale ≤ s.a ∧ s.minScale ≤ s.b := by
  exact ⟨(min_le_left _ _).trans (min_le_left _ _),
    (min_le_left _ _).trans (min_le_right _ _),
    (min_le_right _ _).trans (min_le_left _ _),
    (min_le_right _ _).trans (min_le_right _ _)⟩

theorem minScale_positive (s : Scales) (hs : s.positive) : 0 < s.minScale :=
  lt_min (lt_min hs.1 hs.2.1) (lt_min hs.2.2.1 hs.2.2.2)

theorem lowerThreshold_gt_one (s : Scales) (hs : s.positive) : 1 < s.lowerThreshold := by
  have hm := s.minScale_positive hs
  dsimp [lowerThreshold]
  linarith [div_pos (by norm_num : (0 : ℝ) < 2) hm]

theorem lower_child_radii (s : Scales) (hs : s.positive) {R : ℝ} (hR : s.lowerThreshold ≤ R) :
    2 ≤ s.q * (R - 1) ∧ 2 ≤ s.r * (R - 1) ∧
    2 ≤ s.a * (R - 1) ∧ 2 ≤ s.b * (R - 1) := by
  have hm := s.minScale_positive hs
  have hR0 : 0 ≤ R - 1 := by linarith [s.lowerThreshold_gt_one hs]
  have hdiv : 2 / s.minScale ≤ R - 1 := by dsimp [lowerThreshold] at hR; linarith
  have htwo : 2 ≤ s.minScale * (R - 1) := by
    calc
      2 = s.minScale * (2 / s.minScale) := by field_simp [ne_of_gt hm]
      _ ≤ s.minScale * (R - 1) := mul_le_mul_of_nonneg_left hdiv hm.le
  have hb := s.minScale_bounds
  exact ⟨htwo.trans (mul_le_mul_of_nonneg_right hb.1 hR0),
    htwo.trans (mul_le_mul_of_nonneg_right hb.2.1 hR0),
    htwo.trans (mul_le_mul_of_nonneg_right hb.2.2.1 hR0),
    htwo.trans (mul_le_mul_of_nonneg_right hb.2.2.2 hR0)⟩

end Komorebi.SpecialFunctions.Coupled.Scales
