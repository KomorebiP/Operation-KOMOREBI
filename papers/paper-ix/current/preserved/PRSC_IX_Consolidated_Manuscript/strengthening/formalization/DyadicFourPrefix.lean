module

public import DyadicFourAllRows
public import DyadicLogThresholds

/-!
Exact initial Newton coefficients for the four normalized generalized Euler
packets. Every displayed rational is derived from the defining triangular
recurrence. Their valuations, together with the checked all-order dyadic bound,
prove the uniform tail estimate needed for exact displacement valuations.
The finite prefix is part of a universal proof, not a sampled surrogate.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false
set_option maxRecDepth 4096
set_option maxHeartbeats 800000

namespace KomorebiPaperIX.DyadicFourPrefix

open Mahler Congruential

/-- Valuation of the first normalized Newton coefficient, for j < 4. -/
def bonus (j : ℕ) : ℕ := match j with
  | 0 => 1
  | 1 => 1
  | 2 => 4
  | _ => 2

def mahlerCoeff (j k : ℕ) : ℚ := Mahler.coefficient (coeff 4 j) k

theorem coeff_0_1 : coeff 4 0 1 = (-1/1:ℚ) := by
  rw [coefficient_recurrence 4 0 (by decide : 0 < 1)]
  norm_num [Finset.sum_range_succ, Nat.choose]

theorem coeff_0_2 : coeff 4 0 2 = (69/1:ℚ) := by
  rw [coefficient_recurrence 4 0 (by decide : 0 < 2)]
  norm_num [Finset.sum_range_succ, Nat.choose, coeff_0_1]

theorem mahler_0_1 : mahlerCoeff 0 1 = (-2/1:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_0_1]

theorem mahler_0_2 : mahlerCoeff 0 2 = (72/1:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_0_1, coeff_0_2]

theorem coeff_1_1 : coeff 4 1 1 = (-1/5:ℚ) := by
  rw [coefficient_recurrence 4 1 (by decide : 0 < 1)]
  norm_num [Finset.sum_range_succ, Nat.choose]

theorem coeff_1_2 : coeff 4 1 2 = (121/45:ℚ) := by
  rw [coefficient_recurrence 4 1 (by decide : 0 < 2)]
  norm_num [Finset.sum_range_succ, Nat.choose, coeff_1_1]

theorem mahler_1_1 : mahlerCoeff 1 1 = (-6/5:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_1_1]

theorem mahler_1_2 : mahlerCoeff 1 2 = (184/45:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_1_1, coeff_1_2]

theorem coeff_2_1 : coeff 4 2 1 = (-1/15:ℚ) := by
  rw [coefficient_recurrence 4 2 (by decide : 0 < 1)]
  norm_num [Finset.sum_range_succ, Nat.choose]

theorem coeff_2_2 : coeff 4 2 2 = (13/45:ℚ) := by
  rw [coefficient_recurrence 4 2 (by decide : 0 < 2)]
  norm_num [Finset.sum_range_succ, Nat.choose, coeff_2_1]

theorem coeff_2_3 : coeff 4 2 3 = (-4009/455:ℚ) := by
  rw [coefficient_recurrence 4 2 (by decide : 0 < 3)]
  norm_num [Finset.sum_range_succ, Nat.choose, coeff_2_1, coeff_2_2]

theorem coeff_2_4 : coeff 4 2 4 = (151129/153:ℚ) := by
  rw [coefficient_recurrence 4 2 (by decide : 0 < 4)]
  norm_num [Finset.sum_range_succ, Nat.choose, coeff_2_1, coeff_2_2, coeff_2_3]

theorem coeff_2_5 : coeff 4 2 5 = (-340474381/1155:ℚ) := by
  rw [coefficient_recurrence 4 2 (by decide : 0 < 5)]
  norm_num [Finset.sum_range_succ, Nat.choose, coeff_2_1, coeff_2_2, coeff_2_3, coeff_2_4]

theorem coeff_2_6 : coeff 4 2 6 = (790092547807/4095:ℚ) := by
  rw [coefficient_recurrence 4 2 (by decide : 0 < 6)]
  norm_num [Finset.sum_range_succ, Nat.choose, coeff_2_1, coeff_2_2, coeff_2_3, coeff_2_4, coeff_2_5]

theorem mahler_2_1 : mahlerCoeff 2 1 = (-16/15:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_2_1]

theorem mahler_2_2 : mahlerCoeff 2 2 = (64/45:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_2_1, coeff_2_2]

theorem mahler_2_3 : mahlerCoeff 2 3 = (-14848/1365:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_2_1, coeff_2_2, coeff_2_3]

theorem mahler_2_4 : mahlerCoeff 2 4 = (71426048/69615:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_2_1, coeff_2_2, coeff_2_3, coeff_2_4]

theorem mahler_2_5 : mahlerCoeff 2 5 = (-25509691392/85085:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_2_1, coeff_2_2, coeff_2_3, coeff_2_4, coeff_2_5]

theorem mahler_2_6 : mahlerCoeff 2 6 = (149113198870528/765765:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_2_1, coeff_2_2, coeff_2_3, coeff_2_4, coeff_2_5, coeff_2_6]

