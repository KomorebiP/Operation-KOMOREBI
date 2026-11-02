import CoupledPositiveReal

/-! # Explicit lower logarithmic growth comparison

The argument uses closed finite caps and a positive real descent. It does
not require convexity of the power function or an exponent at least one.
-/

set_option autoImplicit false
set_option maxHeartbeats 2000000

noncomputable section

open Set
open scoped Topology Matrix

namespace Komorebi.SpecialFunctions.Coupled.Scales

def lowerShift (s : Scales) : ℝ := s.maxScale / (1 - s.maxScale)
def lowerDescent (s : Scales) : ℝ := (1 - s.maxScale) * s.lowerThreshold + s.maxScale
def lowerPowerConstant (s : Scales) (ρ : ℝ) : ℝ :=
  Real.log 2 / (s.lowerThreshold + s.lowerShift) ^ ρ

def LowerPowerAt (s : Scales) (ρ : ℝ) (w : Fin 2 → ℝ) (R : ℝ) : Prop :=
  s.lowerPowerConstant ρ * w 0 * (R + s.lowerShift) ^ ρ ≤ Real.log (s.UReal R) ∧
  s.lowerPowerConstant ρ * w 1 * (R + s.lowerShift) ^ ρ ≤ Real.log (s.VReal R)

theorem maxScale_positive (s : Scales) (hs : s.positive) : 0 < s.maxScale :=
  lt_of_lt_of_le hs.1 s.maxScale_bounds.1

theorem lowerShift_positive (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) : 0 < s.lowerShift :=
  div_pos (s.maxScale_positive hs) (sub_pos.mpr (s.maxScale_lt_one hstrict))

theorem lowerDescent_positive (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) : 0 < s.lowerDescent := by
  have hQ := s.maxScale_positive hs
  have hden := sub_pos.mpr (s.maxScale_lt_one hstrict)
  have hB : 0 < s.lowerThreshold := lt_trans (by norm_num) (s.lowerThreshold_gt_one hs)
  exact add_pos (mul_pos hden hB) hQ

