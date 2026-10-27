module

public import DifferenceFiltration

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.StepMultiples

open Mahler

variable {R : Type*} [CommRing R]

/-- The literal sum of the forward h-translates, including the empty sum at u=0. -/
def translateSum (h u : ℕ) (f : ℕ → R) (n : ℕ) : R :=
  ∑ a ∈ Finset.range u, f (n+a*h)

theorem difference_translate (h k a : ℕ) (f : ℕ → R) (n : ℕ) :
    difference h k (fun r => f (r+a)) n = difference h k f (n+a) :=
  fwdDiff_iter_comp_add h f a k n

/-- Actual telescoping of a longer step, not an assumed operator factorization. -/
theorem single_step_telescope (h u : ℕ) (f : ℕ → R) (n : ℕ) :
    f (n+u*h)-f n = translateSum h u (difference h 1 f) n := by
  induction u with
  | zero => simp [translateSum]
  | succ u ih =>
    simp only [translateSum, Finset.sum_range_succ, difference_one] at ih ⊢
    rw [← ih]
    rw [Nat.succ_mul, ← Nat.add_assoc]
    ring

theorem difference_commute_one (h k H : ℕ) (f : ℕ → R) :
    difference h k (difference H 1 f) = difference H 1 (difference h k f) := by
  funext n
  induction k generalizing n with
  | zero => rfl
  | succ k ih =>
    rw [difference_succ, ih, ih, difference_one, difference_one,
      difference_one, difference_succ, difference_succ]
    rw [show n+h+H=n+H+h by omega]
    ring

/-- Longer-step differences are controlled by shorter-step differences on the whole forward tail. -/
theorem divisibility_transfer (d : R) (h u k n₀ : ℕ) (f : ℕ → R)
    (H : ∀ n, n₀≤n → d∣difference h k f n) :
    ∀ n, n₀≤n → d∣difference (u*h) k f n := by
  induction k generalizing f with
  | zero => exact H
  | succ k ih =>
    have hs : ∀ n, n₀≤n → d∣difference h k (difference (u*h) 1 f) n := by
      intro n hn
      rw [difference_commute_one, difference_one, single_step_telescope]
      unfold translateSum
      apply Finset.dvd_sum
      intro a _
      have he : difference h 1 (difference h k f) (n+a*h) = difference h (k+1) f (n+a*h) := by
        rw [difference_one, difference_succ]
      rw [he]
      exact H _ (by omega)
    have hr := ih (difference (u*h) 1 f) hs
    intro n hn
    have hn' := hr n hn
    have he : difference (u*h) k (difference (u*h) 1 f) n =
        difference (u*h) (k+1) f n := by
      simp only [difference, Function.iterate_add_apply]
    rw [he] at hn'
    exact hn'

/-- Monotone row precision transfers to every multiple of the original step. -/
theorem saturated_multiple_step (p : R) (m h : ℕ) (f : ℕ → R)
    (H : ∀ k n, p^(min k (m*n))∣difference h k f n) (u k n : ℕ) :
    p^(min k (m*n))∣difference (u*h) k f n := by
  apply divisibility_transfer (p^(min k (m*n))) h u k n f _ n le_rfl
  intro r hr
  apply dvd_trans (pow_dvd_pow p (min_le_min le_rfl (Nat.mul_le_mul_left m hr)))
  exact H k r

end KomorebiPaperIX.StepMultiples
