module

public import FiniteMahler

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.DifferenceFiltration

open Mahler

variable {R : Type*} [CommRing R]

/-- A congruence on a forward tail remains a congruence at every positive difference order. -/
theorem tail_period_higher_difference (d : R) (h n₀ : ℕ) (f : ℕ → R)
    (H : ∀ n, n₀≤n → d ∣ f (n+h)-f n) (k n : ℕ) (hk : 0<k) (hn : n₀≤n) :
    d ∣ difference h k f n := by
  induction k generalizing n with
  | zero => omega
  | succ k ih =>
    by_cases h0 : k=0
    · subst k; simpa using H n hn
    · rw [difference_succ]
      exact dvd_sub (ih (n+h) (by omega) (by omega)) (ih n (by omega) hn)

/-- Extends the triangular region k<=m*n to all orders by saturation.
This is an implication; it does not assert the triangular estimates for Euler packets. -/
theorem saturated_bound_of_triangular (p : R) (m h : ℕ) (f : ℕ → R)
    (H : ∀ n k, k≤m*n → p^k ∣ difference h k f n) (k n : ℕ) :
    p^(min k (m*n)) ∣ difference h k f n := by
  induction k generalizing n with
  | zero => simp
  | succ k ih =>
    by_cases hk : k+1≤m*n
    · rw [min_eq_left hk]; exact H n (k+1) hk
    · have hkn : m*n≤k := by omega
      rw [min_eq_right (by omega : m*n≤k+1), difference_succ]
      apply dvd_sub
      · apply dvd_trans (pow_dvd_pow p (le_min hkn (Nat.mul_le_mul_left m (by omega : n≤n+h))))
        exact ih (n+h)
      · apply dvd_trans (pow_dvd_pow p (le_min hkn le_rfl))
        exact ih n

/-- The triangular estimates and the complete saturated estimate are equivalent. -/
theorem saturated_bound_iff (p : R) (m h : ℕ) (f : ℕ → R) :
    (∀ n k, p^(min k (m*n)) ∣ difference h k f n) ↔
      (∀ n k, k≤m*n → p^k ∣ difference h k f n) := by
  constructor
  · intro H n k hk; simpa [min_eq_left hk] using H n k
  · intro H n k; exact saturated_bound_of_triangular p m h f H k n

/-- Difference stencils commute with every coefficient-ring homomorphism. -/
theorem difference_map {S : Type*} [CommRing S] (φ : R →+* S)
    (h k : ℕ) (f : ℕ → R) (n : ℕ) :
    difference h k (fun j => φ (f j)) n = φ (difference h k f n) := by
  induction k generalizing n with
  | zero => rfl
  | succ k ih => rw [difference_succ, difference_succ, ih, ih, map_sub]

end KomorebiPaperIX.DifferenceFiltration
