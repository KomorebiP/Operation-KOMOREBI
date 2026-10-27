import Mathlib.NumberTheory.Padics.Hensel
import Mathlib.NumberTheory.Padics.RingHoms
import Mathlib.Tactic

/-! Effective local image of an integral polynomial on a sufficiently small ball.
    This file treats scalar p-adic integers, not matrix-valued polynomials. -/

namespace Komorebi.StrongArtin.EffectiveResonance

open Polynomial

variable {p : ℕ} [Fact p.Prime]

theorem polynomial_norm_difference (P : Polynomial (PadicInt p)) (a z : PadicInt p)
    (hz : ‖z - a‖ < ‖P.derivative.eval a‖) :
    ‖P.eval z - P.eval a‖ = ‖P.derivative.eval a‖ * ‖z - a‖ := by
  obtain ⟨q, hq⟩ := P.binomExpansion a (z - a)
  have he : P.eval z - P.eval a =
      (P.derivative.eval a + q * (z - a)) * (z - a) := by
    have ha : a + (z - a) = z := by ring
    rw [ha] at hq
    rw [hq]
    ring
  have hsmall : ‖q * (z - a)‖ < ‖P.derivative.eval a‖ := by
    calc
      ‖q * (z - a)‖ = ‖q‖ * ‖z - a‖ := norm_mul _ _
      _ ≤ 1 * ‖z - a‖ := mul_le_mul_of_nonneg_right (PadicInt.norm_le_one q) (norm_nonneg _)
      _ < ‖P.derivative.eval a‖ := by simpa using hz
  rw [he, norm_mul, PadicInt.norm_add_eq_max_of_ne (ne_of_gt hsmall), max_eq_left hsmall.le]

theorem polynomial_ball_root_iff (P : Polynomial (PadicInt p)) (a : PadicInt p)
    (ρ : ℝ) (hρ : 0 ≤ ρ) (hsmall : ρ < ‖P.derivative.eval a‖) :
    (∃! z : PadicInt p, P.eval z = 0 ∧ ‖z - a‖ ≤ ρ) ↔
      ‖P.eval a‖ ≤ ‖P.derivative.eval a‖ * ρ := by
  have hd : 0 < ‖P.derivative.eval a‖ := lt_of_le_of_lt hρ hsmall
  constructor
  · rintro ⟨z, ⟨hz, hdist⟩, _⟩
    have he := polynomial_norm_difference P a z (lt_of_le_of_lt hdist hsmall)
    simp only [hz, zero_sub, norm_neg] at he
    rw [he]
    exact mul_le_mul_of_nonneg_left hdist hd.le
  · intro he
    have hh : ‖P.eval a‖ < ‖P.derivative.eval a‖ ^ 2 :=
      lt_of_le_of_lt he (by nlinarith)
    have hh' : ‖P.aeval a‖ < ‖P.derivative.aeval a‖ ^ 2 := by simpa using hh
    obtain ⟨z, hz, hza, _, hu⟩ := hensels_lemma hh'
    have hz' : P.eval z = 0 := by simpa using hz
    have hza' : ‖z - a‖ < ‖P.derivative.eval a‖ := by simpa using hza
    have heq := polynomial_norm_difference P a z hza'
    simp only [hz', zero_sub, norm_neg] at heq
    have hdist : ‖z - a‖ ≤ ρ := by rw [heq] at he; nlinarith
    refine ⟨z, ⟨hz', hdist⟩, ?_⟩
    intro w hw
    apply hu w
    · simpa using hw.1
    · simpa using lt_of_le_of_lt hw.2 hsmall

theorem reduction_eq_iff_norm (m : ℕ) (x y : PadicInt p) :
    PadicInt.toZModPow m x = PadicInt.toZModPow m y ↔
      ‖x - y‖ ≤ (p : ℝ) ^ (-(m : ℤ)) := by
  rw [PadicInt.norm_le_pow_iff_mem_span_pow, ← PadicInt.ker_toZModPow,
    RingHom.mem_ker, map_sub, sub_eq_zero]

theorem polynomial_prefix_root_iff (P : Polynomial (PadicInt p)) (a : PadicInt p)
    (m s : ℕ) (hsm : s < m)
    (hd : ‖P.derivative.eval a‖ = (p : ℝ) ^ (-(s : ℤ))) :
    (∃! z : PadicInt p, P.eval z = 0 ∧
      PadicInt.toZModPow m z = PadicInt.toZModPow m a) ↔
      PadicInt.toZModPow (m + s) (P.eval a) = 0 := by
  have hp : (1 : ℝ) < p := by exact_mod_cast (Fact.out : p.Prime).one_lt
  have hρ : 0 ≤ (p : ℝ) ^ (-(m : ℤ)) := (zpow_pos (lt_trans zero_lt_one hp) _).le
  have hsmall : (p : ℝ) ^ (-(m : ℤ)) < ‖P.derivative.eval a‖ := by
    rw [hd]
    apply (zpow_lt_zpow_iff_right₀ hp).2
    omega
  have h := polynomial_ball_root_iff P a _ hρ hsmall
  simp only [← reduction_eq_iff_norm] at h
  rw [h, hd]
  have hmul : (p : ℝ) ^ (-(s : ℤ)) * (p : ℝ) ^ (-(m : ℤ)) =
      (p : ℝ) ^ (-((m + s : ℕ) : ℤ)) := by
    rw [← zpow_add₀ (ne_of_gt (lt_trans zero_lt_one hp))]
    congr 1
    omega
  rw [hmul]
  simpa using (reduction_eq_iff_norm (m + s) (P.eval a) 0).symm

end Komorebi.StrongArtin.EffectiveResonance
