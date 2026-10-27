module
public import NewtonDominance
public import DyadicFourPrefix
public import ExactPeriodClassification
public import NishibuchiCompletion
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.DyadicFourLeastPeriods
open Mahler Congruential GlobalEulerBoundary

/-- The original coefficients include the address factorial in their exact gain. -/
def originalBonus (j : ℕ) : ℕ :=
  DyadicFourPrefix.bonus j + padicValNat 2 j.factorial

theorem originalBonus_values :
    originalBonus 0 = 1 ∧ originalBonus 1 = 1 ∧
    originalBonus 2 = 5 ∧ originalBonus 3 = 3 := by
  have h2 : padicValNat 2 2 = 1 := by
    simp
  have h6 : padicValNat 2 6 = 1 := by
    simpa using DyadicFourPrefix.valuation_two_power_odd 1 3 (by norm_num)
  norm_num [originalBonus, DyadicFourPrefix.bonus, h2, h6]

/-- Exact valuation for every positive displacement and every normalized packet row. -/
theorem normalized_exact_displacement (j n T : ℕ) (hj : j < 4) (hT : 0 < T) :
    coeff 4 j (n + T) - coeff 4 j n ≠ 0 ∧
    padicValRat 2 (coeff 4 j (n + T) - coeff 4 j n) =
      (padicValNat 2 T : ℤ) + (DyadicFourPrefix.bonus j : ℤ) := by
  exact NewtonDominance.exact_displacement (coeff 4 j) (DyadicFourPrefix.bonus j)
    (DyadicFourPrefix.first_nonzero j hj) (DyadicFourPrefix.first_valuation j hj)
    (DyadicFourPrefix.tail_precision j hj) n T hT

/-- Original, unnormalized coefficients: the gain is exactly 1,1,5,3 by address. -/
theorem exact_displacement (j n T : ℕ) (hj : j < 4) (hT : 0 < T) :
    unnormalized 4 j (n + T) - unnormalized 4 j n ≠ 0 ∧
    padicValRat 2 (unnormalized 4 j (n + T) - unnormalized 4 j n) =
      (padicValNat 2 T : ℤ) + (originalBonus j : ℤ) := by
  have h := normalized_exact_displacement j n T hj hT
  have hf : (j.factorial : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero j)
  have he : unnormalized 4 j (n + T) - unnormalized 4 j n =
      (j.factorial : ℚ) * (coeff 4 j (n + T) - coeff 4 j n) := by
    simp only [unnormalized, mul_sub]
  rw [he]
  refine ⟨mul_ne_zero hf h.1, ?_⟩
  rw [padicValRat.mul hf h.1, padicValRat.of_nat, h.2]
  simp only [originalBonus, Nat.cast_add]
  ring

/-- Pointwise congruence has the same sharp displacement criterion at every row. -/
theorem precision_iff_dvd (j r n T : ℕ) (hj : j < 4) (hT : 0 < T) :
    precision 2 (r : ℤ) (unnormalized 4 j (n + T) - unnormalized 4 j n) ↔
      2 ^ (r - originalBonus j) ∣ T :=
  ExactPeriodClassification.precision_iff_dvd 2 (unnormalized 4 j)
    (originalBonus j) r n T hT (exact_displacement j n T hj hT)

/-- All positive periods, not only power-of-two candidates, are classified. -/
theorem period_iff_dvd (j r T : ℕ) (hj : j < 4) :
    ExactPeriodClassification.IsPeriod 2 (unnormalized 4 j) r T ↔
      0 < T ∧ 2 ^ (r - originalBonus j) ∣ T :=
  ExactPeriodClassification.isPeriod_iff_dvd 2 (unnormalized 4 j)
    (originalBonus j) r T (fun n S hS => exact_displacement j n S hj hS)

/-- The least positive packet period is valid uniformly from row zero. -/
theorem least_packet_period (j r : ℕ) (hj : j < 4) :
    IsLeast {T : ℕ | ExactPeriodClassification.IsPeriod 2 (unnormalized 4 j) r T}
      (2 ^ (r - originalBonus j)) :=
  ExactPeriodClassification.least_period 2 (unnormalized 4 j)
    (originalBonus j) r (fun n S hS => exact_displacement j n S hj hS)

/-- Exact displacement in Nishibuchi's original degree-indexed convention. -/
theorem original_degree_exact_displacement (j n T : ℕ) (hj : j < 4) (hT : 0 < T) :
    NishibuchiCompletion.generalizedEuler 4 (by decide) j (4 * n + 4 * T) -
      NishibuchiCompletion.generalizedEuler 4 (by decide) j (4 * n) ≠ 0 ∧
    padicValRat 2
      (NishibuchiCompletion.generalizedEuler 4 (by decide) j (4 * n + 4 * T) -
       NishibuchiCompletion.generalizedEuler 4 (by decide) j (4 * n)) =
      (padicValNat 2 T : ℤ) + (originalBonus j : ℤ) := by
  rw [← Nat.mul_add, NishibuchiCompletion.generalizedEuler_at_packet,
    NishibuchiCompletion.generalizedEuler_at_packet]
  exact exact_displacement j n T hj hT

end KomorebiPaperIX.DyadicFourLeastPeriods
