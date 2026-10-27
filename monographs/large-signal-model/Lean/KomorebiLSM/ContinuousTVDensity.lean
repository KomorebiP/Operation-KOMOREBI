import KomorebiLSM.SequentialLowerCertificate
import Mathlib.MeasureTheory.VectorMeasure.WithDensityVec

/-! Exact probability-convention total variation for actual measures with a
common reference density. The half-integral identity is derived through the
variation of the genuine signed-measure difference. -/
set_option autoImplicit false
namespace Komorebi.LSM.ContinuousTVDensity
open MeasureTheory
open scoped ENNReal

variable {Ω : Type*} [MeasurableSpace Ω]

/-- An actual nonnegative integrable density has its expected signed measure. -/
theorem toSignedMeasure_withDensity_real (ν : Measure Ω) (f : Ω → ℝ)
    [IsFiniteMeasure (ν.withDensity (fun x => ENNReal.ofReal (f x)))]
    (hf : Integrable f ν) (hf0 : 0 ≤ᵐ[ν] f) :
    (ν.withDensity (fun x => ENNReal.ofReal (f x))).toSignedMeasure=ν.withDensityᵥ f := by
  have hfin : (∫⁻ x, ENNReal.ofReal (f x) ∂ν) ≠ ⊤ :=
    ((hasFiniteIntegral_iff_ofReal hf0).mp hf.hasFiniteIntegral).ne
  have hreal := withDensityᵥ_toReal hf.aestronglyMeasurable.aemeasurable.ennreal_ofReal hfin
  refine hreal.symm.trans (WithDensityᵥEq.congr_ae ?_)
  filter_upwards [hf0] with x hx
  exact ENNReal.toReal_ofReal hx

/-- The exact half absolute-integral formula for actual real density laws. -/
theorem lawTV_withDensity_real (ν : Measure Ω) (f g : Ω → ℝ)
    [IsProbabilityMeasure (ν.withDensity (fun x => ENNReal.ofReal (f x)))]
    [IsProbabilityMeasure (ν.withDensity (fun x => ENNReal.ofReal (g x)))]
    (hf : Integrable f ν) (hg : Integrable g ν)
    (hf0 : 0 ≤ᵐ[ν] f) (hg0 : 0 ≤ᵐ[ν] g) :
    SequentialLowerCertificate.lawTV
      (ν.withDensity (fun x => ENNReal.ofReal (f x)))
      (ν.withDensity (fun x => ENNReal.ofReal (g x)))=
      (1/2:ℝ) * ∫ x, |f x-g x| ∂ν := by
  have hdiff : Integrable (fun x => f x-g x) ν := (hf.sub hg).congr (by filter_upwards with x; rfl)
  rw [SequentialLowerCertificate.lawTV,toSignedMeasure_withDensity_real ν f hf hf0,
    toSignedMeasure_withDensity_real ν g hg hg0,← withDensityᵥ_sub' hf hg,
    SignedMeasure.totalVariation_eq_variation,Measure.variation_withDensityᵥ hdiff,
    Measure.real,withDensity_apply _ MeasurableSet.univ,Measure.restrict_univ,
    ← integral_norm_eq_lintegral_enorm hdiff.aestronglyMeasurable]
  simp only [Real.norm_eq_abs]

/-- A probability density has finite reference integral, even when the common
reference measure itself is infinite. -/
theorem density_lintegral_finite (ν : Measure Ω) (f : Ω → ℝ≥0∞)
    [IsProbabilityMeasure (ν.withDensity f)] : (∫⁻ x, f x ∂ν) ≠ ⊤ := by
  have he : (∫⁻ x, f x ∂ν)=1 := by
    rw [← Measure.restrict_univ (μ := ν),← withDensity_apply _ MeasurableSet.univ]
    exact measure_univ
  rw [he]
  exact ENNReal.one_ne_top

/-- No real-density integrability premise is needed: finite probability laws
derive it from the measurable ENNReal densities. -/
theorem lawTV_withDensity_lintegral (ν : Measure Ω) (f g : Ω → ℝ≥0∞)
    [IsProbabilityMeasure (ν.withDensity f)] [IsProbabilityMeasure (ν.withDensity g)]
    (hf : AEMeasurable f ν) (hg : AEMeasurable g ν) :
    SequentialLowerCertificate.lawTV (ν.withDensity f) (ν.withDensity g)=
      (1/2:ℝ) * (∫⁻ x, ENNReal.ofReal |(f x).toReal-(g x).toReal| ∂ν).toReal := by
  have hfi := density_lintegral_finite ν f
  have hgi := density_lintegral_finite ν g
  have hfr := integrable_toReal_of_lintegral_ne_top hf hfi
  have hgr := integrable_toReal_of_lintegral_ne_top hg hgi
  have hdiff : Integrable (fun x => (f x).toReal-(g x).toReal) ν := (hfr.sub hgr).congr (by filter_upwards with x; rfl)
  rw [SequentialLowerCertificate.lawTV,← withDensityᵥ_toReal hf hfi,
    ← withDensityᵥ_toReal hg hgi,← withDensityᵥ_sub' hfr hgr,
    SignedMeasure.totalVariation_eq_variation,Measure.variation_withDensityᵥ hdiff,
    Measure.real,withDensity_apply _ MeasurableSet.univ,Measure.restrict_univ]
  simp only [Real.enorm_eq_ofReal_abs]

/-- The ENNReal half-integral identity can be compared directly with a
nonnegative reference-integral error budget. -/
theorem ofReal_lawTV_withDensity_lintegral (ν : Measure Ω) (f g : Ω → ℝ≥0∞)
    [IsProbabilityMeasure (ν.withDensity f)] [IsProbabilityMeasure (ν.withDensity g)]
    (hf : AEMeasurable f ν) (hg : AEMeasurable g ν) :
    ENNReal.ofReal (SequentialLowerCertificate.lawTV (ν.withDensity f) (ν.withDensity g))=
      (1/2:ℝ≥0∞) * ∫⁻ x, ENNReal.ofReal |(f x).toReal-(g x).toReal| ∂ν := by
  have hfr := integrable_toReal_of_lintegral_ne_top hf (density_lintegral_finite ν f)
  have hgr := integrable_toReal_of_lintegral_ne_top hg (density_lintegral_finite ν g)
  have hdiff : Integrable (fun x => (f x).toReal-(g x).toReal) ν := (hfr.sub hgr).congr (by filter_upwards with x; rfl)
  have hfin : (∫⁻ x, ENNReal.ofReal |(f x).toReal-(g x).toReal| ∂ν) ≠ ⊤ := by
    simpa only [← Real.enorm_eq_ofReal_abs] using hdiff.hasFiniteIntegral.ne
  rw [lawTV_withDensity_lintegral ν f g hf hg,ENNReal.ofReal_mul (by norm_num : (0:ℝ)≤1/2),
    ENNReal.ofReal_toReal hfin,ENNReal.ofReal_div_of_pos (by norm_num : (0:ℝ)<2)]
  norm_num

end Komorebi.LSM.ContinuousTVDensity
