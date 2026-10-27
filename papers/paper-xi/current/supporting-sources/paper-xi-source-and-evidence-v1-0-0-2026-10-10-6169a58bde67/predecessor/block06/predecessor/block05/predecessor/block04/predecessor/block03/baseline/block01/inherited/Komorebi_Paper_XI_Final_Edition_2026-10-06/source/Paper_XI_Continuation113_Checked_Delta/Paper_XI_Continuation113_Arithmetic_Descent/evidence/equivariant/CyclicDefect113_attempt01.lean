import PaperXI.ScalarCocycle112
import Mathlib.Data.Int.GCD
import Mathlib.Algebra.Group.Hom.Instances
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

/-! Explicit coprime correction of the character defect left by scalar
cocycle comparison. Arithmetic realization is not asserted here. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CyclicDefect113
open Finset
open ScalarCocycle112

variable {A C : Type*} [CommGroup A] [CommGroup C]

/-- Norm of an arbitrary scalar function along a finite cyclic orbit. -/
def orbitNorm (β : A ≃* A) (f : A → C) (n : ℕ) (a : A) : C :=
  ∏ i ∈ range n, f ((β ^ i) a)

/-- Weighted norm, formed in the character group. -/
def weightedCharacter (β : A ≃* A) (r : A →* C) (n : ℕ) : A →* C :=
  ∏ i ∈ range n, (r.comp (β ^ i).toMonoidHom) ^ i

@[simp] theorem orbitNorm_zero (β : A ≃* A) (f : A → C) (a : A) :
    orbitNorm β f 0 a = 1 := by simp [orbitNorm]

theorem orbitNorm_succ (β : A ≃* A) (f : A → C) (n : ℕ) (a : A) :
    orbitNorm β f (n+1) a = orbitNorm β f n a * f ((β ^ n) a) := by
  simp [orbitNorm, prod_range_succ]

@[simp] theorem weightedCharacter_zero (β : A ≃* A) (r : A →* C) (a : A) :
    weightedCharacter β r 0 a = 1 := by simp [weightedCharacter]

theorem weightedCharacter_succ (β : A ≃* A) (r : A →* C) (n : ℕ) (a : A) :
    weightedCharacter β r (n+1) a =
      weightedCharacter β r n a * r ((β ^ n) a) ^ n := by
  simp [weightedCharacter, prod_range_succ]

theorem power_apply_shift (β : A ≃* A) (n : ℕ) (a : A) :
    (β ^ n) (β a) = (β ^ (n+1)) a := by
  rw [pow_succ]
  rfl

/-- The weighted norm is an explicit contracting operator for cyclic defects. -/
theorem weightedCharacter_shift (β : A ≃* A) (r : A →* C) (n : ℕ) (a : A) :
    weightedCharacter β r n (β a) * orbitNorm β r n (β a) =
      weightedCharacter β r n a * r ((β ^ n) a) ^ n := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [weightedCharacter_succ, orbitNorm_succ, weightedCharacter_succ,
      power_apply_shift]
    calc
      _ = (weightedCharacter β r n (β a) * orbitNorm β r n (β a)) *
          r ((β ^ (n+1)) a) ^ (n+1) := by rw [pow_succ]; ac_rfl
      _ = _ := by rw [ih]; ac_rfl

/-- A Bezout power inverts n-th powers on the m-torsion subgroup. -/
theorem bezout_power {n m : ℕ} (hcop : n.Coprime m) (z : C) (hm : z ^ m = 1) :
    (z ^ n) ^ (Nat.gcdA n m) = z := by
  have hbez : (1 : ℤ) = n * Nat.gcdA n m + m * Nat.gcdB n m := by
    simpa only [hcop.gcd_eq_one, Int.natCast_one] using Nat.gcd_eq_gcd_ab n m
  calc
    (z ^ n) ^ (Nat.gcdA n m) = z ^ (n * Nat.gcdA n m) := by
      rw [← zpow_natCast, ← zpow_mul]
    _ = z ^ (n * Nat.gcdA n m) * z ^ (m * Nat.gcdB n m) := by
      rw [zpow_mul, zpow_natCast, hm, one_zpow, mul_one]
    _ = z := by rw [← zpow_add, ← hbez, zpow_one]

/-- The correcting character is explicit, using a weighted norm and Bezout. -/
def correctingCharacter (β : A ≃* A) (r : A →* C) (n m : ℕ) : A →* C :=
  weightedCharacter β r n ^ (Nat.gcdA n m)

/-- Every norm-one character defect for a coprime cyclic action is a
coboundary. No correcting character is assumed. -/
theorem correctingCharacter_coboundary (β : A ≃* A) (r : A →* C)
    (n m : ℕ) (hβ : β ^ n = 1) (hm : ∀ a : A, a ^ m = 1)
    (hcop : n.Coprime m) (hnorm : ∀ a, orbitNorm β r n a = 1) (a : A) :
    correctingCharacter β r n m (β a) / correctingCharacter β r n m a = r a := by
  have ht := weightedCharacter_shift β r n a
  rw [hnorm, mul_one, hβ] at ht
  change weightedCharacter β r n (β a) = weightedCharacter β r n a * r a ^ n at ht
  have hr : r a ^ m = 1 := by rw [← map_pow, hm, map_one]
  change weightedCharacter β r n (β a) ^ (Nat.gcdA n m) /
    weightedCharacter β r n a ^ (Nat.gcdA n m) = _
  rw [ht, mul_zpow, mul_div_cancel_left]
  exact bezout_power hcop (r a) hr

end PaperXI.CyclicDefect113
