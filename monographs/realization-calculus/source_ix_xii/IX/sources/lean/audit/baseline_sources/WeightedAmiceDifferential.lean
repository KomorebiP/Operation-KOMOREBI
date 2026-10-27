module
public import WeightedAmice
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.WeightedAmice
open PowerSeries
variable (p : ℕ) [hp : Fact p.Prime]

theorem linear_le_power (q : ℕ) : q+1≤p^q := by
  induction q with
  | zero => simp
  | succ q ih =>
    rw [pow_succ]
    have h2 := hp.out.two_le
    have h1 : 1≤p^q := le_trans (by omega) ih
    nlinarith

theorem valuation_le_floor (n : ℕ) (hn : n≠0) : padicValNat p n≤n/p := by
  have hpow : p^(padicValNat p n)≤n := Nat.le_of_dvd (Nat.pos_of_ne_zero hn) pow_padicValNat_dvd
  cases hv : padicValNat p n with
  | zero => exact Nat.zero_le _
  | succ v =>
    rw [hv, pow_succ] at hpow
    apply (Nat.le_div_iff_mul_le hp.out.pos).mpr
    have hlin := linear_le_power p v
    nlinarith

/-- A denominator loses exactly its p-part, before a larger allowed weight is applied. -/
theorem inverse_nat_integral (n : ℕ) (hn : n≠0) :
    Integral p ((p:ℚ_[p])^(padicValNat p n)/(n:ℚ_[p])) := by
  have hp0 : (p:ℚ)≠0 := Nat.cast_ne_zero.mpr hp.out.ne_zero
  have hn0 : (n:ℚ)≠0 := Nat.cast_ne_zero.mpr hn
  have hq0 : (p:ℚ)^(padicValNat p n)/(n:ℚ)≠0 := div_ne_zero (pow_ne_zero _ hp0) hn0
  have hv : padicValRat p ((p:ℚ)^(padicValNat p n)/(n:ℚ))=0 := by
    rw [padicValRat.div (pow_ne_zero _ hp0) hn0]
    simp [padicValRat.self hp.out.one_lt]
  let q : ℚ := (p:ℚ)^(padicValNat p n)/(n:ℚ)
  have he : (p:ℚ_[p])^(padicValNat p n)/(n:ℚ_[p]) = (q:ℚ_[p]) := by
    simp only [q, Rat.cast_div, Rat.cast_pow, Rat.cast_natCast]
  rw [he]
  change ‖(q:ℚ_[p])‖≤1
  rw [Padic.eq_padicNorm, padicNorm.eq_zpow_of_nonzero hq0, hv]
  norm_num

/-- Formal differentiation preserves the weighted class; multiples of p supply the extra factor. -/
theorem weighted_derivative {f : PowerSeries ℚ_[p]} (hf : Weighted p f) :
    Weighted p (derivative ℚ_[p] f) := by
  intro n
  rw [coeff_derivative]
  have hh := hf (n+1)
  by_cases hd : p ∣ n+1
  · have he : (n+1)/p=n/p+1 := by rw [Nat.succ_div, ite_eq_left hd]
    rw [he] at hh
    obtain ⟨q,hq⟩ := hd
    have hq' : (n+1 : ℚ_[p]) = (p:ℚ_[p])*(q:ℚ_[p]) := by exact_mod_cast hq
    convert integral_mul p (integral_nat p q) hh using 1
    rw [hq', pow_succ]
    ring
  · have he : (n+1)/p=n/p := by rw [Nat.succ_div, ite_eq_right hd, add_zero]
    rw [he] at hh
    convert integral_mul p hh (integral_nat p (n+1)) using 1
    push_cast
    ring

theorem weighted_X : Weighted p (X : PowerSeries ℚ_[p]) := by
  intro n
  rw [coeff_X]
  by_cases h : n=1
  · subst n
    rw [ite_eq_left rfl, mul_one]
    exact integral_pow p (integral_nat p p) (1/p)
  · rw [ite_eq_right h, mul_zero]
    exact integral_zero p

theorem weighted_log : Weighted p (log ℚ_[p]) := by
  intro n
  rw [coeff_log]
  by_cases hn : n=0
  · rw [ite_eq_left hn, mul_zero]
    exact integral_zero p
  · rw [ite_eq_right hn]
    have h1 : Integral p ((p:ℚ_[p])^(n/p)*(1/(n:ℚ_[p]))) := by
      apply scaled_mono p (valuation_le_floor p n hn)
      simpa only [mul_one_div] using inverse_nat_integral p n hn
    have hm := integral_mul p (integral_pow p (integral_int p (-1)) (n+1)) h1
    convert hm using 1
    simp only [map_div₀, map_pow, map_neg, map_one, map_natCast, Int.cast_neg, Int.cast_one]
    ring

/-- The actual transformed Euler vector field. -/
def eulerLog (f : PowerSeries ℚ_[p]) : PowerSeries ℚ_[p] :=
  log ℚ_[p] * (1+X) * derivative ℚ_[p] f

theorem weighted_eulerLog {f : PowerSeries ℚ_[p]} (hf : Weighted p f) :
    Weighted p (eulerLog p f) :=
  weighted_mul p (weighted_mul p (weighted_log p)
    (weighted_add p (weighted_one p) (weighted_X p))) (weighted_derivative p hf)

end KomorebiPaperIX.WeightedAmice
