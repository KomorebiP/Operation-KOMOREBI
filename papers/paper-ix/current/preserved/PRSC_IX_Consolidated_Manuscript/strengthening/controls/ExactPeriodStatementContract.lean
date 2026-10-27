module
public import DyadicFourLeastPeriods
@[expose] public section
set_option autoImplicit false
open KomorebiPaperIX

example (j n T : ℕ) (hj : j < 4) (hT : 0 < T) :
    Congruential.unnormalized 4 j (n + T) - Congruential.unnormalized 4 j n ≠ 0 ∧
    padicValRat 2 (Congruential.unnormalized 4 j (n + T) - Congruential.unnormalized 4 j n) =
      (padicValNat 2 T : ℤ) + (DyadicFourLeastPeriods.originalBonus j : ℤ) :=
  DyadicFourLeastPeriods.exact_displacement j n T hj hT

example (j r T : ℕ) (hj : j < 4) :
    (0 < T ∧ ∀ n, GlobalEulerBoundary.precision 2 (r : ℤ)
      (Congruential.unnormalized 4 j (n + T) - Congruential.unnormalized 4 j n)) ↔
    0 < T ∧ 2 ^ (r - DyadicFourLeastPeriods.originalBonus j) ∣ T :=
  DyadicFourLeastPeriods.period_iff_dvd j r T hj

example (j r : ℕ) (hj : j < 4) :
    IsLeast {T : ℕ | 0 < T ∧ ∀ n, GlobalEulerBoundary.precision 2 (r : ℤ)
      (Congruential.unnormalized 4 j (n + T) - Congruential.unnormalized 4 j n)}
      (2 ^ (r - DyadicFourLeastPeriods.originalBonus j)) :=
  DyadicFourLeastPeriods.least_packet_period j r hj

example : DyadicFourLeastPeriods.originalBonus 0 = 1 ∧
    DyadicFourLeastPeriods.originalBonus 1 = 1 ∧
    DyadicFourLeastPeriods.originalBonus 2 = 5 ∧
    DyadicFourLeastPeriods.originalBonus 3 = 3 :=
  DyadicFourLeastPeriods.originalBonus_values
