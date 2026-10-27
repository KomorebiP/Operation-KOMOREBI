/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedZeroOrbits
import Mathlib.Analysis.Analytic.IsolatedZeros

namespace Komorebi.PaperIV
noncomputable section
open Filter Metric Set

@[simp] theorem canonicalSignedDenominator_zero {N : ℕ} (hN : 0 < N) :
    canonicalSignedDenominator N 0 = 1 := by
  rw [canonicalSignedDenominator, entireSigned_zero_eq_average]
  simp [Nat.ne_of_gt hN]

/-- Compact sets contain only finitely many zeros of the actual entire denominator. -/
theorem canonicalSignedDenominator_finite_zeros_on_compact {N : ℕ} (hN : 0 < N)
    {K : Set ℂ} (hK : IsCompact K) :
    {z ∈ K | canonicalSignedDenominator N z = 0}.Finite := by
  have ha : AnalyticOnNhd ℂ (canonicalSignedDenominator N) univ :=
    fun z _ => analyticAt_entireSigned N 0 _ _ z
  have hn : ¬ EqOn (canonicalSignedDenominator N) 0 univ := by
    intro h
    have hh := h (mem_univ (0 : ℂ))
    simp [canonicalSignedDenominator_zero hN] at hh
  have he := (ha.eqOn_zero_or_eventually_ne_zero_of_preconnected isPreconnected_univ).resolve_left hn
  have hk := (codiscreteWithin_mono (subset_univ K)) he
  exact (hK.finite_sdiff_of_mem_codiscreteWithin hk).subset fun _ hz => ⟨hz.1, fun hn => hn hz.2⟩

/-- A point belongs to one of the `N` positive root-of-unity rays. -/
def onSignedZeroRay (N : ℕ) (z : ℂ) : Prop :=
  ∃ k < N, ∃ t : ℝ, 0 < t ∧ z = canonicalPrimitiveRoot N ^ k * (t : ℂ)

theorem canonicalSignedDenominator_eventually_simple_on_rays {N : ℕ} (hN : 2 ≤ N) :
    ∃ R : ℝ, 0 < R ∧ ∀ z : ℂ, R ≤ ‖z‖ → canonicalSignedDenominator N z = 0 →
      analyticOrderAt (canonicalSignedDenominator N) z = 1 ∧ onSignedZeroRay N z := by
  let : NeZero N := ⟨by omega⟩
  have homega := canonicalPrimitiveRoot_isPrimitive (by omega : 0 < N)
  rcases eq_or_lt_of_le hN with htwo | hthree
  · subst N
    refine ⟨1, by norm_num, ?_⟩
    intro z _ hz
    have hrho := canonicalSignedRoot_pow (by norm_num : 0 < 2)
    refine ⟨entireSigned_two_zero_order_one homega hrho hz, ?_⟩
    obtain ⟨m, hm | hm⟩ := (entireSigned_two_zero_iff_nat homega hrho).mp hz
    · refine ⟨0, by omega, ((m : ℝ) + 1 / 2) * Real.pi, by positivity, ?_⟩
      simpa using hm
    · refine ⟨1, by omega, ((m : ℝ) + 1 / 2) * Real.pi, by positivity, ?_⟩
      rw [pow_one, IsPrimitiveRoot.eq_neg_one_of_two_right homega]
      simpa using hm
  · obtain ⟨R, hR, hex⟩ := canonicalSignedDenominator_large_zero_orbits (by omega : 3 ≤ N) 0
    refine ⟨R, hR, ?_⟩
    intro z hz hz0
    obtain ⟨k, _, m, _, _, hi, hp, hs⟩ := hex z hz hz0
    have hu : (canonicalPrimitiveRoot N ^ k) ^ N = 1 := by
      rw [← pow_mul, Nat.mul_comm, pow_mul, homega.pow_eq_one, one_pow]
    have hui : ((canonicalPrimitiveRoot N ^ k)⁻¹) ^ N = 1 := by rw [inv_pow, hu, inv_one]
    obtain ⟨j, hj, he⟩ := homega.eq_pow_of_pow_eq_one hui
    have hu0 : canonicalPrimitiveRoot N ^ k ≠ 0 := by
      intro h; simp [h, Nat.ne_of_gt (show 0 < N by omega)] at hu
    refine ⟨hs, j, hj, (canonicalPrimitiveRoot N ^ k * z).re, hp, ?_⟩
    have hzreal : ((canonicalPrimitiveRoot N ^ k * z).re : ℂ) = canonicalPrimitiveRoot N ^ k * z := by
      apply Complex.ext <;> simp [hi]
    rw [hzreal, he, ← mul_assoc, inv_mul_cancel₀ hu0, one_mul]

/-- Corollary 11.11: the exceptional zeros form a finite set. -/
theorem canonicalSignedDenominator_finite_exceptional_zeros {N : ℕ} (hN : 2 ≤ N) :
    {z : ℂ | canonicalSignedDenominator N z = 0 ∧
      (analyticOrderAt (canonicalSignedDenominator N) z ≠ 1 ∨ ¬ onSignedZeroRay N z)}.Finite := by
  obtain ⟨R, _, hex⟩ := canonicalSignedDenominator_eventually_simple_on_rays hN
  apply (canonicalSignedDenominator_finite_zeros_on_compact (by omega : 0 < N)
    (isCompact_closedBall (0 : ℂ) R)).subset
  intro z hz
  refine ⟨?_, hz.1⟩
  rw [mem_closedBall, dist_zero_right]
  by_contra h
  have hh := hex z (le_of_lt (lt_of_not_ge h)) hz.1
  exact hz.2.elim (fun h => h hh.1) (fun h => h hh.2)

end
end Komorebi.PaperIV
