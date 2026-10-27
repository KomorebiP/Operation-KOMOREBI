import KomorebiLSM.CurvedMomentMarkov
import KomorebiLSM.ContinuousTVDensity
import KomorebiLSM.KernelTVMeasurable
import Mathlib.Tactic

/-! Exact parameter-to-law bounds for the literal curved-moment instrument. -/
set_option autoImplicit false
namespace Komorebi.LSM.CurvedMoment
open MeasureTheory ProbabilityTheory
noncomputable section

namespace Reference
variable {μ : Measure ℝ} (R : Reference μ)

def absoluteFirst (_R : Reference μ) : ℝ := ∫ u, |u| ∂μ

def absoluteLegendre (_R : Reference μ) : ℝ := ∫ u, |legendre u| ∂μ

def parameterBudget (da db : ℝ) : ℝ :=
  (R.absoluteFirst * da + R.absoluteLegendre * db) / 2

theorem absoluteFirst_nonneg : 0 ≤ R.absoluteFirst := integral_nonneg (fun _ => abs_nonneg _)

theorem absoluteLegendre_nonneg : 0 ≤ R.absoluteLegendre := integral_nonneg (fun _ => abs_nonneg _)

theorem parameterBudget_nonneg {da db : ℝ} (ha : 0 ≤ da) (hb : 0 ≤ db) :
    0 ≤ R.parameterBudget da db := by
  exact div_nonneg (add_nonneg (mul_nonneg R.absoluteFirst_nonneg ha)
    (mul_nonneg R.absoluteLegendre_nonneg hb)) (by norm_num)

theorem likelihood_difference_le (a b a' b' da db u : ℝ)
    (ha : |a-a'| ≤ da) (hb : |b-b'| ≤ db) {z : State} (hz : z ∈ normalized) :
    |likelihood a b u z-likelihood a' b' u z| ≤ da*|u|+db*|legendre u| := by
  have hbounds := normalized_bounds hz
  have he : likelihood a b u z-likelihood a' b' u z =
      (a-a')*u*z 1+(b-b')*legendre u*z 2 := by unfold likelihood;ring
  rw [he]
  calc
    |(a-a')*u*z 1+(b-b')*legendre u*z 2| ≤
        |(a-a')*u*z 1|+|(b-b')*legendre u*z 2| := abs_add_le _ _
    _ ≤ da*|u|+db*|legendre u| := by
      simp only [abs_mul]
      apply add_le_add
      · calc
          |a-a'| * |u| * |z 1| ≤ da*|u| * 1 :=
            mul_le_mul (mul_le_mul_of_nonneg_right ha (abs_nonneg _)) hbounds.1
              (abs_nonneg _) (mul_nonneg (le_trans (abs_nonneg _) ha) (abs_nonneg _))
          _ = da*|u| := by ring
      · calc
          |b-b'| * |legendre u| * |z 2| ≤ db*|legendre u| * 1 :=
            mul_le_mul (mul_le_mul_of_nonneg_right hb (abs_nonneg _))
              (by simpa [abs_of_nonneg hbounds.2.1] using hbounds.2.2)
              (abs_nonneg _) (mul_nonneg (le_trans (abs_nonneg _) hb) (abs_nonneg _))
          _ = db*|legendre u| := by ring

/-- The half-L1 identity is for the actual normalized kernel measures. -/
theorem observation_lawTV_le [IsProbabilityMeasure μ] (a b ρ a' b' ρ' da db : ℝ)
    (hρ : 0 ≤ ρ) (hab : |a|+|b| ≤ 1-ρ)
    (hρ' : 0 ≤ ρ') (hab' : |a'|+|b'| ≤ 1-ρ')
    (ha : |a-a'| ≤ da) (hb : |b-b'| ≤ db)
    (z : ContinuousInstrument.DensityInstrument.State probabilityCone) :
    SequentialLowerCertificate.lawTV
      ((R.instrument a b ρ hρ hab).kernel () z)
      ((R.instrument a' b' ρ' hρ' hab').kernel () z) ≤ R.parameterBudget da db := by
  let := R.probability
  let D := R.instrument a b ρ hρ hab
  let D' := R.instrument a' b' ρ' hρ' hab'
  have hz : z.1 ∈ normalized := by rw [← base_eq_normalized];exact z.2
  have hf : Integrable (fun u => likelihood a b u z.1) μ := R.continuous_integrable (by unfold likelihood legendre;fun_prop)
  have hg : Integrable (fun u => likelihood a' b' u z.1) μ := R.continuous_integrable (by unfold likelihood legendre;fun_prop)
  have hfm : D.kernel () z=μ.withDensity (fun u => ENNReal.ofReal (likelihood a b u z.1)) := by
    rw [D.kernel_apply]
    congr 1
    funext u
    congr 1
    exact R.instrument_density a b ρ u hρ hab z.1
  have hgm : D'.kernel () z=μ.withDensity (fun u => ENNReal.ofReal (likelihood a' b' u z.1)) := by
    rw [D'.kernel_apply]
    congr 1
    funext u
    congr 1
    exact R.instrument_density a' b' ρ' u hρ' hab' z.1
  have : IsProbabilityMeasure (μ.withDensity (fun u => ENNReal.ofReal (likelihood a b u z.1))) := by rw [← hfm];infer_instance
  have : IsProbabilityMeasure (μ.withDensity (fun u => ENNReal.ofReal (likelihood a' b' u z.1))) := by rw [← hgm];infer_instance
  change SequentialLowerCertificate.lawTV (D.kernel () z) (D'.kernel () z) ≤ _
  have htv := ContinuousTVDensity.lawTV_withDensity_real μ _ _ hf hg
    (R.support.mono (fun u hu => hρ.trans (likelihood_lower a b ρ u hρ hab hu hz)))
    (R.support.mono (fun u hu => hρ'.trans (likelihood_lower a' b' ρ' u hρ' hab' hu hz)))
  simp only [←hfm,←hgm] at htv
  rw [htv]
  have hiu : Integrable (fun u : ℝ => |u|) μ := R.continuous_integrable continuous_abs
  have hiL : Integrable (fun u => |legendre u|) μ := R.continuous_integrable (by unfold legendre;fun_prop)
  have hle : (∫ u, |likelihood a b u z.1-likelihood a' b' u z.1| ∂μ) ≤
      ∫ u, da*|u|+db*|legendre u| ∂μ :=
    integral_mono_ae (hf.sub hg).abs ((hiu.const_mul da).add (hiL.const_mul db))
      (Filter.Eventually.of_forall (fun u => likelihood_difference_le a b a' b' da db u ha hb hz))
  rw [integral_add (hiu.const_mul da) (hiL.const_mul db),integral_const_mul,integral_const_mul] at hle
  unfold parameterBudget absoluteFirst absoluteLegendre
  nlinarith

theorem signalKernel_lawTV_le (a b ρ a' b' ρ' da db : ℝ)
    (hρ : 0 ≤ ρ) (hab : |a|+|b| ≤ 1-ρ)
    (hρ' : 0 ≤ ρ') (hab' : |a'|+|b'| ≤ 1-ρ')
    (ha : |a-a'| ≤ da) (hb : |b-b'| ≤ db) (s : Signal) :
    SequentialLowerCertificate.lawTV (R.signalKernel a b ρ hρ hab s)
      (R.signalKernel a' b' ρ' hρ' hab' s) ≤ R.parameterBudget da db := by
  let := R.probability
  exact R.observation_lawTV_le a b ρ a' b' ρ' da db hρ hab hρ' hab' ha hb (curveState s)

end Reference
end
end Komorebi.LSM.CurvedMoment
