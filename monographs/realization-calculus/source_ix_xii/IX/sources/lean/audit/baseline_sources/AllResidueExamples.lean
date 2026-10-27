module
public import Theorem75
public import NormalizationBoundary
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.AllResidueExamples
open Congruential Mahler GlobalEulerBoundary AllResidueEuler

/-- An actual singular-address coefficient, derived from the original rational recurrence. -/
theorem singular_third : coeff 6 3 3=-(223199/7980:ℚ) := by
  rw [coefficient_recurrence 6 3 (by decide : 0<3)]
  norm_num [Finset.sum_range_succ, Nat.choose, Normalization.normalized_first,
    Normalization.normalized_second]

theorem singular_second_difference : difference 1 2 (coeff 6 3) 1=-(244128/8645:ℚ) := by
  norm_num [difference_succ, singular_third, Normalization.normalized_first,
    Normalization.normalized_second]

theorem singular_unnormalized_second :
    difference 1 2 (unnormalized 6 3) 1=-(1464768/8645:ℚ) := by
  rw [GlobalEulerBoundary.unnormalized_difference, singular_second_difference]
  norm_num

/-- The singular-address higher-order result attains the predicted power p^2. -/
theorem singular_second_valuation :
    padicValRat 3 (difference 1 2 (unnormalized 6 3) 1)=2 := by
  rw [singular_unnormalized_second]
  norm_num [padicValRat_def, padicValInt]
  rw [show (1464768:ℕ)=3^2*162752 by decide,
    padicValNat.mul (by decide : (3:ℕ)^2≠0) (by decide : (162752:ℕ)≠0)]
  norm_num [padicValNat.eq_zero_of_not_dvd]
  rw [show (9:ℕ)=3^2 from rfl, padicValNat.pow]
  norm_num

/-- A regular address beyond the singular boundary, also derived from the same recurrence. -/
theorem upper_regular_coefficients :
    coeff 6 4 1=-(1/210:ℚ) ∧ coeff 6 4 2=(557/27300:ℚ) ∧
    coeff 6 4 3=-(962938/548625:ℚ) := by
  have h1 : coeff 6 4 1=-(1/210:ℚ) := by
    rw [coefficient_recurrence 6 4 (by decide : 0<1)]
    norm_num [Finset.sum_range_succ, Nat.choose]
  have h2 : coeff 6 4 2=(557/27300:ℚ) := by
    rw [coefficient_recurrence 6 4 (by decide : 0<2)]
    norm_num [Finset.sum_range_succ, Nat.choose, h1]
  have h3 : coeff 6 4 3=-(962938/548625:ℚ) := by
    rw [coefficient_recurrence 6 4 (by decide : 0<3)]
    norm_num [Finset.sum_range_succ, Nat.choose, h1, h2]
  exact ⟨h1,h2,h3⟩

theorem upper_regular_unnormalized_second :
    difference 1 2 (unnormalized 6 4) 1=-(102745512/2377375:ℚ) := by
  rw [GlobalEulerBoundary.unnormalized_difference]
  obtain ⟨h1,h2,h3⟩ := upper_regular_coefficients
  norm_num [difference_succ, h1,h2,h3]

/-- Actual application of the universal theorem beyond the previously checked standard window. -/
theorem upper_regular_global_bound :
    precision 3 2 (difference 1 2 (unnormalized 6 4) 1) := by
  simpa using global_unnormalized_precision 3 2 4 1 2 1 (by decide) (by decide) (by decide)

/-- The earlier no-loss counterexample is preserved, even though the corrected global theorem is proved. -/
theorem no_loss_still_false :
    ¬ precision 3 1 (difference 1 1 (coeff 6 3) 1) := by
  rw [precision, difference_one]
  exact fun h => h.elim Normalization.difference_nonzero
    (by rw [Normalization.difference_valuation]; omega)

end KomorebiPaperIX.AllResidueExamples