theorem lowerPowerConstant_positive (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (ρ : ℝ) :
    0 < s.lowerPowerConstant ρ := by
  have hB : 0 < s.lowerThreshold := lt_trans (by norm_num) (s.lowerThreshold_gt_one hs)
  exact div_pos (Real.log_pos (by norm_num))
    (Real.rpow_pos_of_pos (add_pos hB (s.lowerShift_positive hs hstrict)) ρ)

theorem shifted_child_radius (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {p : ℝ} (hp : p ≤ s.maxScale) (R : ℝ) :
    p * (R + s.lowerShift) ≤ p * (R - 1) + s.lowerShift := by
  have hc := s.lowerShift_positive hs hstrict
  have hden := sub_pos.mpr (s.maxScale_lt_one hstrict)
  have he : (1 - s.maxScale) * s.lowerShift = s.maxScale := by
    dsimp [lowerShift]
    field_simp [ne_of_gt hden]
  have hm : 0 ≤ (s.maxScale - p) * (1 + s.lowerShift) :=
    mul_nonneg (sub_nonneg.mpr hp) (by linarith)
  nlinarith only [he, hm]

theorem child_radius_descent (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {p R : ℝ} (hp : p ≤ s.maxScale) (hR : s.lowerThreshold ≤ R) :
    p * (R - 1) ≤ R - s.lowerDescent := by
  have hR0 : 0 ≤ R - 1 := by linarith [s.lowerThreshold_gt_one hs]
  have hm := mul_le_mul_of_nonneg_right hp hR0
  have hn := mul_nonneg (sub_pos.mpr (s.maxScale_lt_one hstrict)).le (sub_nonneg.mpr hR)
  dsimp [lowerDescent]
  nlinarith only [hm, hn]

theorem real_radius_descent_induction {P : ℝ → Prop} {B d : ℝ} (hd : 0 < d)
    (hseed : ∀ R, 2 ≤ R → R ≤ B → P R)
    (hstep : ∀ R, 2 ≤ R → B < R → (∀ y, 2 ≤ y → y ≤ R - d → P y) → P R) :
    ∀ R, 2 ≤ R → P R := by
  have hcap : ∀ n : ℕ, ∀ R : ℝ, 2 ≤ R → R ≤ B + (n : ℝ) * d → P R := by
    intro n
    induction n with
    | zero =>
      intro R hR hcap
      exact hseed R hR (by simpa only [Nat.cast_zero, zero_mul, add_zero] using hcap)
    | succ n ih =>
      intro R hR hcap
      by_cases hRB : R ≤ B
      · exact hseed R hR hRB
      · apply hstep R hR (lt_of_not_ge hRB)
        intro y hy hyd
        apply ih y hy
        simp only [Nat.cast_succ] at hcap
        nlinarith only [hyd, hcap]
  intro R hR
  obtain ⟨n, hn⟩ := exists_nat_gt ((R - B) / d)
  have hnR : R ≤ B + (n : ℝ) * d := by
    have h := (div_lt_iff₀ hd).mp hn
    linarith only [h]
  exact hcap n R hR hnR

theorem lower_power_seed (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {ρ : ℝ} (hρ : 0 < ρ) {w : Fin 2 → ℝ} (hw : ∀ i, w i ≤ 1)
    {R : ℝ} (hR : 2 ≤ R) (hRB : R ≤ s.lowerThreshold) : s.LowerPowerAt ρ w R := by
  have hc := s.lowerPowerConstant_positive hs hstrict ρ
  have hC := s.lowerShift_positive hs hstrict
  have hR0 : 0 < R := by linarith
  have hB : 0 < s.lowerThreshold + s.lowerShift := by linarith [s.lowerThreshold_gt_one hs]
  have hpR := Real.rpow_pos_of_pos (by linarith : 0 < R + s.lowerShift) ρ
  have hpB := Real.rpow_pos_of_pos hB ρ
  have hRB' : R + s.lowerShift ≤ s.lowerThreshold + s.lowerShift := by linarith only [hRB]
  have hp := Real.rpow_le_rpow (by linarith : 0 ≤ R + s.lowerShift)
    hRB' hρ.le
  have he : s.lowerPowerConstant ρ * (s.lowerThreshold + s.lowerShift) ^ ρ = Real.log 2 := by
    exact div_mul_cancel₀ _ (ne_of_gt hpB)
  have ht (i : Fin 2) : s.lowerPowerConstant ρ * w i * (R + s.lowerShift) ^ ρ ≤ Real.log 2 := by
    calc
      _ ≤ s.lowerPowerConstant ρ * 1 * (R + s.lowerShift) ^ ρ :=
        mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left (hw i) hc.le) hpR.le
      _ = s.lowerPowerConstant ρ * (R + s.lowerShift) ^ ρ := by ring
      _ ≤ s.lowerPowerConstant ρ * (s.lowerThreshold + s.lowerShift) ^ ρ :=
        mul_le_mul_of_nonneg_left hp hc.le
      _ = Real.log 2 := he
  have hl := s.real_axis_lower_linear hs hstrict hR0.le
  have hlog := Real.log_le_log (by norm_num : (0 : ℝ) < 2) hR
  exact ⟨(ht 0).trans (hlog.trans (Real.log_le_log hR0 hl.1)),
    (ht 1).trans (hlog.trans (Real.log_le_log hR0 hl.2))⟩

theorem lower_power_step (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {ρ : ℝ} (hρ : 0 < ρ) {w : Fin 2 → ℝ} (hw : ∀ i, 0 ≤ w i)
    (he : s.characteristicMatrix ρ *ᵥ w = w) {R : ℝ} (hR : 2 ≤ R)
    (hBR : s.lowerThreshold < R)
    (hIH : ∀ y, 2 ≤ y → y ≤ R - s.lowerDescent → s.LowerPowerAt ρ w y) :
    s.LowerPowerAt ρ w R := by
  have hc := s.lowerPowerConstant_positive hs hstrict ρ
  have hC := s.lowerShift_positive hs hstrict
  have hRp : 0 ≤ R + s.lowerShift := by linarith
  have hb := s.maxScale_bounds
  have hk := s.lower_child_radii hs hBR.le
  have hq := hIH (s.q * (R - 1)) hk.1 (s.child_radius_descent hs hstrict hb.1 hBR.le)
  have hr := hIH (s.r * (R - 1)) hk.2.1 (s.child_radius_descent hs hstrict hb.2.1 hBR.le)
  have ha := hIH (s.a * (R - 1)) hk.2.2.1 (s.child_radius_descent hs hstrict hb.2.2.1 hBR.le)
  have hB := hIH (s.b * (R - 1)) hk.2.2.2 (s.child_radius_descent hs hstrict hb.2.2.2 hBR.le)
  have hscale (p : ℝ) (hp0 : 0 ≤ p) (hpQ : p ≤ s.maxScale) (i : Fin 2) :
      s.lowerPowerConstant ρ * w i * (p ^ ρ * (R + s.lowerShift) ^ ρ) ≤
        s.lowerPowerConstant ρ * w i * (p * (R - 1) + s.lowerShift) ^ ρ := by
    have hp := Real.rpow_le_rpow (mul_nonneg hp0 hRp)
      (s.shifted_child_radius hs hstrict hpQ R) hρ.le
    rw [Real.mul_rpow hp0 hRp] at hp
    exact mul_le_mul_of_nonneg_left hp (mul_nonneg hc.le (hw i))
  have hlog := s.real_axis_log_unit_lower hs hstrict
    (lt_trans (s.lowerThreshold_gt_one hs) hBR)
  have hu := (add_le_add ((hscale s.q hs.1.le hb.1 0).trans hq.1)
    ((hscale s.r hs.2.1.le hb.2.1 1).trans hr.2)).trans hlog.1
  have hv := (add_le_add ((hscale s.a hs.2.2.1.le hb.2.2.1 0).trans ha.1)
    ((hscale s.b hs.2.2.2.le hb.2.2.2 1).trans hB.2)).trans hlog.2
  have he0 := congrFun he 0
  have he1 := congrFun he 1
  norm_num [characteristicMatrix, Matrix.mulVec, dotProduct, Fin.sum_univ_two] at he0 he1
  have h0 := congrArg (fun x : ℝ => s.lowerPowerConstant ρ * x * (R + s.lowerShift) ^ ρ) he0
  have h1 := congrArg (fun x : ℝ => s.lowerPowerConstant ρ * x * (R + s.lowerShift) ^ ρ) he1
  constructor
  · nlinarith only [hu, h0]
  · nlinarith only [hv, h1]

theorem coupled_lower_log_power (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {ρ : ℝ} (hρ : 0 < ρ) {w : Fin 2 → ℝ} (hw0 : ∀ i, 0 ≤ w i)
    (hw1 : ∀ i, w i ≤ 1) (he : s.characteristicMatrix ρ *ᵥ w = w) :
    ∀ R, 2 ≤ R → s.LowerPowerAt ρ w R := by
  exact real_radius_descent_induction (P := fun R => s.LowerPowerAt ρ w R)
    (B := s.lowerThreshold) (d := s.lowerDescent) (s.lowerDescent_positive hs hstrict)
    (fun R hR hRB => s.lower_power_seed hs hstrict hρ hw1 hR hRB)
    (fun R hR hBR hIH => s.lower_power_step hs hstrict hρ hw0 he hR hBR hIH)

theorem normalizedCharacteristicVector_le_one (s : Scales) (hs : s.positive)
    (hq : s.q < 1) {ρ : ℝ} (hρ : 0 < ρ) (i : Fin 2) :
    s.normalizedCharacteristicVector ρ i ≤ 1 := by
  have hm := s.normalizedCharacteristicVector_max hs hq hρ
  fin_cases i
  · exact (le_max_left _ _).trans hm.le
  · exact (le_max_right _ _).trans hm.le

theorem canonical_lower_log_power (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : 2 ≤ R) :
    s.LowerPowerAt (s.characteristicExponent hs hstrict)
      (s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict)) R := by
  have hρ := s.characteristicExponent_spec hs hstrict
  exact s.coupled_lower_log_power hs hstrict hρ.1
    (fun i => (s.normalizedCharacteristicVector_positive hs hstrict.1 hρ.1 i).le)
    (s.normalizedCharacteristicVector_le_one hs hstrict.1 hρ.1)
    (s.normalized_characteristic_eigenvector hs hρ.2) R hR

theorem lower_log_power_ratio (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {ρ : ℝ} (hρ : 0 < ρ) {w : Fin 2 → ℝ} (hw : ∀ i, 0 ≤ w i)
    {R : ℝ} (hR : 2 ≤ R) (hL : s.LowerPowerAt ρ w R) :
    s.lowerPowerConstant ρ * w 0 ≤ Real.log (s.UReal R) / R ^ ρ ∧
    s.lowerPowerConstant ρ * w 1 ≤ Real.log (s.VReal R) / R ^ ρ := by
  have hc := s.lowerPowerConstant_positive hs hstrict ρ
  have hC := s.lowerShift_positive hs hstrict
  have hR0 : 0 < R := by linarith
  have hpR := Real.rpow_pos_of_pos hR0 ρ
  have hp := Real.rpow_le_rpow hR0.le (by linarith : R ≤ R + s.lowerShift) hρ.le
  constructor
  · apply (le_div_iff₀ hpR).mpr
    exact (mul_le_mul_of_nonneg_left hp (mul_nonneg hc.le (hw 0))).trans hL.1
  · apply (le_div_iff₀ hpR).mpr
    exact (mul_le_mul_of_nonneg_left hp (mul_nonneg hc.le (hw 1))).trans hL.2

def canonicalLowerCoefficient (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) : ℝ :=
  s.lowerPowerConstant (s.characteristicExponent hs hstrict) *
    s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) i

theorem canonicalLowerCoefficient_positive (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    0 < s.canonicalLowerCoefficient hs hstrict i :=
  mul_pos (s.lowerPowerConstant_positive hs hstrict _)
    (s.normalizedCharacteristicVector_positive hs hstrict.1
      (s.characteristicExponent_spec hs hstrict).1 i)

theorem canonical_lower_growth_ratio (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : 2 ≤ R) :
    s.canonicalLowerCoefficient hs hstrict 0 ≤
      Real.log (s.UReal R) / R ^ (s.characteristicExponent hs hstrict) ∧
    s.canonicalLowerCoefficient hs hstrict 1 ≤
      Real.log (s.VReal R) / R ^ (s.characteristicExponent hs hstrict) := by
  have hρ := s.characteristicExponent_spec hs hstrict
  exact s.lower_log_power_ratio hs hstrict hρ.1
    (fun i => (s.normalizedCharacteristicVector_positive hs hstrict.1 hρ.1 i).le)
    hR (s.canonical_lower_log_power hs hstrict hR)

theorem canonical_lower_norm_power (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : 2 ≤ R) :
    s.canonicalLowerCoefficient hs hstrict 0 *
      (R + s.lowerShift) ^ (s.characteristicExponent hs hstrict) ≤ Real.log ‖s.U (R : ℂ)‖ ∧
    s.canonicalLowerCoefficient hs hstrict 1 *
      (R + s.lowerShift) ^ (s.characteristicExponent hs hstrict) ≤ Real.log ‖s.V (R : ℂ)‖ := by
  have he := s.real_axis_norm hs hstrict (by linarith : 0 ≤ R)
  rw [he.1, he.2]
  exact s.canonical_lower_log_power hs hstrict hR

end Komorebi.SpecialFunctions.Coupled.Scales
