import Komorebi.Foundation.TowerObstruction

/-!
# Uniform arithmetic classification of constant residuals

For the integer tower with bonding map multiplication by m >= 2, a constant
inhomogeneous sequence c admits a lift exactly when m - 1 divides c.
This is an infinite-family theorem, not a finite experiment.
-/

namespace Komorebi.MultiplierTower

abbrev Sequence := ℕ → ℤ

def delta (m : ℕ) : Sequence →+ Sequence where
  toFun a n := a n - (m : ℤ) * a (n + 1)
  map_zero' := by ext n; simp
  map_add' a b := by ext n; simp only [Pi.add_apply]; ring

def constant (c : ℤ) : Sequence := fun _ => c

theorem iterate_identity (m : ℕ) (c : ℤ) (a : Sequence)
    (ha : delta m a = constant c) (n : ℕ) :
    ((m : ℤ) - 1) * a 0 + c =
      (m : ℤ) ^ n * (((m : ℤ) - 1) * a n + c) := by
  induction n with
  | zero => simp
  | succ n ih =>
      have hs : a n - (m : ℤ) * a (n + 1) = c := congrFun ha n
      have he : a n = c + (m : ℤ) * a (n + 1) := by omega
      rw [ih, pow_succ, he]
      ring

theorem eq_zero_of_all_powers_dvd (m : ℕ) (hm : 1 < m) (z : ℤ)
    (h : ∀ n : ℕ, (m : ℤ) ^ n ∣ z) : z = 0 := by
  apply Int.eq_zero_of_dvd_of_natAbs_lt_natAbs (h z.natAbs)
  simpa using (Nat.lt_pow_self (n := z.natAbs) hm)

/-- Exact classification, including both the obstruction and solvable cases. -/
theorem constant_has_lift_iff (m : ℕ) (hm : 1 < m) (c : ℤ) :
    (∃ a : Sequence, delta m a = constant c) ↔ ((m : ℤ) - 1) ∣ c := by
  constructor
  · rintro ⟨a, ha⟩
    have hz : ((m : ℤ) - 1) * a 0 + c = 0 :=
      eq_zero_of_all_powers_dvd m hm _ (fun n =>
        ⟨((m : ℤ) - 1) * a n + c, iterate_identity m c a ha n⟩)
    refine ⟨-a 0, ?_⟩
    calc
      c = -(((m : ℤ) - 1) * a 0) := by omega
      _ = ((m : ℤ) - 1) * (-a 0) := by ring
  · rintro ⟨t, ht⟩
    refine ⟨constant (-t), ?_⟩
    funext n
    change -t - (m : ℤ) * (-t) = c
    rw [ht]
    ring

abbrev ObstructionGroup (m : ℕ) := Sequence ⧸ (delta m).range

def constantClass (m : ℕ) (c : ℤ) : ObstructionGroup m :=
  QuotientAddGroup.mk (constant c)

/-- The constant class vanishes exactly on the ideal (m - 1) of the integers. -/
theorem constant_class_eq_zero_iff (m : ℕ) (hm : 1 < m) (c : ℤ) :
    constantClass m c = 0 ↔ ((m : ℤ) - 1) ∣ c := by
  change QuotientAddGroup.mk (constant c) = (0 : ObstructionGroup m) ↔ _
  rw [QuotientAddGroup.eq_zero_iff]
  exact constant_has_lift_iff m hm c

/-- A negative control: multiplication by two does not obstruct the constant one. -/
theorem two_constant_one_vanishes : constantClass 2 1 = 0 := by
  rw [constant_class_eq_zero_iff 2 (by omega)]
  norm_num

/-- Multiplication by three does obstruct the constant one. -/
theorem three_constant_one_nonzero : constantClass 3 1 ≠ 0 := by
  rw [ne_eq, constant_class_eq_zero_iff 3 (by omega)]
  norm_num

/-- Multiplication by three does not obstruct the constant two. -/
theorem three_constant_two_vanishes : constantClass 3 2 = 0 := by
  rw [constant_class_eq_zero_iff 3 (by omega)]
  norm_num

end Komorebi.MultiplierTower
