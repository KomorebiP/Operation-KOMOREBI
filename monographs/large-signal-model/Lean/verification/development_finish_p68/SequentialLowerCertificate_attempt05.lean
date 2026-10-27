import Mathlib.MeasureTheory.VectorMeasure.Integral
import Mathlib.MeasureTheory.VectorMeasure.Variation.SignedMeasure
import Mathlib.MeasureTheory.Integral.IntegrableOn
import Mathlib.Tactic

set_option autoImplicit false

/-!
# Sequential lower discrepancy certificate

The law distance is the probability convention for total variation: one half
the total mass of the variation of the actual signed measure `P - Q`.
The observation space is an arbitrary measurable space. The certificate is
conditional on the simultaneous residual event of Proposition 66; no new
concentration statement is assumed or asserted here.
-/
namespace Komorebi.LSM.SequentialLowerCertificate

noncomputable section

open MeasureTheory Set
open scoped ENNReal BigOperators

variable {Ω : Type*} [MeasurableSpace Ω]

/-- Standard total variation distance between finite probability laws. -/
def lawTV (P Q : Measure Ω) [IsProbabilityMeasure P] [IsProbabilityMeasure Q] : ℝ :=
  (1 / 2 : ℝ) * (P.toSignedMeasure - Q.toSignedMeasure).totalVariation.real univ

/-- The probability convention gives a nonnegative law discrepancy. -/
theorem lawTV_nonneg (P Q : Measure Ω) [IsProbabilityMeasure P] [IsProbabilityMeasure Q] :
    0 ≤ lawTV P Q := by
  exact mul_nonneg (by norm_num) ENNReal.toReal_nonneg

/-- Identical laws have zero discrepancy. -/
theorem lawTV_self (P : Measure Ω) [IsProbabilityMeasure P] : lawTV P P = 0 := by
  simp [lawTV, SignedMeasure.totalVariation_zero]

/-- Two probability laws have total variation at most one. -/
theorem lawTV_le_one (P Q : Measure Ω)
    [IsProbabilityMeasure P] [IsProbabilityMeasure Q] : lawTV P Q ≤ 1 := by
  have hle := VectorMeasure.variation_sub_le (μ := P.toSignedMeasure) (ν := Q.toSignedMeasure)
  have hset : (P.toSignedMeasure - Q.toSignedMeasure).totalVariation univ ≤ (2 : ℝ≥0∞) := by
    rw [SignedMeasure.totalVariation_eq_variation]
    simpa only [Measure.variation_toSignedMeasure, Measure.add_apply, measure_univ] using hle univ
  have hr := ENNReal.toReal_mono (by norm_num : (2 : ℝ≥0∞) ≠ ⊤) hset
  norm_num only [ENNReal.toReal_ofNat] at hr
  dsimp [lawTV, Measure.real]
  linarith

/-- A measurable test bounded in `[0,1]` is integrable under a probability law. -/
theorem bounded_test_integrable (P : Measure Ω) [IsProbabilityMeasure P]
    (φ : Ω → ℝ) (hφ : Measurable φ) (h0 : ∀ x, 0 ≤ φ x) (h1 : ∀ x, φ x ≤ 1) :
    Integrable φ P := by
  apply Integrable.of_bound hφ.aestronglyMeasurable 1
  exact ae_of_all P (fun x => by rw [Real.norm_eq_abs, abs_of_nonneg (h0 x)]; exact h1 x)

/-- Actual bounded-test integral discrepancy is controlled by actual total variation. -/
theorem bounded_test_integral_le_tv (P Q : Measure Ω)
    [IsProbabilityMeasure P] [IsProbabilityMeasure Q]
    (φ : Ω → ℝ) (hφ : Measurable φ) (h0 : ∀ x, 0 ≤ φ x) (h1 : ∀ x, φ x ≤ 1) :
    |(∫ x, φ x ∂P) - (∫ x, φ x ∂Q)| ≤ lawTV P Q := by
  let s : SignedMeasure Ω := P.toSignedMeasure - Q.toSignedMeasure
  have : IsFiniteMeasure s.variation := by
    rw [← s.totalVariation_eq_variation]
    infer_instance
  have hp := bounded_test_integrable P φ hφ h0 h1
  have hq := bounded_test_integrable Q φ hφ h0 h1
  have hpc : P.toSignedMeasure.Integrable (fun x => φ x - (1 / 2 : ℝ)) := by
    simpa only [VectorMeasure.Integrable, Measure.variation_toSignedMeasure] using
      hp.sub' (integrable_const (1 / 2 : ℝ))
  have hqc : Q.toSignedMeasure.Integrable (fun x => φ x - (1 / 2 : ℝ)) := by
    simpa only [VectorMeasure.Integrable, Measure.variation_toSignedMeasure] using
      hq.sub' (integrable_const (1 / 2 : ℝ))
  have hid : (∫ᵛ x, (φ x - (1 / 2 : ℝ)) ∂<•s) =
      (∫ x, φ x ∂P) - (∫ x, φ x ∂Q) := by
    change (∫ᵛ x, (φ x - (1 / 2 : ℝ)) ∂<•(P.toSignedMeasure - Q.toSignedMeasure)) = _
    rw [VectorMeasure.integral_sub_vectorMeasure hpc hqc]
    simp only [VectorMeasure.integral_toSignedMeasure,
      integral_sub hp (integrable_const (1 / 2 : ℝ)),
      integral_sub hq (integrable_const (1 / 2 : ℝ)), integral_const,
      Measure.real, measure_univ, ENNReal.toReal_one, smul_eq_mul, one_mul]
    ring
  have hbound : ∀ᵐ x ∂s.variation, ‖φ x - (1 / 2 : ℝ)‖ ≤ (1 / 2 : ℝ) := by
    exact ae_of_all _ (fun x => by
      rw [Real.norm_eq_abs]
      exact abs_le.mpr ⟨by linarith [h0 x], by linarith [h1 x]⟩)
  have hn := VectorMeasure.norm_integral_le_of_norm_le_const
    (B := (ContinuousLinearMap.lsmul ℝ ℝ).flip) hbound
  rw [hid, Real.norm_eq_abs] at hn
  change |(∫ x, φ x ∂P) - (∫ x, φ x ∂Q)| ≤ (1 / 2 : ℝ) * s.totalVariation.real univ
  rw [s.totalVariation_eq_variation]
  simpa only [ContinuousLinearMap.opNorm_flip, ContinuousLinearMap.opNorm_lsmul, mul_one] using hn

