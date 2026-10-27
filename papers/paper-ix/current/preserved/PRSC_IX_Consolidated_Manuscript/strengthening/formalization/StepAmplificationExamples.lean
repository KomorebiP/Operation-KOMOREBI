module
public import DyadicStepAmplification
public import ConjectureExamples
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.StepAmplificationExamples
open Mahler Congruential GlobalEulerBoundary

theorem actual_second_coefficient : coeff 4 0 2 = 69 := by
  rw [coefficient_recurrence 4 0 (by decide : 0<2)]
  norm_num [Finset.sum_range_succ,Nat.choose,ConjectureExamples.four_first_coefficients.1]

theorem actual_first_difference : difference 1 1 (coeff 4 0) 1 = 70 := by
  rw [difference_one,actual_second_coefficient,ConjectureExamples.four_first_coefficients.1]
  norm_num

theorem actual_first_difference_valuation : padicValRat 2 (difference 1 1 (coeff 4 0) 1)=1 := by
  rw [actual_first_difference]
  norm_num [padicValRat_def,padicValInt]
  rw [show (70:ℕ)=2*35 by decide,
    padicValNat.mul (by decide : (2:ℕ)≠0) (by decide : (35:ℕ)≠0)]
  norm_num [padicValNat.eq_zero_of_not_dvd]

/-- The proved dyadic estimate is exact at this row and address. -/
theorem no_uniform_extra_digit : ¬precision 2 2 (difference 1 1 (coeff 4 0) 1) := by
  intro H
  rcases H with hz | hv
  · rw [actual_first_difference] at hz
    norm_num at hz
  · rw [actual_first_difference_valuation] at hv
    omega

end KomorebiPaperIX.StepAmplificationExamples
