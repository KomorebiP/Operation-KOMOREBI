module
public import FiniteMahler
public import Mathlib.NumberTheory.Padics.PadicVal.Basic
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.PeriodFromDifferences
open Mahler
variable (p : ℕ) [Fact p.Prime]

/-- A valuation of a positive natural number is strictly smaller than that number. -/
omit [Fact p.Prime] in
theorem valuation_lt (k : ℕ) (hk : 0 < k) : padicValNat p k < k :=
  (padicValNat_le_nat_log k).trans_lt (Nat.log_lt_self p hk.ne')

/-- The Newton coefficient provides the powers missing at low difference orders. -/
theorem binomial_precision (s k : ℕ) (hk : 0 < k) (hkn : k ≤ p^s) :
    p^(s+1) ∣ (p^s).choose k * p^k := by
  have hp : p.Prime := Fact.out
  have hN : 0 < p^s := pow_pos hp.pos s
  have hc : (p^s).choose k ≠ 0 := Nat.choose_ne_zero hkn
  have he := Nat.add_one_mul_choose_eq (p^s-1) (k-1)
  rw [Nat.sub_add_cancel (by omega : 1≤p^s), Nat.sub_add_cancel (by omega : 1≤k)] at he
  have hd : p^s ∣ (p^s).choose k * k := by rw [←he]; exact dvd_mul_right _ _
  have hv := (padicValNat_dvd_iff_le (Nat.mul_ne_zero hc hk.ne')).mp hd
  rw [padicValNat.mul hc hk.ne'] at hv
  have hvk := valuation_lt p k hk
  apply (padicValNat_dvd_iff_le (Nat.mul_ne_zero hc (pow_ne_zero _ hp.ne_zero))).mpr
  rw [padicValNat.mul hc (pow_ne_zero _ hp.ne_zero), padicValNat.prime_pow]
  omega

variable {R : Type*} [CommRing R]
/-- Finite Newton expansion isolates the positive-order contributions to a displacement. -/
theorem displacement_expansion (f : ℕ → R) (h n t : ℕ) :
    f (n+t*h)-f n = ∑ k ∈ Finset.range t,
      ((t.choose (k+1):ℕ):R)*difference h (k+1) f n := by
  have he : f (n+t*h) = ∑ k ∈ Finset.range (t+1),
      (t.choose k:R)*difference h k f n := by
    simpa [nsmul_eq_mul, difference] using shift_eq_sum_fwdDiff_iter h f t n
  rw [he, Finset.sum_range_succ']
  simp [difference, add_sub_cancel_right]

/-- Saturated higher differences imply a prime-power displacement congruence.
This uses the bounds at this row only, not a presumed period. -/
theorem prime_power_period (f : ℕ → R) (h n r : ℕ) (hr : 0<r)
    (H : ∀ k, (p:R)^(min k r) ∣ difference h k f n) :
    (p:R)^r ∣ f (n+p^(r-1)*h)-f n := by
  rw [displacement_expansion]
  apply Finset.dvd_sum
  intro k hk
  have hkr : k+1 ≤ p^(r-1) := by have := Finset.mem_range.mp hk; omega
  by_cases hsmall : k+1 < r
  · have hd := H (k+1)
    rw [min_eq_left (by omega : k+1≤r)] at hd
    obtain ⟨a,ha⟩ := hd
    rw [ha, ←mul_assoc]
    have hb := binomial_precision p (r-1) (k+1) (by omega) hkr
    rw [Nat.sub_add_cancel (by omega : 1≤r)] at hb
    have hcast : (p:R)^r ∣ (((p^(r-1)).choose (k+1):ℕ):R)*(p:R)^(k+1) := by
      obtain ⟨b,hb⟩ := hb
      refine ⟨(b:R), ?_⟩
      simpa only [Nat.cast_mul, Nat.cast_pow] using congrArg (fun a:ℕ => (a:R)) hb
    exact dvd_mul_of_dvd_left hcast a
  · have hd := H (k+1)
    rw [min_eq_right (by omega : r≤k+1)] at hd
    exact dvd_mul_of_dvd_right hd _

end KomorebiPaperIX.PeriodFromDifferences
