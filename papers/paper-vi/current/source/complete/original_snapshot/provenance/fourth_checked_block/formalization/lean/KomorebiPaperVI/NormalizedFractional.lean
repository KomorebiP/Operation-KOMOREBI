import KomorebiPaperVI.BetaNormalization
import KomorebiPaperVI.FractionalIntegral
import Mathlib.Analysis.CStarAlgebra.ContinuousFunctionalCalculus.Basic

/-!
Author: Komorebi P.
The CFC integration argument adapts Mathlib's Rpow/IntegralRepresentation.lean,
Copyright (c) 2025 Frédéric Dupuis, Apache 2.0. Its explicit measure is retained here.
-/
set_option backward.isDefEq.respectTransparency false
namespace KomorebiPaperVI.NormalizedFractional
open Set MeasureTheory Real
open scoped NNReal ENNReal
attribute [local instance] IsStarNormal.instContinuousFunctionalCalculus
variable {A : Type*} [CStarAlgebra A] [PartialOrder A] [StarOrderedRing A]

noncomputable def coefficient (p : ℝ) : ℝ := Real.sin (Real.pi*p)/Real.pi

theorem scalar_measure (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1) :
    let c : ℝ≥0 := ⟨coefficient p,(by exact (BetaNormalization.sine_factor_positive p hp).le)⟩
    ∀ x ∈ Ici (0:ℝ), IntegrableOn (fun t => rpowIntegrand₀₁ p t x) (Ioi 0) (c • volume) ∧
      x^(p:ℝ)=∫ t in Ioi 0,rpowIntegrand₀₁ p t x ∂(c • volume) := by
  dsimp only
  intro x hx
  constructor
  · unfold IntegrableOn
    rw [Measure.restrict_smul]
    exact Integrable.smul_measure_nnreal (integrableOn_rpowIntegrand₀₁_Ioi hp hx)
  · simp only [Measure.restrict_smul,integral_smul_nnreal_measure,NNReal.smul_def,smul_eq_mul]
    exact BetaNormalization.scalar_fractional_integral p x hp hx

theorem cfc_explicit_measure (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1) (a : A) (ha : 0 ≤ a) :
    let c : ℝ≥0 := ⟨coefficient p,(by exact (BetaNormalization.sine_factor_positive p hp).le)⟩
    IntegrableOn (fun t => cfcₙ (rpowIntegrand₀₁ p t) a) (Ioi 0) (c • volume) ∧
      CFC.nnrpow a p=∫ t in Ioi 0,cfcₙ (rpowIntegrand₀₁ p t) a ∂(c • volume) := by
  let c : ℝ≥0 := ⟨coefficient p,(by exact (BetaNormalization.sine_factor_positive p hp).le)⟩
  let μ : Measure ℝ := c • volume
  have hμ := scalar_measure p hp
  change IntegrableOn _ _ μ ∧ _
  nontriviality A
  have p_pos : 0 < (p : ℝ) := by exact_mod_cast hp.1
  let f t := rpowIntegrand₀₁ p t
  let maxr := sSup (quasispectrum ℝ a)
  have maxr_nonneg : 0 ≤ maxr :=
    le_csSup_of_le (b := 0) (IsCompact.bddAbove (by grind)) (by simp) (by simp)
  let bound (t : ℝ) := ‖f t maxr‖
  have hf : ContinuousOn (Function.uncurry f) (Ioi (0 : ℝ) ×ˢ quasispectrum ℝ a) := by
    refine continuousOn_rpowIntegrand₀₁_uncurry hp (quasispectrum ℝ a) ?_
    grind
  have hbound : ∀ᵐ t ∂μ.restrict (Ioi 0), ∀ z ∈ quasispectrum ℝ a, ‖f t z‖ ≤ bound t := by
    filter_upwards [ae_restrict_mem measurableSet_Ioi] with t ht
    intro z hz
    have hz' : 0 ≤ z := by grind
    unfold bound f
    rw [Real.norm_of_nonneg (rpowIntegrand₀₁_nonneg p_pos (le_of_lt ht) hz'),
        Real.norm_of_nonneg (rpowIntegrand₀₁_nonneg p_pos (le_of_lt ht) maxr_nonneg)]
    refine rpowIntegrand₀₁_monotoneOn hp (le_of_lt ht) hz' maxr_nonneg ?_
    exact le_csSup (IsCompact.bddAbove (quasispectrum.isCompact _)) hz
  have hbound_finite_integral : HasFiniteIntegral bound (μ.restrict (Ioi 0)) := by
    rw [hasFiniteIntegral_norm_iff]
    exact (hμ maxr maxr_nonneg).1.2
  have hmapzero : ∀ᵐ (x : ℝ) ∂μ.restrict (Ioi 0), rpowIntegrand₀₁ p x 0 = 0 := by
    filter_upwards [ae_restrict_mem measurableSet_Ioi]
    simp
  refine ⟨?integrable, ?integral⟩
  case integrable =>
    exact integrableOn_cfcₙ measurableSet_Ioi _ bound a hf hmapzero hbound hbound_finite_integral
  case integral => calc
    a ^ p = cfcₙ (fun r => ∫ t in Ioi 0, rpowIntegrand₀₁ p t r ∂μ) a := by
      rw [CFC.nnrpow_eq_cfcₙ_real _ _]
      exact cfcₙ_congr fun r _ ↦ (hμ r (by grind)).2
    _ = _ := cfcₙ_setIntegral measurableSet_Ioi _ bound a hf hmapzero hbound
                hbound_finite_integral ha.isSelfAdjoint

theorem cfc_lebesgue_integral (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1) (a : A) (ha : 0 ≤ a) :
    IntegrableOn (fun t => cfcₙ (rpowIntegrand₀₁ p t) a) (Ioi 0) ∧
      CFC.nnrpow a p=coefficient p • ∫ t in Ioi 0,cfcₙ (rpowIntegrand₀₁ p t) a := by
  let c : ℝ≥0 := ⟨coefficient p,by exact (BetaNormalization.sine_factor_positive p hp).le⟩
  have h := cfc_explicit_measure p hp a ha
  change IntegrableOn _ _ (c • volume) ∧ _ at h
  have hc0 : (c:ℝ≥0∞) ≠ 0 := by
    have hc : c ≠ 0 := by
      apply NNReal.coe_ne_zero.mp
      exact (BetaNormalization.sine_factor_positive p hp).ne'
    exact_mod_cast hc
  constructor
  · have hi := h.1
    unfold IntegrableOn at hi ⊢
    rw [Measure.restrict_smul] at hi
    exact (integrable_smul_measure hc0 (by simp)).mp hi
  · have he := h.2
    simp only [Measure.restrict_smul,integral_smul_nnreal_measure,NNReal.smul_def] at he
    convert! he using 1

end KomorebiPaperVI.NormalizedFractional
