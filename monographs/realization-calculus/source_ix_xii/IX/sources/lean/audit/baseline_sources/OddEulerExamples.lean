module

public import OddEulerReconstruction

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.OddEulerExamples

open OddPower EulerCoefficients OddEuler

/-- The scalar anchors are derived from the same general congruential recurrence. -/
theorem coefficient_one : Congruential.coeff 2 0 1 = -1 := by
  rw [Congruential.coefficient_recurrence 2 0 (by decide : 0 < 1)]
  norm_num [Finset.sum_range_succ, Nat.choose]

theorem coefficient_two : Congruential.coeff 2 0 2 = 5 := by
  rw [Congruential.coefficient_recurrence 2 0 (by decide : 0 < 2)]
  norm_num [Finset.sum_range_succ, coefficient_one, Nat.choose]

theorem coefficient_three : Congruential.coeff 2 0 3 = -61 := by
  rw [Congruential.coefficient_recurrence 2 0 (by decide : 0 < 3)]
  norm_num [Finset.sum_range_succ, coefficient_one, coefficient_two, Nat.choose]

theorem coefficient_four : Congruential.coeff 2 0 4 = 1385 := by
  rw [Congruential.coefficient_recurrence 2 0 (by decide : 0 < 4)]
  norm_num [Finset.sum_range_succ, coefficient_one, coefficient_two, coefficient_three, Nat.choose]

theorem euler_anchor_values : eulerEven 0 = 1 ∧ eulerEven 1 = -1 ∧ eulerEven 2 = 5 ∧
    eulerEven 3 = -61 ∧ eulerEven 4 = 1385 := by
  simp [eulerEven, coefficient_one, coefficient_two, coefficient_three, coefficient_four]

theorem inverse_anchor_values : inverseEven 0 = 1 ∧ inverseEven 1 = -2 ∧ inverseEven 2 = 16 ∧
    inverseEven 3 = -272 ∧ inverseEven 4 = 7936 := by
  obtain ⟨h0,h1,h2,h3,h4⟩ := euler_anchor_values
  norm_num [inverseEven, inverseCoeff, Finset.sum_range_succ, euler, h0,h1,h2,h3,h4, Nat.choose]

theorem source_anchor_values : source 5 0 = 1 ∧ source 5 2 = 49 ∧ source 5 4 = 4705 ∧
    source 5 6 = 428689 ∧ source 5 8 = 37665985 := by
  norm_num [source, Finset.sum_range_succ]

/-- Checks the exact displayed Example 4.4 without a numerical approximation. -/
theorem manuscript_truncation : truncation 5 4 2 = 2731001385 := by
  obtain ⟨h0,h1,h2,h3,h4⟩ := inverse_anchor_values
  obtain ⟨s0,s2,s4,s6,s8⟩ := source_anchor_values
  norm_num [truncation, Finset.sum_range_succ, h0,h1,h2,s4,s6,s8, Nat.choose]

theorem manuscript_error : eulerEven 4 - truncation 5 4 2 = -2731000000 := by
  rw [manuscript_truncation, euler_anchor_values.2.2.2.2]
  norm_num

theorem manuscript_error_sharp : (5:ℤ)^6 ∣ eulerEven 4 - truncation 5 4 2 ∧
    ¬ (5:ℤ)^7 ∣ eulerEven 4 - truncation 5 4 2 := by
  rw [manuscript_error]
  norm_num

/-- Oddness is indispensable: the even length two already fails in row zero. -/
theorem even_length_reconstruction_fails : truncation 2 0 0 ≠ eulerEven 0 := by
  rw [euler_anchor_values.1]
  norm_num [truncation, inverseEven, source, Finset.sum_range_succ]

end KomorebiPaperIX.OddEulerExamples
