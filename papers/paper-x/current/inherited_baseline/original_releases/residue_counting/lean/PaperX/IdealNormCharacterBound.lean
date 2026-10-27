import PaperX.IdealNormWeightedAttachment
import PaperX.IdealClassQuantitativeTransfer

/-! Transfer of a bound for actual generators to actual ideal norm characters.
The generator estimate is supplied; no estimate for the ideal sum is assumed.
The inverse-class representative's character value must remain nonzero. -/

set_option autoImplicit false
noncomputable section

open Ideal NumberField Filter Asymptotics
open scoped nonZeroDivisors
open NumberField.Units

namespace PaperX.IdealNormWeighted

open PaperX.IdealClassQuantitative

variable (K : Type*) [Field K] [NumberField K]

/-- An actual generator estimate gives an explicit power-saving ideal-character estimate. -/
theorem classNormSum_bound_of_generator_bound {C : ClassGroup (𝓞 K)}
    {J : (Ideal (𝓞 K))⁰} (hJ : ClassGroup.mk0 J = C⁻¹)
    (m : ℕ) (χ : ZMod m →*₀ ℂ)
    (hχJ : χ (absNorm (J : Ideal (𝓞 K)) : ZMod m) ≠ 0)
    {B : ℝ} (hB0 : 0 ≤ B)
    (hB : ∀ Y : ℝ, 1 ≤ Y →
      ‖boundedGeneratorSum K J (fun n => χ (n : ZMod m)) Y‖ ≤
        B * (Y ^ countExponent K + 1)) :
    ∀ X : ℝ, 1 ≤ X →
      ‖classNormSum K C (fun n => χ (n : ZMod m)) X‖ ≤
        (B / ‖(torsionOrder K : ℂ) * χ (absNorm (J : Ideal (𝓞 K)) : ZMod m)‖ *
          ((absNorm (J : Ideal (𝓞 K)) : ℝ) ^ countExponent K + 1)) *
            X ^ countExponent K := by
  intro X hX
  have hN : (1 : ℝ) ≤ absNorm (J : Ideal (𝓞 K)) := by
    exact_mod_cast absNorm_pos_of_nonZeroDivisors J
  have hX0 : 0 ≤ X := le_trans zero_le_one hX
  have hN0 : (0 : ℝ) ≤ absNorm (J : Ideal (𝓞 K)) := le_trans zero_le_one hN
  have hY : 1 ≤ X * absNorm (J : Ideal (𝓞 K)) := by
    nlinarith [mul_nonneg (sub_nonneg.mpr hX) (sub_nonneg.mpr hN)]
  have hp : 1 ≤ X ^ countExponent K := Real.one_le_rpow hX (countExponent_nonneg K)
  rw [classNormSum_character_eq_div K hJ m χ hχJ X, norm_div]
  calc
    _ ≤ B * ((X * (absNorm (J : Ideal (𝓞 K)) : ℝ)) ^ countExponent K + 1) /
        ‖(torsionOrder K : ℂ) * χ (absNorm (J : Ideal (𝓞 K)) : ZMod m)‖ :=
      div_le_div_of_nonneg_right (hB _ hY) (norm_nonneg _)
    _ ≤ _ := by
      rw [Real.mul_rpow hX0 hN0]
      have hc : 0 ≤ B /
          ‖(torsionOrder K : ℂ) * χ (absNorm (J : Ideal (𝓞 K)) : ZMod m)‖ :=
        div_nonneg hB0 (norm_nonneg _)
      calc
        _ = (B / ‖(torsionOrder K : ℂ) * χ (absNorm (J : Ideal (𝓞 K)) : ZMod m)‖) *
            (X ^ countExponent K * (absNorm (J : Ideal (𝓞 K)) : ℝ) ^ countExponent K + 1) := by ring
        _ ≤ (B / ‖(torsionOrder K : ℂ) * χ (absNorm (J : Ideal (𝓞 K)) : ZMod m)‖) *
            (X ^ countExponent K * (absNorm (J : Ideal (𝓞 K)) : ℝ) ^ countExponent K +
              X ^ countExponent K) := mul_le_mul_of_nonneg_left (by linarith) hc
        _ = _ := by ring

/-- Existence of an actual generator bound transfers to an actual ideal bound. -/
theorem exists_classNormSum_bound_of_generator_bound {C : ClassGroup (𝓞 K)}
    {J : (Ideal (𝓞 K))⁰} (hJ : ClassGroup.mk0 J = C⁻¹)
    (m : ℕ) (χ : ZMod m →*₀ ℂ)
    (hχJ : χ (absNorm (J : Ideal (𝓞 K)) : ZMod m) ≠ 0)
    (hgen : ∃ B : ℝ, 0 ≤ B ∧ ∀ Y : ℝ, 1 ≤ Y →
      ‖boundedGeneratorSum K J (fun n => χ (n : ZMod m)) Y‖ ≤
        B * (Y ^ countExponent K + 1)) :
    ∃ M : ℝ, 0 ≤ M ∧ ∀ X : ℝ, 1 ≤ X →
      ‖classNormSum K C (fun n => χ (n : ZMod m)) X‖ ≤ M * X ^ countExponent K := by
  obtain ⟨B, hB0, hB⟩ := hgen
  refine ⟨B / ‖(torsionOrder K : ℂ) * χ (absNorm (J : Ideal (𝓞 K)) : ZMod m)‖ *
    ((absNorm (J : Ideal (𝓞 K)) : ℝ) ^ countExponent K + 1), ?_,
    classNormSum_bound_of_generator_bound K hJ m χ hχJ hB0 hB⟩
  positivity

/-- Asymptotic form of the same transfer, still on the actual bounded ideal sum. -/
theorem classNormSum_isBigO_of_generator_bound {C : ClassGroup (𝓞 K)}
    {J : (Ideal (𝓞 K))⁰} (hJ : ClassGroup.mk0 J = C⁻¹)
    (m : ℕ) (χ : ZMod m →*₀ ℂ)
    (hχJ : χ (absNorm (J : Ideal (𝓞 K)) : ZMod m) ≠ 0)
    (hgen : ∃ B : ℝ, 0 ≤ B ∧ ∀ Y : ℝ, 1 ≤ Y →
      ‖boundedGeneratorSum K J (fun n => χ (n : ZMod m)) Y‖ ≤
        B * (Y ^ countExponent K + 1)) :
    classNormSum K C (fun n => χ (n : ZMod m)) =O[atTop]
      (fun X : ℝ => X ^ countExponent K) := by
  obtain ⟨M, _, hM⟩ := exists_classNormSum_bound_of_generator_bound K hJ m χ hχJ hgen
  apply IsBigO.of_bound M
  filter_upwards [eventually_ge_atTop (1 : ℝ)] with X hX
  rw [Real.norm_eq_abs, abs_of_nonneg (Real.rpow_nonneg (by linarith) _)]
  exact hM X hX

end PaperX.IdealNormWeighted
