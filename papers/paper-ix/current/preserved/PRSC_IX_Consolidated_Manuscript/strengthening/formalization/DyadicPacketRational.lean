module
public import DyadicFourLeastPeriods
public import Mathlib.NumberTheory.Padics.PadicNorm

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.DyadicPacketRational

open Congruential DyadicFourLeastPeriods

/-- Subtract the constant term and divide by the exact displacement gain. -/
def packet (j n : ℕ) : ℚ :=
  (unnormalized 4 j n - (j.factorial : ℚ)) / (2 : ℚ) ^ originalBonus j

@[simp] theorem packet_zero (j : ℕ) : packet j 0 = 0 := by
  simp [packet, unnormalized]

theorem packet_sub (j m n : ℕ) :
    packet j m - packet j n =
      (unnormalized 4 j m - unnormalized 4 j n) / (2 : ℚ) ^ originalBonus j := by
  unfold packet
  ring

/-- Normalization removes exactly the additional valuation, at every row and shift. -/
theorem exact_displacement (j n T : ℕ) (hj : j < 4) (hT : 0 < T) :
    packet j (n + T) - packet j n ≠ 0 ∧
    padicValRat 2 (packet j (n + T) - packet j n) = (padicValNat 2 T : ℤ) := by
  have h := DyadicFourLeastPeriods.exact_displacement j n T hj hT
  have hd : (2 : ℚ) ^ originalBonus j ≠ 0 := pow_ne_zero _ (by norm_num)
  rw [packet_sub]
  refine ⟨div_ne_zero h.1 hd, ?_⟩
  rw [padicValRat.div h.1 hd, h.2, padicValRat.pow]
  rw [show padicValRat 2 (2 : ℚ) = 1 from padicValRat.self (by decide)]
  ring

/-- All positive displacements preserve the dyadic rational norm. -/
theorem norm_displacement (j n T : ℕ) (hj : j < 4) (hT : 0 < T) :
    padicNorm 2 (packet j (n + T) - packet j n) = padicNorm 2 (T : ℚ) := by
  have h := exact_displacement j n T hj hT
  have ht : (T : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr (Nat.ne_of_gt hT)
  rw [padicNorm.eq_zpow_of_nonzero h.1, padicNorm.eq_zpow_of_nonzero ht,
    h.2, padicValRat.of_nat]

/-- The actual rational packets preserve dyadic distance between every pair of rows. -/
theorem norm_sub (j m n : ℕ) (hj : j < 4) :
    padicNorm 2 (packet j m - packet j n) =
      padicNorm 2 ((m : ℚ) - (n : ℚ)) := by
  rcases lt_trichotomy m n with hmn | hmn | hmn
  · have h := norm_displacement j m (n - m) hj (Nat.sub_pos_of_lt hmn)
    rw [Nat.add_sub_of_le (Nat.le_of_lt hmn), Nat.cast_sub (Nat.le_of_lt hmn)] at h
    simpa only [← neg_sub (packet j n) (packet j m), padicNorm.neg,
      ← neg_sub (n : ℚ) (m : ℚ)] using h
  · subst n
    simp
  · have h := norm_displacement j n (m - n) hj (Nat.sub_pos_of_lt hmn)
    rw [Nat.add_sub_of_le (Nat.le_of_lt hmn), Nat.cast_sub (Nat.le_of_lt hmn)] at h
    exact h

/-- Every normalized packet value is a dyadic integer. -/
theorem norm_le_one (j n : ℕ) (hj : j < 4) : padicNorm 2 (packet j n) ≤ 1 := by
  have h := norm_sub j n 0 hj
  simp only [packet_zero, sub_zero, Nat.cast_zero] at h
  rw [h]
  exact padicNorm.of_nat n

end KomorebiPaperIX.DyadicPacketRational
