import PaperX.IdealClassCharacterSum

/-!
# Power saving for actual ordinary class character sums

The common leading coefficient in the actual ideal-class asymptotic cancels for
weights of total sum zero. Nontrivial ordinary ideal-class characters satisfy this
condition by finite-group character orthogonality, proved in the preceding file.
These are not characters of an additional norm-residue or ray-class quotient.
-/
set_option autoImplicit false
noncomputable section

open Ideal NumberField Filter Asymptotics
open scoped nonZeroDivisors Classical BigOperators

namespace PaperX.IdealClassCharacter

open PaperX.IdealClassQuantitative

variable (K : Type*) [Field K] [NumberField K]

/-- The actual number-field counting exponent is strictly below one. -/
theorem countExponent_lt_one : countExponent K < 1 := by
  apply sub_lt_self
  apply inv_pos.mpr
  exact_mod_cast Module.finrank_pos (R := ℚ) (M := K)

/-- Zero total weight cancels the common leading term exactly. -/
theorem weightedSum_eq_sum_errors (w : ClassGroup (𝓞 K) → ℂ)
    (hw : ∑ C, w C = 0) (X : ℝ) :
    weightedSum K w X = ∑ C, w C *
      (((classCount K C X : ℝ) - classResidue K * X : ℝ) : ℂ) := by
  rw [weightedSum_eq_sum_classCount]
  simp only [Complex.ofReal_sub, Complex.ofReal_natCast, mul_sub, Finset.sum_sub_distrib]
  rw [← Finset.sum_mul, hw, zero_mul, sub_zero]

/-- Every zero-sum family of class weights has a power-saving bound at all `X ≥ 1`. -/
theorem exists_weightedSum_bound (w : ClassGroup (𝓞 K) → ℂ)
    (hw : ∑ C, w C = 0) :
    ∃ M : ℝ, 0 ≤ M ∧ ∀ X : ℝ, 1 ≤ X →
      ‖weightedSum K w X‖ ≤ M * X ^ countExponent K := by
  choose M hM0 hM using exists_classCount_bound K
  refine ⟨∑ C, ‖w C‖ * M C, Finset.sum_nonneg (fun C _ =>
    mul_nonneg (norm_nonneg _) (hM0 C)), ?_⟩
  intro X hX
  rw [weightedSum_eq_sum_errors K w hw]
  calc
    _ ≤ ∑ C, ‖w C *
        (((classCount K C X : ℝ) - classResidue K * X : ℝ) : ℂ)‖ :=
      norm_sum_le _ _
    _ ≤ ∑ C, (‖w C‖ * M C) * X ^ countExponent K := by
      apply Finset.sum_le_sum
      intro C _
      rw [norm_mul, Complex.norm_real, Real.norm_eq_abs, mul_assoc]
      exact mul_le_mul_of_nonneg_left (hM C X hX) (norm_nonneg _)
    _ = _ := (Finset.sum_mul _ _ _).symm

/-- The actual ideal sum of a nontrivial ordinary class character has a power saving. -/
theorem exists_characterSum_bound (χ : ClassGroup (𝓞 K) →* ℂ) (hχ : χ ≠ 1) :
    ∃ M : ℝ, 0 ≤ M ∧ ∀ X : ℝ, 1 ≤ X →
      ‖weightedSum K χ X‖ ≤ M * X ^ countExponent K :=
  exists_weightedSum_bound K χ (sum_character_eq_zero χ hχ)

/-- Asymptotic form of the uniform bound for zero-sum class weights. -/
theorem weightedSum_isBigO (w : ClassGroup (𝓞 K) → ℂ)
    (hw : ∑ C, w C = 0) :
    weightedSum K w =O[atTop] (fun X : ℝ => X ^ countExponent K) := by
  obtain ⟨M, _, hM⟩ := exists_weightedSum_bound K w hw
  apply IsBigO.of_bound M
  filter_upwards [eventually_ge_atTop (1 : ℝ)] with X hX
  rw [Real.norm_eq_abs, abs_of_nonneg (Real.rpow_nonneg (by linarith) _)]
  exact hM X hX

/-- Asymptotic power saving for each actual nontrivial ordinary ideal-class character. -/
theorem characterSum_isBigO (χ : ClassGroup (𝓞 K) →* ℂ) (hχ : χ ≠ 1) :
    weightedSum K χ =O[atTop] (fun X : ℝ => X ^ countExponent K) :=
  weightedSum_isBigO K χ (sum_character_eq_zero χ hχ)

end PaperX.IdealClassCharacter
