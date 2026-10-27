import Komorebi.DyadicPrecision

set_option autoImplicit false
namespace Komorebi.RoundedPosterior

/-- A computable sufficient bit count. Integer logarithm avoids a linearly oversized precision. -/
def precisionFor (C δ : ℚ) : ℕ := Nat.log 2 (Nat.ceil (C/δ)) + 1

/-- The chosen dyadic denominator dominates the prescribed coefficient-to-slack ratio. -/
theorem coefficient_mesh_le (C δ : ℚ) (hδ : 0 < δ) (p : ℕ) (hp : precisionFor C δ ≤ p) :
    C*mesh p ≤ δ := by
  have hn : Nat.ceil (C/δ) ≤ 2^p := by
    have hlog := (Nat.lt_pow_succ_log_self (by norm_num : 1 < (2 : ℕ)) (Nat.ceil (C/δ))).le
    have hpow : 2^(Nat.log 2 (Nat.ceil (C/δ))+1) ≤ 2^p :=
      Nat.pow_le_pow_right (by norm_num) hp
    exact hlog.trans hpow
  have hratio : C/δ ≤ scale p := by
    apply (Nat.le_ceil (C/δ)).trans
    change (Nat.ceil (C/δ) : ℚ) ≤ (2 : ℚ)^p
    exact_mod_cast hn
  have hc : C ≤ scale p*δ := (div_le_iff₀ hδ).mp hratio
  change C*(1/scale p) ≤ δ
  rw [mul_one_div, div_le_iff₀ (scale_pos p)]
  nlinarith only [hc]

end Komorebi.RoundedPosterior
