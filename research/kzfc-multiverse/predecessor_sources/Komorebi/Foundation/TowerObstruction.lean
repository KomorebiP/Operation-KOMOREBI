import Komorebi.Foundation.KappaResidualReflection
import Mathlib.GroupTheory.QuotientGroup.Basic
import Mathlib.Tactic.Ring

/-!
# A fixed-integer-domain reconstruction obstruction

The difference operator for the integer tower with bonding map multiplication by 3
has a nonzero cokernel class represented by the constant sequence 1. Every finite
prefix of the corresponding inhomogeneous equations is solvable. The cokernel is
constructed explicitly; no identification with Mathlib's derived functor is asserted.
-/

namespace Komorebi.IntegerTower

abbrev Sequence := ℕ → ℤ

/-- The usual product difference operator for the multiplication-by-three tower. -/
def delta : Sequence →+ Sequence where
  toFun a n := a n - 3 * a (n + 1)
  map_zero' := by ext n; simp
  map_add' a b := by ext n; simp only [Pi.add_apply]; ring

def ones : Sequence := fun _ => 1

/-- Recursive integer geometric sum, avoiding division in finite lifts. -/
def geometric : ℕ → ℤ
  | 0 => 0
  | n + 1 => 1 + 3 * geometric n

/-- A lift with terminal value zero at the end of a finite prefix. -/
def prefixLift (N : ℕ) : Sequence := fun n => geometric (N - n)

theorem prefixLift_solves (N n : ℕ) (hn : n < N) :
    delta (prefixLift N) n = 1 := by
  change geometric (N - n) - 3 * geometric (N - (n + 1)) = 1
  have hsub : N - n = (N - (n + 1)) + 1 := by omega
  rw [hsub, geometric]
  ring

/-- Every finite initial segment of the inhomogeneous equations has an integer lift. -/
theorem every_prefix_solvable (N : ℕ) :
    ∃ a : Sequence, ∀ n < N, delta a n = ones n := by
  exact ⟨prefixLift N, fun n hn => prefixLift_solves N n hn⟩

/-- Any finite set of equations, not only an initial segment, has an integer lift. -/
theorem every_finite_set_solvable (J : Finset ℕ) :
    ∃ a : Sequence, ∀ n ∈ J, delta a n = ones n := by
  refine ⟨prefixLift (J.sup id + 1), ?_⟩
  intro n hn
  apply prefixLift_solves
  have hle : n ≤ J.sup id := Finset.le_sup (f := id) hn
  omega

/-- Iteration of a hypothetical global lift gives an exact divisibility identity. -/
theorem iterate_identity (a : Sequence) (ha : delta a = ones) (n : ℕ) :
    2 * a 0 + 1 = (3 : ℤ) ^ n * (2 * a n + 1) := by
  induction n with
  | zero => simp
  | succ n ih =>
      have hstep : a n - 3 * a (n + 1) = 1 := congrFun ha n
      rw [ih, pow_succ]
      have hstep' : 2 * a n + 1 = 3 * (2 * a (n + 1) + 1) := by omega
      rw [hstep']
      ring

/-- No integer is nonzero and divisible by every power of three. -/
theorem eq_zero_of_all_three_powers_dvd (z : ℤ)
    (h : ∀ n : ℕ, (3 : ℤ) ^ n ∣ z) : z = 0 := by
  apply Int.eq_zero_of_dvd_of_natAbs_lt_natAbs (h z.natAbs)
  simpa using (Nat.lt_pow_self (n := z.natAbs) (show 1 < 3 by omega))

/-- The constant sequence 1 has no global integer lift under the tower difference. -/
theorem no_global_lift : ¬ ∃ a : Sequence, delta a = ones := by
  rintro ⟨a, ha⟩
  have hz : 2 * a 0 + 1 = 0 := eq_zero_of_all_three_powers_dvd _ (fun n =>
    ⟨2 * a n + 1, iterate_identity a ha n⟩)
  omega

/-- The explicit product-cokernel obstruction group. -/
abbrev ObstructionGroup := Sequence ⧸ delta.range

/-- The obstruction class of the inhomogeneous sequence. -/
def obstruction : ObstructionGroup := QuotientAddGroup.mk ones

/-- Vanishing is exactly existence of a lift. -/
theorem obstruction_eq_zero_iff : obstruction = 0 ↔ ∃ a : Sequence, delta a = ones := by
  change QuotientAddGroup.mk ones = (0 : ObstructionGroup) ↔ _
  rw [QuotientAddGroup.eq_zero_iff]
  rfl

/-- A concrete nonzero residual, established over the ordinary integers. -/
theorem obstruction_ne_zero : obstruction ≠ 0 := by
  intro h
  exact no_global_lift (obstruction_eq_zero_iff.mp h)

end Komorebi.IntegerTower
