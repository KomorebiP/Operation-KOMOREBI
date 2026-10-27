module
public import DyadicFourLeastPeriods
@[expose] public section
set_option autoImplicit false
namespace KomorebiPaperIX.ExactPeriodControls
open Congruential GlobalEulerBoundary DyadicFourLeastPeriods

/-- The second higher address is constant modulo32 at every row. -/
theorem address_two_mod32 (n : ℕ) :
    precision 2 5 (unnormalized 4 2 (n + 1) - unnormalized 4 2 n) := by
  apply (precision_iff_dvd 2 5 n 1 (by decide) (by decide)).mpr
  rw [originalBonus_values.2.2.1]
  norm_num

/-- At the next precision the least packet period is exactly two. -/
theorem address_two_mod64_least :
    IsLeast {T : ℕ | ExactPeriodClassification.IsPeriod 2 (unnormalized 4 2) 6 T} 2 := by
  have h := least_packet_period 2 6 (by decide)
  rw [originalBonus_values.2.2.1] at h
  norm_num at h
  exact h

/-- Constancy modulo32 does not extend to constancy modulo64. -/
theorem address_two_period_one_fails_mod64 :
    ¬ ExactPeriodClassification.IsPeriod 2 (unnormalized 4 2) 6 1 := by
  rw [period_iff_dvd 2 6 1 (by decide), originalBonus_values.2.2.1]
  norm_num

/-- The other higher address has least period128 modulo1024. -/
theorem address_three_mod1024_least :
    IsLeast {T : ℕ | ExactPeriodClassification.IsPeriod 2 (unnormalized 4 3) 10 T} 128 := by
  have h := least_packet_period 3 10 (by decide)
  rw [originalBonus_values.2.2.2] at h
  norm_num at h
  exact h

/-- Odd multiples of the least period are covered by the complete classification. -/
theorem address_two_mod1024_period96 :
    ExactPeriodClassification.IsPeriod 2 (unnormalized 4 2) 10 96 := by
  apply (period_iff_dvd 2 10 96 (by decide)).mpr
  rw [originalBonus_values.2.2.1]
  norm_num

/-- A positive shift never makes these original rational coefficient values equal. -/
theorem positive_shift_nonzero (j n T : ℕ) (hj : j < 4) (hT : 0 < T) :
    unnormalized 4 j (n + T) ≠ unnormalized 4 j n := by
  exact sub_ne_zero.mp (exact_displacement j n T hj hT).1

end KomorebiPaperIX.ExactPeriodControls
