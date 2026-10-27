import Mathlib.Data.Nat.Choose.Lucas
import Mathlib.NumberTheory.Padics.PadicVal.Basic

namespace KomorebiCrossRadix

/-- The exact standard-window congruence. The hypothesis needed for this local
statement is only `p ∣ N` and `j < p`; no `m ∣ p-1` assumption is required. -/
theorem standardWindow_choose_modEq_one
    {p N n j : ℕ} [Fact p.Prime]
    (hN : p ∣ N) (hj : j < p) :
    Nat.choose (N * n + j) j ≡ 1 [MOD p] := by
  have h := Choose.choose_modEq_choose_mod_mul_choose_div_nat
    (p := p) (n := N * n + j) (k := j)
  have hNmod : N % p = 0 := Nat.mod_eq_zero_of_dvd hN
  have hjmod : j % p = j := Nat.mod_eq_of_lt hj
  have hjdiv : j / p = 0 := Nat.div_eq_of_lt hj
  have htopmod : (N * n + j) % p = j := by
    simp [Nat.add_mod, Nat.mul_mod, hNmod, hjmod]
  rw [htopmod, hjmod, hjdiv] at h
  simpa using h

/-- Consequently the standard-window binomial coefficient is prime to `p`. -/
theorem standardWindow_choose_not_dvd
    {p N n j : ℕ} [Fact p.Prime]
    (hN : p ∣ N) (hj : j < p) :
    ¬ p ∣ Nat.choose (N * n + j) j := by
  intro hdvd
  have hmod := standardWindow_choose_modEq_one (p := p) (N := N) (n := n) (j := j) hN hj
  have hzero : Nat.choose (N * n + j) j ≡ 0 [MOD p] := by
    exact Nat.modEq_zero_iff_dvd.mpr hdvd
  have hone : (1 : ℕ) ≡ 0 [MOD p] := hmod.symm.trans hzero
  exact (Fact.out : p.Prime).not_dvd_one (Nat.modEq_zero_iff_dvd.mp hone)

/-- The exact `p`-adic valuation of the standard-window binomial is zero. -/
theorem standardWindow_choose_padicValNat_eq_zero
    {p N n j : ℕ} [Fact p.Prime]
    (hN : p ∣ N) (hj : j < p) :
    padicValNat p (Nat.choose (N * n + j) j) = 0 := by
  exact padicValNat.eq_zero_of_not_dvd
    (standardWindow_choose_not_dvd (p := p) (N := N) (n := n) (j := j) hN hj)

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.standardWindow_choose_modEq_one
#print axioms KomorebiCrossRadix.standardWindow_choose_padicValNat_eq_zero
