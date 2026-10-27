import KomorebiLSM.ScalarRegressionConfidence
import KomorebiLSM.BoundedResponseNoise
import KomorebiLSM.OutwardConfidenceIntervals

/-! P84: actual scalar regression events are retained through exact outer
radius construction, outward endpoint rounding and intersection with the prior. -/
set_option autoImplicit false
namespace Komorebi.LSM.RationalRegressionConfidence
open MeasureTheory RegressionConfidence
open OutwardConfidenceIntervals
open scoped BigOperators
variable {Ω : Type*} [mΩ : MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]

noncomputable def variance (x : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) : ℝ :=
  scalarV (fun i => x i ω) n
noncomputable def estimate (x y : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) : ℝ :=
  scalarEstimate (fun i => x i ω) (fun i => y i ω) n
noncomputable def radius (denominator : ℕ) (sigma : ℚ) (delta : ℝ)
    (x : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) : ℚ :=
  RationalConfidenceArithmetic.outerRadius denominator sigma (variance x n ω) delta
noncomputable def lower (radiusGrid endpointGrid : ℕ) (sigma : ℚ) (delta : ℝ)
    (x y : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) : ℚ :=
  lowerEndpoint endpointGrid (estimate x y n ω) (radius radiusGrid sigma delta x n ω)
noncomputable def upper (radiusGrid endpointGrid : ℕ) (sigma : ℚ) (delta : ℝ)
    (x y : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) : ℚ :=
  upperEndpoint endpointGrid (estimate x y n ω) (radius radiusGrid sigma delta x n ω)

/-- The scalar covariance and ridge estimate are the actual P81 objects;
the returned event is its actual Gaussian-mixture no-crossing event. -/
theorem scalar_outer_certificate (F : Filtration ℕ mΩ)
    (radiusGrid endpointGrid : ℕ) (hr : 0<radiusGrid) (he : 0<endpointGrid)
    (sigma : ℚ) (hs : 0<sigma) (delta : ℝ) (hd : 0<delta) (hd1 : delta≤1)
    (x y : ℕ → Ω → ℝ) (theta : ℝ)
    (hx : ∀ n,Measurable[F n] (x n)) (hy : ∀ n,Measurable[F (n+1)] (y n)) (htheta : |theta|≤1)
    (H : ∀ n,ConditionalSubgaussian (F.le n) (fun ω => y n ω-theta*x n ω) sigma μ) :
    MeasurableSet (scalarGood sigma delta x y theta) ∧
    1-delta≤μ.real (scalarGood sigma delta x y theta) ∧
    ∀ ω∈scalarGood sigma delta x y theta,∀ n,
      theta∈Set.Icc (lower radiusGrid endpointGrid sigma delta x y n ω : ℝ)
        (upper radiusGrid endpointGrid sigma delta x y n ω : ℝ) := by
  have hsr : (0 : ℝ)<sigma := by exact_mod_cast hs
  have hc := scalar_regression_confidence_certificate F sigma delta hsr hd hd1 x y theta hx hy htheta H
  refine ⟨hc.1,hc.2.1,?_⟩
  intro ω hω n
  have herr := hc.2.2 ω hω n
  have hbound := RationalConfidenceArithmetic.scalarRadius_le_outer radiusGrid hr sigma hs.le
    (variance x n ω) delta (scalarV_ge_one _ _) hd hd1
  change |estimate x y n ω-theta|≤
    RationalConfidenceArithmetic.scalarRadius sigma (variance x n ω) delta at herr
  exact contains_true endpointGrid he _ theta _ _ herr hbound htheta

theorem two_good_coverage (A B : Set Ω) (hA : MeasurableSet A) (hB : MeasurableSet B)
    (hpA : 1-(1/40 : ℝ)≤μ.real A) (hpB : 1-(1/40 : ℝ)≤μ.real B) :
    (19/20 : ℝ)≤μ.real (A∩B) := by
  have ha := measureReal_add_measureReal_compl (μ := μ) hA
  have hb := measureReal_add_measureReal_compl (μ := μ) hB
  have hg := measureReal_add_measureReal_compl (μ := μ) (hA.inter hB)
  simp only [probReal_univ] at ha hb hg
  have hu := measureReal_union_le (μ := μ) Aᶜ Bᶜ
  rw [← Set.compl_inter] at hu
  linarith

/-- No independence between response coordinates is required for their
simultaneous all-time coverage. The two exact source noise scales are derived. -/
theorem two_regression_outer_certificate (F : Filtration ℕ mΩ)
    (endpointGrid : ℕ) (he : 0<endpointGrid)
    (xA yA xB yB : ℕ → Ω → ℝ) (thetaA thetaB : ℝ)
    (hxA : ∀ n,Measurable[F n] (xA n)) (hyA : ∀ n,Measurable[F (n+1)] (yA n))
    (hxB : ∀ n,Measurable[F n] (xB n)) (hyB : ∀ n,Measurable[F (n+1)] (yB n))
    (hbA : ∀ n,∀ᵐ ω∂μ,yA n ω∈Set.Icc (-1 : ℝ) 1)
    (hbB : ∀ n,∀ᵐ ω∂μ,yB n ω∈Set.Icc (-(1/2) : ℝ) 1)
    (hmA : ∀ n,(μ[yA n|F n])=ᵐ[μ] (fun ω => thetaA*xA n ω))
    (hmB : ∀ n,(μ[yB n|F n])=ᵐ[μ] (fun ω => thetaB*xB n ω))
    (htA : |thetaA|≤1) (htB : |thetaB|≤1) :
    let G := scalarGood 1 (1/40) xA yA thetaA∩scalarGood (3/4) (1/40) xB yB thetaB
    MeasurableSet G ∧ (19/20 : ℝ)≤μ.real G ∧ ∀ ω∈G,∀ n,
      thetaA∈Set.Icc (lower (10^12) endpointGrid 1 (1/40) xA yA n ω : ℝ)
        (upper (10^12) endpointGrid 1 (1/40) xA yA n ω : ℝ) ∧
      thetaB∈Set.Icc (lower (10^12) endpointGrid (3/4) (1/40) xB yB n ω : ℝ)
        (upper (10^12) endpointGrid (3/4) (1/40) xB yB n ω : ℝ) := by
  have hA := scalar_outer_certificate F (10^12) endpointGrid (by norm_num) he 1 (by norm_num)
    (1/40) (by norm_num) (by norm_num) xA yA thetaA hxA hyA htA
    (by simpa only [Rat.cast_one] using
      BoundedResponseNoise.process_neg_one_one F thetaA xA yA hxA hyA hbA hmA)
  have hB := scalar_outer_certificate F (10^12) endpointGrid (by norm_num) he (3/4) (by norm_num)
    (1/40) (by norm_num) (by norm_num) xB yB thetaB hxB hyB htB
    (by simpa only [Rat.cast_div,Rat.cast_ofNat] using
      BoundedResponseNoise.process_neg_half_one F thetaB xB yB hxB hyB hbB hmB)
  simp only [Rat.cast_one,Rat.cast_div,Rat.cast_ofNat] at hA hB
  exact ⟨hA.1.inter hB.1,two_good_coverage _ _ hA.1 hB.1 hA.2.1 hB.2.1,
    fun ω hω n => ⟨hA.2.2 ω hω.1 n,hB.2.2 ω hω.2 n⟩⟩

end Komorebi.LSM.RationalRegressionConfidence
