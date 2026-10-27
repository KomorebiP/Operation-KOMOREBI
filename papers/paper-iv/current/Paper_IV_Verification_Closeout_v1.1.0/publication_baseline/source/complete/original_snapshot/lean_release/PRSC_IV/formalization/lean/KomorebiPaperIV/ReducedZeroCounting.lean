/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.FullZeroCounting

namespace Komorebi.PaperIV
noncomputable section
open Set Metric

def SignedZeroEnumeration.reducedRoot {N : ℕ} (e : SignedZeroEnumeration N) (m : ℕ) : ℂ :=
  (e.root m : ℂ) ^ N

def SignedZeroEnumeration.reducedDisk {N : ℕ} (e : SignedZeroEnumeration N) (r : ℝ) : Set ℂ :=
  e.reducedRoot '' {m | e.root m ≤ r}

def SignedZeroEnumeration.reducedExceptions {N : ℕ} (e : SignedZeroEnumeration N) : Set ℂ :=
  zeroDisk (entireReducedDenominator N) (e.radius ^ N) \ range e.reducedRoot

theorem SignedZeroEnumeration.reducedRoot_norm {N : ℕ} (e : SignedZeroEnumeration N) (m : ℕ) :
    ‖e.reducedRoot m‖ = e.root m ^ N := by
  rw [SignedZeroEnumeration.reducedRoot, norm_pow, Complex.norm_real, Real.norm_eq_abs, abs_of_pos (e.positive m)]

