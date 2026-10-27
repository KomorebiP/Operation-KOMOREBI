import RealizationBoundaries.RootFibers
import Mathlib.Data.Nat.Factorization.Basic
import Mathlib.Data.Fintype.BigOperators

/-! # Exact finite root counts

The radical is the product of distinct prime divisors. All root-count statements
retain m > 0, so the convention for the product at zero cannot conceal an
infinite zero-multiplier fiber behind Nat.card's value zero.
-/
set_option autoImplicit false
noncomputable section
open scoped BigOperators
namespace RealizationBoundaries

/-- Product of distinct prime divisors. Only positive multipliers enter root counts. -/
def primeRadical (m : ℕ) : ℕ := ∏ p ∈ m.primeFactors, p

theorem primeRadical_pos (m : ℕ) : 0 < primeRadical m :=
  Finset.prod_pos (fun _ hp => Nat.pos_of_mem_primeFactors hp)

@[simp] theorem primeRadical_one : primeRadical 1 = 1 := by simp [primeRadical]

@[simp] theorem primeRadical_prime {p : ℕ} (hp : p.Prime) : primeRadical p = p := by
  simp [primeRadical, hp.primeFactors]

/-- Repeated prime powers do not change the radical. -/
theorem primeRadical_pow (m : ℕ) {k : ℕ} (hk : k ≠ 0) :
    primeRadical (m ^ k) = primeRadical m := by
  simp only [primeRadical, Nat.primeFactors_pow m hk]

theorem primeRadical_prime_pow {p k : ℕ} (hp : p.Prime) (hk : k ≠ 0) :
    primeRadical (p ^ k) = p := by
  rw [primeRadical_pow p hk, primeRadical_prime hp]

theorem primeRadical_dvd (m : ℕ) : primeRadical m ∣ m := Nat.prod_primeFactors_dvd m

theorem prime_dvd_radical_iff {m : ℕ} (hm : 0 < m) (p : Prime) :
    p.val ∣ primeRadical m ↔ p.val ∣ m := by
  constructor
  · exact fun h => dvd_trans h (primeRadical_dvd m)
  · intro h
    exact Finset.dvd_prod_of_mem (fun n : ℕ => n)
      (p.property.mem_primeFactors h (Nat.ne_of_gt hm))

theorem primeRadical_dvd_of_dvd {m n : ℕ} (hn : 0 < n) (hmn : m ∣ n) :
    primeRadical m ∣ primeRadical n :=
  Finset.prod_dvd_prod_of_subset _ _ _ (Nat.primeFactors_mono hmn (Nat.ne_of_gt hn))

/-- Relate the actual subtype of prime divisors to the printed radical. -/
theorem divisorPrime_prod {m : ℕ} (hm : 0 < m) [Fintype (DivisorPrime m)] :
    (∏ p : DivisorPrime m, p.val.val) = primeRadical m := by
  classical
  apply Finset.prod_bij (fun (p : DivisorPrime m) _ => p.val.val)
  · intro p _
    exact p.val.property.mem_primeFactors p.property (Nat.ne_of_gt hm)
  · intro p _ q _ h
    exact Subtype.ext (Subtype.ext h)
  · intro p hp
    exact ⟨⟨⟨p, Nat.prime_of_mem_primeFactors hp⟩, Nat.dvd_of_mem_primeFactors hp⟩,
      Finset.mem_univ _, rfl⟩
  · intro p _
    rfl

/-- Cardinality of the finite divisor-coordinate product, with no counted roots assumed. -/
theorem divisorCoordinates_card {m : ℕ} (hm : 0 < m) :
    Nat.card (DivisorCoordinates m) = primeRadical m := by
  let : Finite (DivisorPrime m) := divisorPrime_finite hm
  let := Fintype.ofFinite (DivisorPrime m)
  change Nat.card ((p : DivisorPrime m) → Coordinate p.val) = _
  rw [Nat.card_pi]
  simp only [Nat.card_eq_fintype_card, ZMod.card]
  exact divisorPrime_prod hm

/-- The torsion kernel contains exactly one independent factor per distinct prime. -/
theorem rootKernel_card (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m) :
    Nat.card (rootKernel W m) = primeRadical m :=
  (Nat.card_congr (rootKernelEquiv W hm).toEquiv).trans (divisorCoordinates_card hm)

/-- A supplied actual root parameterizes all roots, including the m=1 singleton case. -/
theorem rootFiber_card_of_root (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m)
    (x : preimage W) (y : RootFiber W m x) :
    Nat.card (RootFiber W m x) = primeRadical m :=
  (Nat.card_congr (rootFiberEquiv W hm x y)).trans (divisorCoordinates_card hm)

theorem rootFiber_card_of_solvable (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m)
    (x : preimage W) (h : ∃ y : preimage W, m • y = x) :
    Nat.card (RootFiber W m x) = primeRadical m := by
  obtain ⟨y, hy⟩ := h
  exact rootFiber_card_of_root W hm x ⟨y, hy⟩

theorem rootFiber_card_of_obstruction (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m)
    (x : preimage W) (p : Prime) (hp : p.val ∣ m) (hx : x.val p ≠ 0) :
    Nat.card (RootFiber W m x) = 0 := by
  let := rootFiber_isEmpty W m x (prime_obstruction W hm x p hp hx)
  exact Nat.card_of_isEmpty

open scoped Classical in
/-- Exact case split: an empty fiber or a finite radical-sized fiber. -/
theorem rootFiber_card (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m)
    (x : preimage W) :
    Nat.card (RootFiber W m x) =
      if ∀ p : Prime, p.val ∣ m → x.val p = 0 then primeRadical m else 0 := by
  classical
  split_ifs with h
  · exact rootFiber_card_of_solvable W hm x ((preimage_root_iff W hm x).mpr h)
  · let := rootFiber_isEmpty W m x (fun hy => h ((preimage_root_iff W hm x).mp hy))
    exact Nat.card_of_isEmpty

/-- Equality of actual multiple subgroups, not just matching quotient cardinalities. -/
theorem multiples_eq_radical (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m) :
    multiples W m = multiples W (primeRadical m) :=
  multiples_eq_of_same_prime_divisors W hm (primeRadical_pos m)
    (fun p => (prime_dvd_radical_iff hm p).symm)

/-- The already-constructed quotient has the same exact cardinal as a nonempty root fiber. -/
theorem integerQuotient_card (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m) :
    Nat.card (preimage W ⧸ multiples W m) = primeRadical m :=
  (Nat.card_congr (integerQuotientEquiv W hm).toEquiv).trans (divisorCoordinates_card hm)

end RealizationBoundaries
