/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.IndicatorGeometry

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

theorem range_erase_nonempty {N : ℕ} (hN : 2 ≤ N) (k : ℕ) :
    ((Finset.range N).erase k).Nonempty := by
  by_cases hk : k = 0
  · exact ⟨1, by simp [hk]; omega⟩
  · exact ⟨0, by simp [Ne.symm hk]; omega⟩

def vertexProjectionGap (N : ℕ) (hN : 2 ≤ N) (k : ℕ) (θ : ℝ) : ℝ :=
  ((Finset.range N).erase k).inf' (range_erase_nonempty hN k)
    (fun l => signedProjection N θ k - signedProjection N θ l)

def directionSeparation (N : ℕ) (hN : 2 ≤ N) (θ : ℝ) : ℝ :=
  (Finset.range N).sup' ⟨0, Finset.mem_range.mpr (by omega)⟩
    (fun k => vertexProjectionGap N hN k θ)

theorem continuous_vertexProjectionGap (N : ℕ) (hN : 2 ≤ N) (k : ℕ) :
    Continuous (vertexProjectionGap N hN k) :=
  Continuous.finset_inf'_apply _ (fun l _ => (continuous_signedProjection N k).sub (continuous_signedProjection N l))

theorem continuous_directionSeparation (N : ℕ) (hN : 2 ≤ N) :
    Continuous (directionSeparation N hN) :=
  Continuous.finset_sup'_apply _ (fun k _ => continuous_vertexProjectionGap N hN k)

