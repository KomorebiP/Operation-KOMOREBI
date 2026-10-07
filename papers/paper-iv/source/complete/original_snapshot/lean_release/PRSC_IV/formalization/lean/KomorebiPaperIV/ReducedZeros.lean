/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ReducedEntire

namespace Komorebi.PaperIV
noncomputable section
open Metric Set

theorem exists_complex_nth_root {N : ℕ} (hN : 0 < N) (w : ℂ) :
    ∃ z : ℂ, z ^ N = w := by
  by_cases hw : w = 0
  · exact ⟨0, by simp [hw, hN.ne']⟩
  refine ⟨Complex.exp (Complex.log w / N), ?_⟩
  rw [← Complex.exp_nat_mul, mul_div_cancel₀ _ (Nat.cast_ne_zero.mpr hN.ne'), Complex.exp_log hw]

theorem entireReducedDenominator_zero_ne_zero {N : ℕ} {w : ℂ}
    (hw : entireReducedDenominator N w = 0) : w ≠ 0 := by
  intro h; simp [h] at hw

theorem entireReducedDenominator_finite_zeros_on_compact {N : ℕ} (hN : 0 < N)
    {K : Set ℂ} (hK : IsCompact K) :
    {w ∈ K | entireReducedDenominator N w = 0}.Finite := by
  have ha : AnalyticOnNhd ℂ (entireReducedDenominator N) univ :=
    fun w _ => analyticAt_entireReducedDenominator hN w
  have hn : ¬ EqOn (entireReducedDenominator N) 0 univ := by
    intro h
    have hh := h (mem_univ (0 : ℂ))
    simp at hh
  have he := (ha.eqOn_zero_or_eventually_ne_zero_of_preconnected isPreconnected_univ).resolve_left hn
  have hk := (Filter.codiscreteWithin_mono (subset_univ K)) he
  exact (hK.finite_sdiff_of_mem_codiscreteWithin hk).subset fun _ hz => ⟨hz.1, fun hn => hn hz.2⟩

theorem onSignedZeroRay_power_positive {N : ℕ} (hN : 0 < N) {z : ℂ}
    (hz : onSignedZeroRay N z) : (z ^ N).im = 0 ∧ 0 < (z ^ N).re := by
  obtain ⟨k, _, t, ht, rfl⟩ := hz
  have hu : (canonicalPrimitiveRoot N ^ k) ^ N = 1 := by
    rw [← pow_mul, Nat.mul_comm, pow_mul, (canonicalPrimitiveRoot_isPrimitive hN).pow_eq_one, one_pow]
  rw [mul_pow, hu, one_mul, ← Complex.ofReal_pow]
  exact ⟨rfl, pow_pos ht N⟩

/-- The exceptional reduced zeros are a finite image of exceptional denominator zeros. -/
theorem entireReducedDenominator_finite_exceptional_zeros {N : ℕ} (hN : 2 ≤ N) :
    {w : ℂ | entireReducedDenominator N w = 0 ∧
      (analyticOrderAt (entireReducedDenominator N) w ≠ 1 ∨ w.im ≠ 0 ∨ w.re ≤ 0)}.Finite := by
  apply ((canonicalSignedDenominator_finite_exceptional_zeros hN).image (fun z : ℂ => z ^ N)).subset
  intro w hw
  obtain ⟨z, hz⟩ := exists_complex_nth_root (by omega : 0 < N) w
  have hz0 : z ≠ 0 := by
    intro h; apply entireReducedDenominator_zero_ne_zero hw.1
    rw [← hz, h, zero_pow (by omega : N ≠ 0)]
  have hd : canonicalSignedDenominator N z = 0 := by
    rw [canonicalSignedDenominator_eq_reduced_power (by omega), hz]; exact hw.1
  refine ⟨z, ⟨hd, ?_⟩, hz⟩
  by_contra h
  push Not at h
  have ho := canonicalSignedDenominator_order_eq_reduced (by omega : 0 < N) hz0
  rw [hz] at ho
  have hp := onSignedZeroRay_power_positive (by omega : 0 < N) h.2
  rw [hz] at hp
  rcases hw.2 with he | hi | hr
  · exact he (ho.symm.trans h.1)
  · exact hi hp.1
  · exact not_le_of_gt hp.2 hr

/-- Pointwise exhaustion and multiplicity for all sufficiently large reduced zeros. -/
theorem entireReducedDenominator_eventually_positive_simple {N : ℕ} (hN : 2 ≤ N) :
    ∃ R : ℝ, 0 < R ∧ ∀ w : ℂ, R ≤ ‖w‖ → entireReducedDenominator N w = 0 →
      analyticOrderAt (entireReducedDenominator N) w = 1 ∧ w.im = 0 ∧ 0 < w.re := by
  obtain ⟨R, hR, hex⟩ := canonicalSignedDenominator_eventually_simple_on_rays hN
  refine ⟨R ^ N, pow_pos hR N, ?_⟩
  intro w hw hw0
  obtain ⟨z, hz⟩ := exists_complex_nth_root (by omega : 0 < N) w
  have hz0 : z ≠ 0 := by
    intro h; apply entireReducedDenominator_zero_ne_zero hw0
    rw [← hz, h, zero_pow (by omega : N ≠ 0)]
  have hr : R ≤ ‖z‖ := by
    by_contra h
    have hp := pow_lt_pow_left₀ (lt_of_not_ge h) (norm_nonneg z) (by omega : N ≠ 0)
    have hn : ‖z‖ ^ N = ‖w‖ := by rw [← norm_pow, hz]
    linarith
  have hd : canonicalSignedDenominator N z = 0 := by
    rw [canonicalSignedDenominator_eq_reduced_power (by omega), hz]; exact hw0
  obtain ⟨ho, hp⟩ := hex z hr hd
  have hh := canonicalSignedDenominator_order_eq_reduced (by omega : 0 < N) hz0
  rw [hz] at hh
  refine ⟨hh.symm.trans ho, ?_⟩
  simpa [hz] using onSignedZeroRay_power_positive (by omega : 0 < N) hp

/-- The order-two reduced zeros are exactly the positive half-integer squares. -/
theorem entireReducedDenominator_two_zero_iff {w : ℂ} :
    entireReducedDenominator 2 w = 0 ↔
      ∃ m : ℕ, w = ((((m : ℂ) + 1 / 2) * Real.pi) ^ 2) := by
  have homega := canonicalPrimitiveRoot_isPrimitive (by norm_num : 0 < 2)
  have hrho := canonicalSignedRoot_pow (by norm_num : 0 < 2)
  constructor
  · intro hw
    obtain ⟨z, hz⟩ := exists_complex_nth_root (by norm_num : 0 < 2) w
    have hd : canonicalSignedDenominator 2 z = 0 := by
      rw [canonicalSignedDenominator_eq_reduced_power (by norm_num), hz]; exact hw
    obtain ⟨m, hm | hm⟩ := (entireSigned_two_zero_iff_nat homega hrho).mp hd
    · exact ⟨m, by rw [← hz, hm]⟩
    · exact ⟨m, by rw [← hz, hm, neg_sq]⟩
  · rintro ⟨m, rfl⟩
    rw [← canonicalSignedDenominator_eq_reduced_power (by norm_num)]
    exact (entireSigned_two_zero_iff_nat homega hrho).mpr ⟨m, Or.inl rfl⟩

theorem entireReducedDenominator_two_zero_order_one {w : ℂ}
    (hw : entireReducedDenominator 2 w = 0) :
    analyticOrderAt (entireReducedDenominator 2) w = 1 := by
  obtain ⟨z, hz⟩ := exists_complex_nth_root (by norm_num : 0 < 2) w
  have hz0 : z ≠ 0 := by
    intro h; apply entireReducedDenominator_zero_ne_zero hw; rw [← hz, h, zero_pow two_ne_zero]
  rw [← hz, ← canonicalSignedDenominator_order_eq_reduced (by norm_num) hz0]
  apply entireSigned_two_zero_order_one (canonicalPrimitiveRoot_isPrimitive (by norm_num))
    (canonicalSignedRoot_pow (by norm_num))
  change canonicalSignedDenominator 2 z = 0
  rw [canonicalSignedDenominator_eq_reduced_power (by norm_num), hz]; exact hw

end
end Komorebi.PaperIV
