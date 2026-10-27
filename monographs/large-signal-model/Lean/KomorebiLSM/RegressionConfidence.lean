import KomorebiLSM.RegressionGaussian
import KomorebiLSM.RegressionRadius
import KomorebiLSM.RegressionExponential
import KomorebiLSM.VilleInequality

/-! P81: the actual ridge estimator is covered at every finite time by a
measurable event derived from the actual Gaussian-mixture supermartingale. -/
set_option autoImplicit false
namespace Komorebi.LSM.RegressionConfidence
open MeasureTheory ProbabilityTheory Matrix
open scoped BigOperators ENNReal ComplexOrder
variable {I Ω : Type*} [Fintype I] [DecidableEq I] [mΩ : MeasurableSpace Ω]
variable {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- The noise is the literal deviation from the declared linear conditional mean. -/
noncomputable def regressionNoise (θ : I → ℝ) (φ : ℕ → Ω → I → ℝ)
    (y : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) : ℝ := y n ω-θ ⬝ᵥ φ n ω

/-- The explicit measurable event used for the time-uniform confidence guarantee. -/
noncomputable def regressionGood (γ σ δ : ℝ) (φ : ℕ → Ω → I → ℝ)
    (y : ℕ → Ω → ℝ) (θ : I → ℝ) : Set Ω :=
  (VilleInequality.crossing
    (exponentialMixture σ φ (regressionNoise θ φ y) (gaussianPrior γ)) (1/δ))ᶜ

omit [DecidableEq I] [IsProbabilityMeasure μ] in
theorem regressionNoise_measurable (ℱ : Filtration ℕ mΩ)
    (θ : I → ℝ) (φ : ℕ → Ω → I → ℝ) (y : ℕ → Ω → ℝ)
    (hφ : ∀ n i,Measurable[ℱ n] (fun ω => φ n ω i))
    (hy : ∀ n,Measurable[ℱ (n+1)] (y n)) (n : ℕ) :
    Measurable[ℱ (n+1)] (regressionNoise θ φ y n) := by
  unfold regressionNoise dotProduct
  exact (hy n).sub (Finset.measurable_sum _ (fun i _ => measurable_const.mul
    ((hφ n i).mono (ℱ.mono (by omega)) le_rfl)))

omit mΩ [IsProbabilityMeasure μ] in
/-- Every sample in the explicit good event has the source's exact ridge
confidence radius at every finite horizon. -/
theorem regressionGood_error_bound (γ σ δ S : ℝ) (hγ : 0 < γ) (hσ : 0 < σ)
    (hδ : 0 < δ) (φ : ℕ → Ω → I → ℝ) (y : ℕ → Ω → ℝ) (θ : I → ℝ)
    (hθ : euclideanNorm θ ≤ S) (ω : Ω) (hgood : ω∈regressionGood γ σ δ φ y θ) (n : ℕ) :
    weightedNorm (ridgeMatrix γ (fun i => φ i ω) n)
      (ridgeEstimate γ (fun i => φ i ω) (fun i => y i ω) n-θ) ≤
      noiseRadius γ σ δ (fun i => φ i ω) n+Real.sqrt γ*S := by
  have hn : exponentialMixture σ φ (regressionNoise θ φ y) (gaussianPrior γ) n ω<1/δ := by
    apply lt_of_not_ge
    intro hc
    exact hgood ⟨n,hc⟩
  rw [exponentialMixture_eq σ φ (regressionNoise θ φ y) (ne_of_gt hσ),
    gaussian_ridge_mixture γ σ hγ hσ] at hn
  have hV := ridgeMatrix_posDef γ hγ (fun i => φ i ω) n
  have hW : (γ • (1 : Matrix I I ℝ)).PosDef := Matrix.PosDef.one.smul hγ
  have hnoise := mixture_lt_implies_noise_bound _ _ hV hW σ δ hσ hδ _ hn
  apply (ridge_error_le γ hγ (fun i => φ i ω) (fun i => y i ω)
    (fun i => regressionNoise θ φ y i ω) θ n (fun i _ => by
      unfold regressionNoise
      ring)).trans
  exact add_le_add hnoise (mul_le_mul_of_nonneg_left hθ (Real.sqrt_nonneg γ))

/-- Full P81. No design boundedness or excitation condition is added. The
noise hypothesis is the actual conditional exponential inequality, and the
mixture, its probability normalization and its crossing control are derived. -/
theorem regression_confidence_certificate (ℱ : Filtration ℕ mΩ)
    (γ σ δ S : ℝ) (hγ : 0 < γ) (hσ : 0 < σ) (hδ : 0 < δ)
    (φ : ℕ → Ω → I → ℝ) (y : ℕ → Ω → ℝ) (θ : I → ℝ)
    (hφ : ∀ n i,Measurable[ℱ n] (fun ω => φ n ω i))
    (hy : ∀ n,Measurable[ℱ (n+1)] (y n)) (hθ : euclideanNorm θ ≤ S)
    (H : ∀ n,ConditionalSubgaussian (ℱ.le n) (regressionNoise θ φ y n) σ μ) :
    MeasurableSet (regressionGood γ σ δ φ y θ) ∧
    1-δ≤μ.real (regressionGood γ σ δ φ y θ) ∧
    ∀ ω∈regressionGood γ σ δ φ y θ,∀ n,
      weightedNorm (ridgeMatrix γ (fun i => φ i ω) n)
        (ridgeEstimate γ (fun i => φ i ω) (fun i => y i ω) n-θ) ≤
        noiseRadius γ σ δ (fun i => φ i ω) n+Real.sqrt γ*S := by
  let : IsProbabilityMeasure (gaussianPrior (I := I) γ) := gaussianPrior_probability γ hγ
  let M := exponentialMixture σ φ (regressionNoise θ φ y) (gaussianPrior γ)
  have hM : Supermartingale M ℱ μ := exponentialMixture_supermartingale ℱ σ φ
    (regressionNoise θ φ y) hφ (regressionNoise_measurable ℱ θ φ y hφ hy) H (gaussianPrior γ)
  have hm := VilleInequality.crossing_measurable μ ℱ M hM (1/δ)
  have hi : (∫ ω,M 0 ω∂μ)≤1 := by simp [M]
  have hb := VilleInequality.crossing_bound μ ℱ M hM
    (exponentialMixture_nonneg σ φ (regressionNoise θ φ y) (gaussianPrior γ)) hi (1/δ)
      (one_div_pos.2 hδ)
  simp only [one_div_one_div] at hb
  have hbr : μ.real (VilleInequality.crossing M (1/δ))≤δ := by
    have h := ENNReal.toReal_mono ENNReal.ofReal_ne_top hb
    simpa only [Measure.real,ENNReal.toReal_ofReal hδ.le] using h
  refine ⟨hm.compl,?_,?_⟩
  · change 1-δ≤μ.real ((VilleInequality.crossing M (1/δ))ᶜ)
    rw [measureReal_compl hm]
    simpa using sub_le_sub_left hbr 1
  · exact fun ω hω n => regressionGood_error_bound γ σ δ S hγ hσ hδ φ y θ hθ ω hω n

end Komorebi.LSM.RegressionConfidence