theorem coeff_3_1 : coeff 4 3 1 = (-1/35:ℚ) := by
  rw [coefficient_recurrence 4 3 (by decide : 0 < 1)]
  norm_num [Finset.sum_range_succ, Nat.choose]

theorem coeff_3_2 : coeff 4 3 2 = (59/1155:ℚ) := by
  rw [coefficient_recurrence 4 3 (by decide : 0 < 2)]
  norm_num [Finset.sum_range_succ, Nat.choose, coeff_3_1]

theorem coeff_3_3 : coeff 4 3 3 = (-407/637:ℚ) := by
  rw [coefficient_recurrence 4 3 (by decide : 0 < 3)]
  norm_num [Finset.sum_range_succ, Nat.choose, coeff_3_1, coeff_3_2]

theorem coeff_3_4 : coeff 4 3 4 = (15330979/522291:ℚ) := by
  rw [coefficient_recurrence 4 3 (by decide : 0 < 4)]
  norm_num [Finset.sum_range_succ, Nat.choose, coeff_3_1, coeff_3_2, coeff_3_3]

theorem mahler_3_1 : mahlerCoeff 3 1 = (-36/35:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_3_1]

theorem mahler_3_2 : mahlerCoeff 3 2 = (256/231:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_3_1, coeff_3_2]

theorem mahler_3_3 : mahlerCoeff 3 3 = (-65792/35035:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_3_1, coeff_3_2, coeff_3_3]

theorem mahler_3_4 : mahlerCoeff 3 4 = (161644544/4849845:ℚ) := by
  norm_num [mahlerCoeff, Mahler.coefficient, difference_explicit, Finset.sum_range_succ, Nat.choose, coeff_3_1, coeff_3_2, coeff_3_3, coeff_3_4]

theorem valuation_two_power_odd (e u : ℕ) (hu : ¬ 2 ∣ u) :
    padicValNat 2 (2^e*u) = e := by
  have hu0 : u ≠ 0 := by intro h; exact hu (h ▸ dvd_zero 2)
  rw [padicValNat.mul (by positivity) hu0, padicValNat.prime_pow,
    padicValNat.eq_zero_of_not_dvd hu, Nat.add_zero]

theorem mahler_valuation_0_1 : padicValRat 2 (mahlerCoeff 0 1) = 1 := by
  have hv : padicValNat 2 2 = 1 := by
    rw [show (2:ℕ) = 2^1*1 by norm_num]
    exact valuation_two_power_odd 1 1 (by norm_num)
  rw [mahler_0_1]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem mahler_valuation_0_2 : padicValRat 2 (mahlerCoeff 0 2) = 3 := by
  have hv : padicValNat 2 72 = 3 := by
    rw [show (72:ℕ) = 2^3*9 by norm_num]
    exact valuation_two_power_odd 3 9 (by norm_num)
  rw [mahler_0_2]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem mahler_valuation_1_1 : padicValRat 2 (mahlerCoeff 1 1) = 1 := by
  have hv : padicValNat 2 6 = 1 := by
    rw [show (6:ℕ) = 2^1*3 by norm_num]
    exact valuation_two_power_odd 1 3 (by norm_num)
  rw [mahler_1_1]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem mahler_valuation_1_2 : padicValRat 2 (mahlerCoeff 1 2) = 3 := by
  have hv : padicValNat 2 184 = 3 := by
    rw [show (184:ℕ) = 2^3*23 by norm_num]
    exact valuation_two_power_odd 3 23 (by norm_num)
  rw [mahler_1_2]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem mahler_valuation_2_1 : padicValRat 2 (mahlerCoeff 2 1) = 4 := by
  have hv : padicValNat 2 16 = 4 := by
    rw [show (16:ℕ) = 2^4*1 by norm_num]
    exact valuation_two_power_odd 4 1 (by norm_num)
  rw [mahler_2_1]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem mahler_valuation_2_2 : padicValRat 2 (mahlerCoeff 2 2) = 6 := by
  have hv : padicValNat 2 64 = 6 := by
    rw [show (64:ℕ) = 2^6*1 by norm_num]
    exact valuation_two_power_odd 6 1 (by norm_num)
  rw [mahler_2_2]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem mahler_valuation_2_3 : padicValRat 2 (mahlerCoeff 2 3) = 9 := by
  have hv : padicValNat 2 14848 = 9 := by
    rw [show (14848:ℕ) = 2^9*29 by norm_num]
    exact valuation_two_power_odd 9 29 (by norm_num)
  rw [mahler_2_3]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem mahler_valuation_2_4 : padicValRat 2 (mahlerCoeff 2 4) = 13 := by
  have hv : padicValNat 2 71426048 = 13 := by
    rw [show (71426048:ℕ) = 2^13*8719 by norm_num]
    exact valuation_two_power_odd 13 8719 (by norm_num)
  rw [mahler_2_4]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem mahler_valuation_2_5 : padicValRat 2 (mahlerCoeff 2 5) = 16 := by
  have hv : padicValNat 2 25509691392 = 16 := by
    rw [show (25509691392:ℕ) = 2^16*389247 by norm_num]
    exact valuation_two_power_odd 16 389247 (by norm_num)
  rw [mahler_2_5]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem mahler_valuation_2_6 : padicValRat 2 (mahlerCoeff 2 6) = 22 := by
  have hv : padicValNat 2 149113198870528 = 22 := by
    rw [show (149113198870528:ℕ) = 2^22*35551357 by norm_num]
    exact valuation_two_power_odd 22 35551357 (by norm_num)
  rw [mahler_2_6]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem mahler_valuation_3_1 : padicValRat 2 (mahlerCoeff 3 1) = 2 := by
  have hv : padicValNat 2 36 = 2 := by
    rw [show (36:ℕ) = 2^2*9 by norm_num]
    exact valuation_two_power_odd 2 9 (by norm_num)
  rw [mahler_3_1]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem mahler_valuation_3_2 : padicValRat 2 (mahlerCoeff 3 2) = 8 := by
  have hv : padicValNat 2 256 = 8 := by
    rw [show (256:ℕ) = 2^8*1 by norm_num]
    exact valuation_two_power_odd 8 1 (by norm_num)
  rw [mahler_3_2]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem mahler_valuation_3_3 : padicValRat 2 (mahlerCoeff 3 3) = 8 := by
  have hv : padicValNat 2 65792 = 8 := by
    rw [show (65792:ℕ) = 2^8*257 by norm_num]
    exact valuation_two_power_odd 8 257 (by norm_num)
  rw [mahler_3_3]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem mahler_valuation_3_4 : padicValRat 2 (mahlerCoeff 3 4) = 15 := by
  have hv : padicValNat 2 161644544 = 15 := by
    rw [show (161644544:ℕ) = 2^15*4933 by norm_num]
    exact valuation_two_power_odd 15 4933 (by norm_num)
  rw [mahler_3_4]
  norm_num [padicValRat_def, padicValInt, hv, padicValNat.eq_zero_of_not_dvd]

