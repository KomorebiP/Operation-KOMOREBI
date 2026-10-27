import KomorebiLSM.CurvedMomentPolynomial
import Mathlib.Probability.Kernel.Composition.MapComap
import Mathlib.Tactic

/-! The observable Markov kernel is defined at every signal in [-1,1].
Its conditional moments are integrals against the actual probability kernel. -/
set_option autoImplicit false
namespace Komorebi.LSM.CurvedMoment
open MeasureTheory ProbabilityTheory
open scoped ENNReal
noncomputable section

abbrev Signal := {s : ℝ // s∈Set.Icc (-1:ℝ) 1}

def curveState (s : Signal) : ContinuousInstrument.DensityInstrument.State probabilityCone :=
  ⟨curve s,curve_mem s s.2,rfl⟩

theorem curveState_measurable : Measurable curveState := by
  apply Measurable.subtype_mk
  have hc : Continuous curve := by unfold curve; fun_prop
  exact hc.measurable.comp measurable_subtype_coe

namespace Reference
variable {μ : Measure ℝ} (R : Reference μ)
include R

def signalKernel (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ) : Kernel Signal ℝ := by
  letI := R.probability
  exact ((R.instrument a b ρ hρ hab).kernel ()).comap curveState curveState_measurable

instance signalKernel_markov (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ) :
    IsMarkovKernel (R.signalKernel a b ρ hρ hab) := by
  let := R.probability
  unfold signalKernel
  infer_instance

theorem instrument_density (a b ρ u : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ) (z : State) :
    (R.instrument a b ρ hρ hab).density () u z=likelihood a b u z := branch_mass a b u z

theorem signalKernel_apply (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ) (s : Signal) :
    R.signalKernel a b ρ hρ hab s=μ.withDensity
      (fun u => ENNReal.ofReal (1+a*s*u+b*(s:ℝ)^2*legendre u)) := by
  let := R.probability
  change (R.instrument a b ρ hρ hab).kernel () (curveState s)=_
  rw [ContinuousInstrument.DensityInstrument.kernel_apply]
  congr 1
  funext u
  rw [R.instrument_density]
  congr 1
  change 1+a*u*(s:ℝ)+b*legendre u*(s:ℝ)^2=1+a*(s:ℝ)*u+b*(s:ℝ)^2*legendre u
  ring

theorem signalKernel_support (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (s : Signal) : ∀ᵐ u∂R.signalKernel a b ρ hρ hab s,u∈Set.Icc (-1:ℝ) 1 := by
  rw [R.signalKernel_apply]
  exact (withDensity_absolutelyContinuous _ _).ae_le R.support

theorem signalKernel_continuous_integrable (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (s : Signal) {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]
    {f : ℝ→F} (hf : Continuous f) : Integrable f (R.signalKernel a b ρ hρ hab s) := by
  have he : (R.signalKernel a b ρ hρ hab s).restrict (Set.Icc (-1:ℝ) 1)=
      R.signalKernel a b ρ hρ hab s := Measure.restrict_eq_self_of_ae_mem (R.signalKernel_support a b ρ hρ hab s)
  have hi : IntegrableOn f (Set.Icc (-1:ℝ) 1) (R.signalKernel a b ρ hρ hab s) :=
    hf.continuousOn.integrableOn_compact isCompact_Icc
  simpa only [IntegrableOn,he] using hi

theorem density_lower (a b ρ u : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (hu : u∈Set.Icc (-1:ℝ) 1) (z : ContinuousInstrument.DensityInstrument.State probabilityCone) :
    ρ≤(R.instrument a b ρ hρ hab).density () u z.1 := by
  rw [R.instrument_density]
  exact likelihood_lower a b ρ u hρ hab hu (by rw [←base_eq_normalized];exact z.2)

/-- Actual conditional expectations from the declared transition law. -/
theorem signalKernel_integral (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (s : Signal) (g : ℝ→ℝ) :
    (∫ u,g u∂R.signalKernel a b ρ hρ hab s)=
      ∫ u,g u*likelihood a b u (curve s)∂μ := by
  let := R.probability
  let D := R.instrument a b ρ hρ hab
  have hd : Measurable (fun u => ENNReal.ofReal (D.density () u (curve s))) :=
    ((D.density_measurable ()).comp (measurable_const.prodMk measurable_id)).ennreal_ofReal
  change (∫ u,g u∂D.kernel () (curveState s))=_
  rw [D.kernel_apply]
  change (∫ u,g u∂μ.withDensity (fun u => ENNReal.ofReal (D.density () u (curve s))))=_
  rw [integral_withDensity_eq_integral_toReal_smul hd
    (Filter.Eventually.of_forall (fun _ => ENNReal.ofReal_lt_top))]
  apply integral_congr_ae
  filter_upwards [D.density_nonneg_ae () (curve_mem s s.2)] with u hu
  rw [ENNReal.toReal_ofReal hu]
  change (R.instrument a b ρ hρ hab).density () u (curve s)*g u=g u*likelihood a b u (curve s)
  rw [R.instrument_density]
  ring

theorem conditional_signal_mean (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (s : Signal) : (∫ u,u∂R.signalKernel a b ρ hρ hab s)=a/3*s := by
  rw [R.signalKernel_integral,R.integral_signal_likelihood]
  simp [curve]
  ring

theorem conditional_legendre_mean (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (s : Signal) : (∫ u,legendre u∂R.signalKernel a b ρ hρ hab s)=b/5*(s:ℝ)^2 := by
  rw [R.signalKernel_integral,R.integral_legendre_likelihood]
  simp [curve]
  ring

theorem update_curve_ae (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (fallback z : ContinuousInstrument.DensityInstrument.State probabilityCone) :
    ∀ᵐ u∂μ,0<likelihood a b u z.1 →
      ((R.instrument a b ρ hρ hab).update fallback () z u).1=curve u := by
  let D := R.instrument a b ρ hρ hab
  filter_upwards [D.update_eq_ae fallback () z] with u hu hp
  have hdp : 0<D.density () u z.1 := by
    change 0<(R.instrument a b ρ hρ hab).density () u z.1
    rwa [R.instrument_density]
  change (D.update fallback () z u).1=_
  rw [hu hdp]
  change (mass (branch a b u z.1))⁻¹ • branch a b u z.1=_
  exact posterior_curve a b u z.1 hp

/-- Every branch with positive probability resets to the observed moment ray;
zero-density branches contribute no mass to this almost-everywhere statement. -/
theorem update_curve_kernel_ae [IsProbabilityMeasure μ] (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (fallback z : ContinuousInstrument.DensityInstrument.State probabilityCone) :
    ∀ᵐ u∂(R.instrument a b ρ hρ hab).kernel () z,
      ((R.instrument a b ρ hρ hab).update fallback () z u).1=curve u := by
  let := R.probability
  let D := R.instrument a b ρ hρ hab
  have hd : Measurable (fun u => ENNReal.ofReal (D.density () u z.1)) :=
    ((D.density_measurable ()).comp (measurable_const.prodMk measurable_id)).ennreal_ofReal
  rw [D.kernel_apply,ae_withDensity_iff hd]
  filter_upwards [R.update_curve_ae a b ρ hρ hab fallback z] with u hu hn
  apply hu
  have hp : 0<D.density () u z.1 := ENNReal.ofReal_ne_zero_iff.mp hn
  rwa [R.instrument_density] at hp

/-- The next transition is the globally specified observable signal kernel,
including for a prior signal whose history has probability zero. -/
theorem observable_markov_transition [IsProbabilityMeasure μ] (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (fallback z : ContinuousInstrument.DensityInstrument.State probabilityCone) :
    ∀ᵐ u∂(R.instrument a b ρ hρ hab).kernel () z,
      ∃ hu : u∈Set.Icc (-1:ℝ) 1,
        (R.instrument a b ρ hρ hab).kernel ()
          ((R.instrument a b ρ hρ hab).update fallback () z u)=R.signalKernel a b ρ hρ hab ⟨u,hu⟩ := by
  let := R.probability
  let D := R.instrument a b ρ hρ hab
  have hs : ∀ᵐ u∂D.kernel () z,u∈Set.Icc (-1:ℝ) 1 := by
    rw [D.kernel_apply]
    exact (withDensity_absolutelyContinuous _ _).ae_le R.support
  filter_upwards [R.update_curve_kernel_ae a b ρ hρ hab fallback z,hs] with u hu hs
  refine ⟨hs,?_⟩
  change D.kernel () (D.update fallback () z u)=D.kernel () (curveState ⟨u,hs⟩)
  congr 1
  exact Subtype.ext hu

/-- The exact same operator density defines normalized laws at every finite horizon. -/
theorem record_probability (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ)
    (π : ContinuousRecords.Policy (A:=Unit) (Y:=ℝ))
    (z : ContinuousInstrument.DensityInstrument.State probabilityCone) (n : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.recordLaw (R.instrument a b ρ hρ hab) π z.1 n) := by
  let := R.probability
  exact ContinuousRecords.recordLaw_probability _ π z n

end Reference
end
end Komorebi.LSM.CurvedMoment