/-- The accumulated observed residual, storing the first time at index zero. -/
def residual (t : ℕ) (observed modelMean : ℕ → ℝ) : ℝ :=
  ∑ s ∈ Finset.range t, (observed s - modelMean s)

/-- Accumulated conditional predictive drift on those same histories and actions. -/
def drift (t : ℕ) (trueMean modelMean : ℕ → ℝ) : ℝ :=
  ∑ s ∈ Finset.range t, (trueMean s - modelMean s)

/-- On the simultaneous event, positive residual excess is bounded by accumulated drift. -/
theorem residual_excess_le_abs_drift (R D boundary : ℝ)
    (hevent : |R - D| ≤ boundary) : max (|R| - boundary) 0 ≤ |D| := by
  have htriangle : |R| ≤ |R - D| + |D| := by
    simpa only [sub_add_cancel] using abs_add_le (R - D) D
  exact max_le (by linarith) (abs_nonneg D)

/-- Actual conditional test drift is controlled by the sum of actual law discrepancies. -/
theorem abs_drift_le_tv_sum (t : ℕ) (P Q : ℕ → Measure Ω)
    [∀ s, IsProbabilityMeasure (P s)] [∀ s, IsProbabilityMeasure (Q s)]
    (φ : ℕ → Ω → ℝ) (hφ : ∀ s, Measurable (φ s))
    (h0 : ∀ s x, 0 ≤ φ s x) (h1 : ∀ s x, φ s x ≤ 1) :
    |drift t (fun s => ∫ x, φ s x ∂P s) (fun s => ∫ x, φ s x ∂Q s)| ≤
      ∑ s ∈ Finset.range t, lawTV (P s) (Q s) := by
  unfold drift
  apply (Finset.abs_sum_le_sum_abs _ _).trans
  exact Finset.sum_le_sum (fun s _ =>
    bounded_test_integral_le_tv (P s) (Q s) (φ s) (hφ s) (h0 s) (h1 s))

/-- Proposition 68, conditional on the actual simultaneous residual event of Proposition 66. -/
theorem sequential_lower_certificate (t : ℕ) (ht : 0 < t)
    (P Q : ℕ → Measure Ω)
    [∀ s, IsProbabilityMeasure (P s)] [∀ s, IsProbabilityMeasure (Q s)]
    (φ : ℕ → Ω → ℝ) (observed : ℕ → ℝ) (boundary : ℝ)
    (hφ : ∀ s, Measurable (φ s))
    (h0 : ∀ s x, 0 ≤ φ s x) (h1 : ∀ s x, φ s x ≤ 1)
    (hevent : |residual t observed (fun s => ∫ x, φ s x ∂Q s) -
      drift t (fun s => ∫ x, φ s x ∂P s) (fun s => ∫ x, φ s x ∂Q s)| ≤ boundary) :
    max (|residual t observed (fun s => ∫ x, φ s x ∂Q s)| - boundary) 0 / (t : ℝ) ≤
      (∑ s ∈ Finset.range t, lawTV (P s) (Q s)) / (t : ℝ) := by
  have hle := (residual_excess_le_abs_drift _ _ _ hevent).trans
    (abs_drift_le_tv_sum t P Q φ hφ h0 h1)
  exact (div_le_div_iff_of_pos_right (Nat.cast_pos.mpr ht)).mpr hle

/-- The conditional certificate holds at all times and all registered rules on one event. -/
theorem simultaneous_sequential_lower_certificate {J : Type*}
    (P Q : ℕ → J → Measure Ω)
    [∀ s j, IsProbabilityMeasure (P s j)] [∀ s j, IsProbabilityMeasure (Q s j)]
    (φ : ℕ → J → Ω → ℝ) (observed : ℕ → J → ℝ) (boundary : ℕ → J → ℝ)
    (hφ : ∀ s j, Measurable (φ s j))
    (h0 : ∀ s j x, 0 ≤ φ s j x) (h1 : ∀ s j x, φ s j x ≤ 1)
    (hevent : ∀ t, 0 < t → ∀ j,
      |residual t (fun s => observed s j) (fun s => ∫ x, φ s j x ∂Q s j) -
      drift t (fun s => ∫ x, φ s j x ∂P s j) (fun s => ∫ x, φ s j x ∂Q s j)| ≤
        boundary t j) :
    ∀ t, 0 < t → ∀ j,
      max (|residual t (fun s => observed s j) (fun s => ∫ x, φ s j x ∂Q s j)| -
        boundary t j) 0 / (t : ℝ) ≤
      (∑ s ∈ Finset.range t, lawTV (P s j) (Q s j)) / (t : ℝ) := by
  intro t ht j
  exact sequential_lower_certificate t ht (fun s => P s j) (fun s => Q s j)
    (fun s => φ s j) (fun s => observed s j) (boundary t j)
    (fun s => hφ s j) (fun s => h0 s j) (fun s => h1 s j) (hevent t ht j)

end
end Komorebi.LSM.SequentialLowerCertificate
