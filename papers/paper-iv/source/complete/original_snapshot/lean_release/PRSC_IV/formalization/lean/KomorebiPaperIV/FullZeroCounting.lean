/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroEnumeration

namespace Komorebi.PaperIV
noncomputable section
open Set Metric

def SignedZeroEnumeration.orbitDisk {N : ℕ} (e : SignedZeroEnumeration N) (R : ℝ) : Set ℂ :=
  e.orbit '' (univ ×ˢ {m | e.root m ≤ R})

def SignedZeroEnumeration.exceptions {N : ℕ} (e : SignedZeroEnumeration N) : Set ℂ :=
  zeroDisk (canonicalSignedDenominator N) e.radius \ range e.orbit

theorem SignedZeroEnumeration.exceptions_finite {N : ℕ} (hN : 0 < N) (e : SignedZeroEnumeration N) :
    e.exceptions.Finite := (canonicalSignedDenominator_zeroDisk_finite hN e.radius).sdiff

theorem SignedZeroEnumeration.orbitDisk_finite_card {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) {R : ℝ} (hR : 0 ≤ R) :
    (e.orbitDisk R).Finite ∧ (e.orbitDisk R).ncard = N * sequenceCounting e.root R := by
  have hf := (lattice_window_counting (div_pos Real.pi_pos (signed_sine_pos hN)) e.shift e.root e.windows hR).1
  refine ⟨(finite_univ.prod hf).image e.orbit, ?_⟩
  rw [SignedZeroEnumeration.orbitDisk, ncard_image_of_injective _ (e.orbit_injective (by omega)), ncard_prod]
  simp [sequenceCounting]

theorem SignedZeroEnumeration.orbitDisk_subset {N : ℕ} (hN : 0 < N)
    (e : SignedZeroEnumeration N) (R : ℝ) :
    e.orbitDisk R ⊆ zeroDisk (canonicalSignedDenominator N) R := by
  rintro z ⟨p, hp, rfl⟩
  exact ⟨(e.orbit_norm hN p).trans_le hp.2, (e.orbit_zero_simple hN p).1⟩

theorem SignedZeroEnumeration.zeroDisk_subset_union {N : ℕ} (hN : 0 < N)
    (e : SignedZeroEnumeration N) (R : ℝ) :
    zeroDisk (canonicalSignedDenominator N) R ⊆ e.orbitDisk R ∪ e.exceptions := by
  classical
  intro z hz
  by_cases hr : z ∈ range e.orbit
  · obtain ⟨p, rfl⟩ := hr
    apply Or.inl
    exact ⟨p, ⟨mem_univ _, by change e.root p.2 ≤ R; rw [← e.orbit_norm hN p]; exact hz.1⟩, rfl⟩
  · apply Or.inr
    refine ⟨⟨?_, hz.2⟩, hr⟩
    by_contra hb
    obtain ⟨k, m, he⟩ := e.exhaustive z (le_of_lt (lt_of_not_ge hb)) hz.2
    exact hr ⟨(k, m), he.symm⟩

theorem SignedZeroEnumeration.weighted_count_bounds {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) {R : ℝ} (hR : 0 ≤ R) :
    N * sequenceCounting e.root R ≤ analyticZeroCount (canonicalSignedDenominator N) R ∧
      analyticZeroCount (canonicalSignedDenominator N) R ≤ N * sequenceCounting e.root R +
        finiteWeight (analyticOrderNatAt (canonicalSignedDenominator N)) e.exceptions := by
  obtain ⟨hT, hc⟩ := e.orbitDisk_finite_card hN hR
  have hw : ∀ z ∈ e.orbitDisk R, analyticOrderNatAt (canonicalSignedDenominator N) z = 1 := by
    rintro _ ⟨p, _, rfl⟩
    exact (e.orbit_zero_simple (by omega) p).2
  have h := finiteWeight_between_tail_and_exceptions (analyticOrderNatAt (canonicalSignedDenominator N))
    (canonicalSignedDenominator_zeroDisk_finite (by omega) R) hT (e.exceptions_finite (by omega))
    (e.orbitDisk_subset (by omega) R) (e.zeroDisk_subset_union (by omega) R) hw
  rwa [hc] at h

/-- The full denominator disk count, including every exceptional multiplicity. -/
theorem canonicalSignedDenominator_zero_counting {N : ℕ} (hN : 2 ≤ N) :
    ∃ K : ℝ, 0 < K ∧ ∀ R : ℝ, 0 ≤ R →
      |(analyticZeroCount (canonicalSignedDenominator N) R : ℝ) -
        ((N : ℝ) * Real.sin (Real.pi / N) / Real.pi) * R| ≤ K := by
  let e := canonicalZeroEnumeration hN
  let W := finiteWeight (analyticOrderNatAt (canonicalSignedDenominator N)) e.exceptions
  refine ⟨(W : ℝ) + N * ((e.shift : ℝ) + 2) + 1, by positivity, ?_⟩
  intro R hR
  have hw := e.weighted_count_bounds hN hR
  have hl : (N : ℝ) * sequenceCounting e.root R ≤ analyticZeroCount (canonicalSignedDenominator N) R := by
    exact_mod_cast hw.1
  have hu : (analyticZeroCount (canonicalSignedDenominator N) R : ℝ) ≤
      N * sequenceCounting e.root R + W := by exact_mod_cast hw.2
  have hc := (lattice_window_counting (div_pos Real.pi_pos (signed_sine_pos hN))
    e.shift e.root e.windows hR).2
  rw [abs_le] at hc ⊢
  have he : ((N : ℝ) * Real.sin (Real.pi / N) / Real.pi) * R =
      N * (R / (Real.pi / Real.sin (Real.pi / N))) := by field_simp
  rw [he]
  have hn := Nat.cast_nonneg (α := ℝ) N
  constructor <;> nlinarith

end
end Komorebi.PaperIV
