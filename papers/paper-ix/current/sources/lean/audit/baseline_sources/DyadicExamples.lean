module

public import DyadicReconstruction
public import OddEulerExamples

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.DyadicExamples

open KomorebiPaperIX.Dyadic KomorebiPaperIX.DyadicReconstruction EulerCoefficients

theorem beta_one : beta 1 = -(1/3:ℚ) := by
  rw [beta_recurrence 1 (by decide)]
  norm_num [Finset.sum_range_succ, kernelCoeff]

theorem beta_two : beta 2 = (1/15:ℚ) := by
  rw [beta_recurrence 2 (by decide)]
  norm_num [Finset.sum_range_succ, kernelCoeff, beta_one]

theorem beta_three : beta 3 = -(2/189:ℚ) := by
  rw [beta_recurrence 3 (by decide)]
  norm_num [Finset.sum_range_succ, kernelCoeff, beta_one, beta_two]

theorem beta_four : beta 4 = (1/675:ℚ) := by
  rw [beta_recurrence 4 (by decide)]
  norm_num [Finset.sum_range_succ, kernelCoeff, beta_one, beta_two, beta_three]

theorem source_anchor_values : sourceEven 0 = 1 ∧ sourceEven 1 = (5/3:ℚ) ∧
    sourceEven 2 = (91/15:ℚ) ∧ sourceEven 3 = (205/7:ℚ) ∧ sourceEven 4 = (7381/45:ℚ) := by
  norm_num [sourceEven]

/-- Example 5.5: all five summands are derived from the general series coefficients. -/
theorem manuscript_terms : summand 4 0 = (7381/45:ℚ) ∧ summand 4 1 = -(6560/3:ℚ) ∧
    summand 4 2 = (163072/15:ℚ) ∧ summand 4 3 = -(204800/9:ℚ) ∧
    summand 4 4 = (229376/15:ℚ) := by
  norm_num [summand, sourceEven, Nat.descFactorial, beta_one, beta_two, beta_three, beta_four]

theorem manuscript_truncations : truncation 4 0 = (7381/45:ℚ) ∧
    truncation 4 1 = -(91019/45:ℚ) ∧ truncation 4 2 = (398197/45:ℚ) ∧
    truncation 4 3 = -(208601/15:ℚ) ∧ truncation 4 4 = 1385 := by
  obtain ⟨h0,h1,h2,h3,h4⟩ := manuscript_terms
  norm_num [truncation, Finset.sum_range_succ, h0,h1,h2,h3,h4]

theorem manuscript_error_zero : (eulerEven 4 : ℚ) - truncation 4 0 = (54944/45:ℚ) := by
  rw [OddEulerExamples.euler_anchor_values.2.2.2.2, manuscript_truncations.1]
  norm_num

theorem manuscript_error_three : (eulerEven 4 : ℚ) - truncation 4 3 = (229376/15:ℚ) := by
  rw [OddEulerExamples.euler_anchor_values.2.2.2.2, manuscript_truncations.2.2.2.1]
  norm_num

theorem manuscript_error_zero_valuation :
    padicValRat 2 ((eulerEven 4 : ℚ) - truncation 4 0) = 5 := by
  rw [manuscript_error_zero]
  norm_num [padicValRat_def,padicValInt]
  rw [show (54944:ℕ)=2^5*1717 by decide,
    padicValNat.mul (by decide : (2^5:ℕ) ≠ 0) (by decide : (1717:ℕ) ≠ 0),
    padicValNat.prime_pow]
  norm_num [padicValNat.eq_zero_of_not_dvd]

theorem manuscript_error_three_valuation :
    padicValRat 2 ((eulerEven 4 : ℚ) - truncation 4 3) = 15 := by
  rw [manuscript_error_three]
  norm_num [padicValRat_def,padicValInt]
  rw [show (229376:ℕ)=2^15*7 by decide,
    padicValNat.mul (by decide : (2^15:ℕ) ≠ 0) (by decide : (7:ℕ) ≠ 0),
    padicValNat.prime_pow]
  norm_num [padicValNat.eq_zero_of_not_dvd]

/-- The unweighted dyadic formula is false; the scale factor is part of the theorem. -/
theorem scale_factor_cannot_be_omitted :
    (eulerEven 1 : ℚ) ≠ ∑ m ∈ Finset.range 2,
      beta m * ((2:ℕ).descFactorial (2*m) : ℚ) * sourceEven (1-m) := by
  rw [OddEulerExamples.euler_anchor_values.2.1]
  norm_num [Finset.sum_range_succ,sourceEven,beta_one,Nat.descFactorial]

/-- The factorial convention is essential: beta_1 is ordinary coefficient -1/3, not -2/3. -/
theorem ordinary_coefficient_not_exponential : beta 1 ≠ -(2/3:ℚ) := by
  rw [beta_one]
  norm_num

theorem zero_row_all_depths (M : ℕ) : truncation 0 M = 1 := by
  rw [full_depth_exact 0 M (Nat.zero_le _), OddEulerExamples.euler_anchor_values.1]
  norm_num

end KomorebiPaperIX.DyadicExamples
