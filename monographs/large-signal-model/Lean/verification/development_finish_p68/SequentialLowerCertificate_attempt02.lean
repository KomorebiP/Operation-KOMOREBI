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
    simpa only [VectorMeasure.Integrable, Measure.variation_toSignedMeasure, Pi.sub_apply] using
      hp.sub (integrable_const (1 / 2 : ℝ))
  have hqc : Q.toSignedMeasure.Integrable (fun x => φ x - (1 / 2 : ℝ)) := by
    simpa only [VectorMeasure.Integrable, Measure.variation_toSignedMeasure, Pi.sub_apply] using
      hq.sub (integrable_const (1 / 2 : ℝ))
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

end
end Komorebi.LSM.SequentialLowerCertificate
