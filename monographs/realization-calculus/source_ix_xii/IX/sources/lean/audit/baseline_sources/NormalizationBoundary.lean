module

public import CongruentialEuler
public import Mathlib.NumberTheory.Padics.PadicVal.Basic

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.Normalization

open Congruential

/-- The coefficient is computed from the same recursive definition as the general theorem. -/
theorem normalized_first : coeff 6 3 1 = -(1/84 : ℚ) := by
  rw [coefficient_recurrence 6 3 (by decide : 0 < 1)]
  norm_num [Finset.sum_range_succ, Nat.choose]

theorem normalized_second : coeff 6 3 2 = (703/5460 : ℚ) := by
  rw [coefficient_recurrence 6 3 (by decide : 0 < 2)]
  norm_num [Finset.sum_range_succ, normalized_first, Nat.choose]

theorem normalized_difference : coeff 6 3 2 - coeff 6 3 1 = (64/455 : ℚ) := by
  rw [normalized_first, normalized_second]
  norm_num

theorem difference_nonzero : coeff 6 3 2 - coeff 6 3 1 ≠ 0 := by
  rw [normalized_difference]
  norm_num

theorem difference_valuation : padicValRat 3 (coeff 6 3 2 - coeff 6 3 1) = 0 := by
  rw [normalized_difference]
  norm_num [padicValRat_def, padicValInt, padicValNat.eq_zero_of_not_dvd]

theorem factorial_valuation : padicValNat 3 (Nat.factorial 3) = 1 := by
  change padicValNat 3 (3*2) = 1
  rw [padicValNat.mul (by decide : (3:ℕ) ≠ 0) (by decide : (2:ℕ) ≠ 0)]
  norm_num [padicValNat.eq_zero_of_not_dvd]

theorem false_unrestricted_bound :
    ¬ ((1 : ℤ) ≤ padicValRat 3 (coeff 6 3 2 - coeff 6 3 1)) := by
  rw [difference_valuation]
  norm_num

theorem factorial_loss_is_sharp :
    padicValRat 3 (coeff 6 3 2 - coeff 6 3 1) =
      (1 : ℤ) - (padicValNat 3 (Nat.factorial 3) : ℤ) := by
  rw [difference_valuation, factorial_valuation]
  norm_num

theorem unnormalized_difference : unnormalized 6 3 2 - unnormalized 6 3 1 = (384/455 : ℚ) := by
  simp only [unnormalized, ← mul_sub, normalized_difference]
  norm_num

theorem unnormalized_difference_valuation :
    padicValRat 3 (unnormalized 6 3 2 - unnormalized 6 3 1) = 1 := by
  rw [unnormalized_difference]
  norm_num [padicValRat_def, padicValInt]
  rw [show (384:ℕ)=3*128 by decide,
    padicValNat.mul (by decide : (3:ℕ) ≠ 0) (by decide : (128:ℕ) ≠ 0)]
  norm_num [padicValNat.eq_zero_of_not_dvd]

/-- The counterexample lies in the claimed all-residue parameter domain. -/
theorem counterexample_parameters :
    Nat.Prime 3 ∧ Odd (3:ℕ) ∧ (2:ℕ) ∣ (3-1) ∧ (6:ℕ)=2*3 ∧
      (3:ℕ)<6 ∧ ((3-1)/2:ℕ)=1 := by
  norm_num

/-- Already the one-step specialization refutes the universal no-loss statement. -/
theorem universal_no_loss_refuted :
    ¬ (∀ p m j n : ℕ, Nat.Prime p → Odd p → 0 < m → m ∣ p-1 → j < m*p →
      (min 1 (m*n) : ℤ) ≤ padicValRat p
        (coeff (m*p) j (n+(p-1)/m) - coeff (m*p) j n)) := by
  intro h
  have bad := h 3 2 3 1 (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  norm_num only [Nat.reduceSub, Nat.reduceDiv, Nat.reduceAdd, Nat.reduceMul,
    Int.reduceMul, min_eq_left (by norm_num : (1:ℤ) ≤ 2)] at bad
  exact false_unrestricted_bound bad

end KomorebiPaperIX.Normalization