theorem directionSeparation_pos {N : ℕ} (hN : 2 ≤ N) {θ : ℝ}
    (hθ : ¬signedTieDirection N θ) : 0 < directionSeparation N hN θ := by
  obtain ⟨k, hk, he⟩ := (Finset.range N).exists_mem_eq_sup'
    ⟨0, Finset.mem_range.mpr (show 0 < N by omega)⟩ (signedProjection N θ)
  have hgap : 0 < vertexProjectionGap N hN k θ := by
    apply (Finset.lt_inf'_iff _).mpr
    intro l hl
    apply sub_pos.mpr
    apply signed_maximizer_strict_of_not_tie (show 0 < N by omega) (norm_rayDirection θ)
      (fun ht => hθ ((signedTieDirection_iff (by omega) θ).mpr ht)) (Finset.mem_range.mp hk)
      (fun j hj => (signedProjection_le_indicator (by omega) hj θ).trans_eq he)
      (Finset.mem_range.mp (Finset.mem_erase.mp hl).2) (Finset.mem_erase.mp hl).1
  exact hgap.trans_le ((Finset.range N).le_sup' (fun j => vertexProjectionGap N hN j θ) hk)

/-- Compactness provides a common strictly positive projection gap. -/
theorem compact_directions_uniform_gap {N : ℕ} (hN : 2 ≤ N) {K : Set ℝ}
    (hK : IsCompact K) (hnt : ∀ θ ∈ K, ¬signedTieDirection N θ) :
    ∃ δ : ℝ, 0 < δ ∧ ∀ θ ∈ K, ∃ k < N,
      ∀ l ∈ (Finset.range N).erase k, δ ≤ signedProjection N θ k - signedProjection N θ l := by
  by_cases hne : K.Nonempty
  · obtain ⟨θ₀, hθ₀, hmin⟩ := hK.exists_isMinOn hne (continuous_directionSeparation N hN).continuousOn
    refine ⟨directionSeparation N hN θ₀, directionSeparation_pos hN (hnt θ₀ hθ₀), ?_⟩
    intro θ hθ
    obtain ⟨k, hk, he⟩ := (Finset.range N).exists_mem_eq_sup'
      ⟨0, Finset.mem_range.mpr (show 0 < N by omega)⟩ (fun k => vertexProjectionGap N hN k θ)
    refine ⟨k, Finset.mem_range.mp hk, fun l hl => ?_⟩
    have hh : directionSeparation N hN θ₀ ≤ vertexProjectionGap N hN k θ := (hmin hθ).trans_eq he
    exact hh.trans (((Finset.range N).erase k).inf'_le _ hl)
  · exact ⟨1, by norm_num, by simp [Set.not_nonempty_iff_eq_empty.mp hne]⟩

/-- Explicit uniform error bound for the normalized denominator. -/
theorem canonicalSignedDenominator_dominant_error {N k : ℕ} (hN : 0 < N) (hk : k < N)
    {θ δ r : ℝ} (hr : 0 ≤ r)
    (hgap : ∀ l ∈ (Finset.range N).erase k, δ ≤ signedProjection N θ k - signedProjection N θ l) :
    ‖(N : ℂ) * Complex.exp (-(canonicalSignedVertex N k * ((r : ℂ) * rayDirection θ))) *
      canonicalSignedDenominator N ((r : ℂ) * rayDirection θ) - 1‖ ≤
      ((N - 1 : ℕ) : ℝ) * Real.exp (-δ * r) := by
  have he : (N : ℂ) * Complex.exp (-(canonicalSignedVertex N k * ((r : ℂ) * rayDirection θ))) *
      canonicalSignedDenominator N ((r : ℂ) * rayDirection θ) =
      Complex.exp (-(canonicalSignedVertex N k * ((r : ℂ) * rayDirection θ))) *
      ∑ l ∈ Finset.range N, Complex.exp (canonicalSignedVertex N l * ((r : ℂ) * rayDirection θ)) := by
    unfold canonicalSignedDenominator
    rw [entireSigned_zero_eq_average]
    have hn : (N : ℂ) ≠ 0 := by exact_mod_cast hN.ne'
    dsimp [canonicalSignedVertex]
    field_simp
  rw [he]
  have h := finite_exponential_dominant_bound (a := canonicalSignedVertex N) (u := rayDirection θ) (δ := δ) (Finset.mem_range.mpr hk) hr
    (fun l hl => by
      rw [sub_mul, Complex.sub_re]
      have hh := hgap l hl
      dsimp [signedProjection] at hh
      linarith)
  simpa only [Finset.card_erase_of_mem (Finset.mem_range.mpr hk), Finset.card_range] using h

/-- The uniform dominant-sector and eventual zero-free clauses of Theorem 11.4. -/
theorem canonicalSignedDenominator_compact_dominant_sectors {N : ℕ} (hN : 2 ≤ N)
    {K : Set ℝ} (hK : IsCompact K) (hnt : ∀ θ ∈ K, ¬signedTieDirection N θ) :
    ∃ δ : ℝ, 0 < δ ∧ ∃ R : ℝ, 0 < R ∧ ∀ θ ∈ K, ∃ k < N,
      ∀ r : ℝ, R ≤ r →
        ‖(N : ℂ) * Complex.exp (-(canonicalSignedVertex N k * ((r : ℂ) * rayDirection θ))) *
          canonicalSignedDenominator N ((r : ℂ) * rayDirection θ) - 1‖ ≤
          ((N - 1 : ℕ) : ℝ) * Real.exp (-δ * r) ∧
        canonicalSignedDenominator N ((r : ℂ) * rayDirection θ) ≠ 0 := by
  obtain ⟨δ, hδ, hgap⟩ := compact_directions_uniform_gap hN hK hnt
  have ht : Tendsto (fun r : ℝ => ((N - 1 : ℕ) : ℝ) * Real.exp (-δ * r)) atTop (𝓝 0) := by
    simpa only [mul_zero, Function.comp_apply, id_eq, neg_mul] using
      (Real.tendsto_exp_neg_atTop_nhds_zero.comp (tendsto_id.const_mul_atTop hδ)).const_mul ((N - 1 : ℕ) : ℝ)
  obtain ⟨R, hR⟩ := eventually_atTop.mp (ht.eventually (eventually_lt_nhds (by norm_num : (0 : ℝ) < 1)))
  refine ⟨δ, hδ, max 1 R, lt_of_lt_of_le zero_lt_one (le_max_left _ _), fun θ hθ => ?_⟩
  obtain ⟨k, hk, hkgap⟩ := hgap θ hθ
  refine ⟨k, hk, fun r hr => ?_⟩
  have hr0 : 0 ≤ r := le_trans (by norm_num) ((le_max_left _ _).trans hr)
  have hb := canonicalSignedDenominator_dominant_error (by omega) hk hr0 hkgap
  refine ⟨hb, fun hz => ?_⟩
  rw [hz, mul_zero, zero_sub, norm_neg, norm_one] at hb
  exact (not_lt_of_ge hb) (hR r ((le_max_right _ _).trans hr))

end
end Komorebi.PaperIV