theorem first_nonzero (j : ℕ) (hj : j < 4) : mahlerCoeff j 1 ≠ 0 := by
  interval_cases j <;> norm_num [mahler_0_1, mahler_1_1, mahler_2_1, mahler_3_1]

theorem first_valuation (j : ℕ) (hj : j < 4) :
    padicValRat 2 (mahlerCoeff j 1) = (bonus j : ℤ) := by
  interval_cases j <;>
    norm_num [mahler_valuation_0_1, mahler_valuation_1_1,
      mahler_valuation_2_1, mahler_valuation_3_1, bonus]

theorem precision_of_order_le (j k L : ℕ) (hj : j < 4) (hL : L ≤ k) :
    GlobalEulerBoundary.precision 2 (L:ℤ) (mahlerCoeff j k) := by
  have H := DyadicFourAllRows.normalized_precision j 1 k 0 hj
  rcases H with hz | hv
  · exact Or.inl hz
  · exact Or.inr (le_trans (by exact_mod_cast hL) hv)

/-- All higher Newton terms have the extra precision needed for first-term dominance. -/
theorem tail_precision (j : ℕ) (hj : j < 4) (k : ℕ) (hk : 2 ≤ k) :
    GlobalEulerBoundary.precision 2 ((bonus j + 1 + Nat.log 2 k : ℕ):ℤ)
      (mahlerCoeff j k) := by
  interval_cases j
  · by_cases hlarge : 3 ≤ k
    · apply precision_of_order_le 0 k _ (by decide)
      simpa [bonus] using DyadicLogThresholds.two_add_log_le k hlarge
    · have he : k = 2 := by omega
      subst k
      apply Or.inr
      rw [mahler_valuation_0_2]
      decide
  · by_cases hlarge : 3 ≤ k
    · apply precision_of_order_le 1 k _ (by decide)
      simpa [bonus] using DyadicLogThresholds.two_add_log_le k hlarge
    · have he : k = 2 := by omega
      subst k
      apply Or.inr
      rw [mahler_valuation_1_2]
      decide
  · by_cases hlarge : 7 ≤ k
    · apply precision_of_order_le 2 k _ (by decide)
      simpa [bonus] using DyadicLogThresholds.five_add_log_le k hlarge
    · interval_cases k <;> apply Or.inr
      all_goals first
        | rw [mahler_valuation_2_2]; decide
        | rw [mahler_valuation_2_3]; decide
        | rw [mahler_valuation_2_4]; decide
        | rw [mahler_valuation_2_5]; decide
        | rw [mahler_valuation_2_6]; decide
  · by_cases hlarge : 5 ≤ k
    · apply precision_of_order_le 3 k _ (by decide)
      simpa [bonus] using DyadicLogThresholds.three_add_log_le k hlarge
    · interval_cases k <;> apply Or.inr
      all_goals first
        | rw [mahler_valuation_3_2]; decide
        | rw [mahler_valuation_3_3]; decide
        | rw [mahler_valuation_3_4]; decide

end KomorebiPaperIX.DyadicFourPrefix