theorem SignedZeroEnumeration.reducedRoot_injective {N : ℕ} (hN : 0 < N)
    (e : SignedZeroEnumeration N) : Function.Injective e.reducedRoot := by
  intro m n h
  apply e.injective
  have hh := congrArg norm h
  rw [e.reducedRoot_norm, e.reducedRoot_norm] at hh
  exact (pow_left_strictMonoOn₀ hN.ne').injOn (e.positive m).le (e.positive n).le hh

theorem SignedZeroEnumeration.reducedRoot_zero_simple {N : ℕ} (hN : 0 < N)
    (e : SignedZeroEnumeration N) (m : ℕ) :
    entireReducedDenominator N (e.reducedRoot m) = 0 ∧
      analyticOrderNatAt (entireReducedDenominator N) (e.reducedRoot m) = 1 := by
  constructor
  · rw [SignedZeroEnumeration.reducedRoot, ← canonicalSignedDenominator_eq_reduced_power hN]
    exact e.zero m
  · rw [analyticOrderNatAt, SignedZeroEnumeration.reducedRoot,
      ← canonicalSignedDenominator_order_eq_reduced hN (Complex.ofReal_ne_zero.mpr (ne_of_gt (e.positive m))), e.simple]
    rfl

theorem SignedZeroEnumeration.reducedExceptions_finite {N : ℕ} (hN : 0 < N)
    (e : SignedZeroEnumeration N) : e.reducedExceptions.Finite :=
  (entireReducedDenominator_zeroDisk_finite hN (e.radius ^ N)).sdiff

theorem SignedZeroEnumeration.reducedDisk_finite_card {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) {r : ℝ} (hr : 0 ≤ r) :
    (e.reducedDisk r).Finite ∧ (e.reducedDisk r).ncard = sequenceCounting e.root r := by
  have hf := (lattice_window_counting (div_pos Real.pi_pos (signed_sine_pos hN)) e.shift e.root e.windows hr).1
  refine ⟨hf.image _, ?_⟩
  exact ncard_image_of_injective _ (e.reducedRoot_injective (by omega))

theorem SignedZeroEnumeration.reducedDisk_subset {N : ℕ} (hN : 0 < N)
    (e : SignedZeroEnumeration N) (r : ℝ) :
    e.reducedDisk r ⊆ zeroDisk (entireReducedDenominator N) (r ^ N) := by
  rintro w ⟨m, hm, rfl⟩
  refine ⟨?_, (e.reducedRoot_zero_simple hN m).1⟩
  rw [e.reducedRoot_norm]
  exact pow_le_pow_left₀ (e.positive m).le hm N

theorem SignedZeroEnumeration.reducedZeroDisk_subset_union {N : ℕ} (hN : 0 < N)
    (e : SignedZeroEnumeration N) {r : ℝ} (hr : 0 ≤ r) :
    zeroDisk (entireReducedDenominator N) (r ^ N) ⊆ e.reducedDisk r ∪ e.reducedExceptions := by
  classical
  intro w hw
  by_cases hwr : w ∈ range e.reducedRoot
  · obtain ⟨m, rfl⟩ := hwr
    apply Or.inl
    refine ⟨m, ?_, rfl⟩
    change e.root m ≤ r
    by_contra hm
    have hlt := pow_lt_pow_left₀ (lt_of_not_ge hm) hr hN.ne'
    have hb := hw.1
    rw [e.reducedRoot_norm] at hb
    exact not_le_of_gt hlt hb
  · apply Or.inr
    refine ⟨⟨?_, hw.2⟩, hwr⟩
    obtain ⟨z, hz⟩ := exists_complex_nth_root hN w
    have hz0 : canonicalSignedDenominator N z = 0 := by
      rw [canonicalSignedDenominator_eq_reduced_power hN, hz]; exact hw.2
    have hb : ‖z‖ ≤ e.radius := by
      by_contra h
      obtain ⟨k, m, he⟩ := e.exhaustive z (le_of_lt (lt_of_not_ge h)) hz0
      apply hwr
      refine ⟨m, ?_⟩
      have hu : (canonicalPrimitiveRoot N ^ k.val) ^ N = 1 := by
        rw [← pow_mul, Nat.mul_comm, pow_mul, (canonicalPrimitiveRoot_isPrimitive hN).pow_eq_one, one_pow]
      rw [← hz, he, mul_pow, hu, one_mul]
      rfl
    rw [← hz, norm_pow]
    exact pow_le_pow_left₀ (norm_nonneg z) hb N

theorem SignedZeroEnumeration.reduced_weighted_count_bounds {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) {r : ℝ} (hr : 0 ≤ r) :
    sequenceCounting e.root r ≤ analyticZeroCount (entireReducedDenominator N) (r ^ N) ∧
      analyticZeroCount (entireReducedDenominator N) (r ^ N) ≤ sequenceCounting e.root r +
        finiteWeight (analyticOrderNatAt (entireReducedDenominator N)) e.reducedExceptions := by
  obtain ⟨hT, hc⟩ := e.reducedDisk_finite_card hN hr
  have hw : ∀ w ∈ e.reducedDisk r, analyticOrderNatAt (entireReducedDenominator N) w = 1 := by
    rintro _ ⟨m, _, rfl⟩
    exact (e.reducedRoot_zero_simple (by omega) m).2
  have h := finiteWeight_between_tail_and_exceptions (analyticOrderNatAt (entireReducedDenominator N))
    (entireReducedDenominator_zeroDisk_finite (by omega) (r ^ N)) hT (e.reducedExceptions_finite (by omega))
    (e.reducedDisk_subset (by omega) r) (e.reducedZeroDisk_subset_union (by omega) hr) hw
  rwa [hc] at h

theorem entireReducedDenominator_zero_counting_power {N : ℕ} (hN : 2 ≤ N) :
    ∃ K : ℝ, 0 < K ∧ ∀ r : ℝ, 0 ≤ r →
      |(analyticZeroCount (entireReducedDenominator N) (r ^ N) : ℝ) -
        (Real.sin (Real.pi / N) / Real.pi) * r| ≤ K := by
  let e := canonicalZeroEnumeration hN
  let W := finiteWeight (analyticOrderNatAt (entireReducedDenominator N)) e.reducedExceptions
  refine ⟨(W : ℝ) + e.shift + 3, by positivity, ?_⟩
  intro r hr
  have hw := e.reduced_weighted_count_bounds hN hr
  have hl : (sequenceCounting e.root r : ℝ) ≤ analyticZeroCount (entireReducedDenominator N) (r ^ N) := by
    exact_mod_cast hw.1
  have hu : (analyticZeroCount (entireReducedDenominator N) (r ^ N) : ℝ) ≤ sequenceCounting e.root r + W := by
    exact_mod_cast hw.2
  have hc := (lattice_window_counting (div_pos Real.pi_pos (signed_sine_pos hN)) e.shift e.root e.windows hr).2
  rw [abs_le] at hc ⊢
  have he : (Real.sin (Real.pi / N) / Real.pi) * r = r / (Real.pi / Real.sin (Real.pi / N)) := by field_simp
  rw [he]
  constructor <;> linarith

/-- Full reduced disk counting, including exceptional multiplicities and the N=2 boundary. -/
theorem entireReducedDenominator_zero_counting {N : ℕ} (hN : 2 ≤ N) :
    ∃ K : ℝ, 0 < K ∧ ∀ R : ℝ, 0 ≤ R →
      |(analyticZeroCount (entireReducedDenominator N) R : ℝ) -
        (Real.sin (Real.pi / N) / Real.pi) * R ^ (1 / (N : ℝ))| ≤ K := by
  obtain ⟨K, hK, hc⟩ := entireReducedDenominator_zero_counting_power hN
  refine ⟨K, hK, ?_⟩
  intro R hR
  have h := hc (R ^ (1 / (N : ℝ))) (Real.rpow_nonneg hR _)
  simpa only [one_div, Real.rpow_inv_natCast_pow hR (by omega : N ≠ 0)] using h

end
end Komorebi.PaperIV
