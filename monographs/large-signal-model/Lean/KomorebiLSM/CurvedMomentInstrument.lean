import KomorebiLSM.CurvedMomentGeometry
import KomorebiLSM.ContinuousInstrument
import KomorebiLSM.ContinuousRecords
import Mathlib.MeasureTheory.Integral.IntegrableOn
import Mathlib.Tactic

/-! The literal two-parameter rank-one density and general four-moment reference. -/
set_option autoImplicit false
namespace Komorebi.LSM.CurvedMoment
open MeasureTheory ProbabilityTheory
open scoped BigOperators
noncomputable section

def legendre (u : ℝ) : ℝ := (3*u^2-1)/2

def likelihood (a b u : ℝ) (z : State) : ℝ := z 0+a*u*z 1+b*legendre u*z 2

def row (a b u : ℝ) : State →L[ℝ] ℝ :=
  (LinearMap.proj 0 : State →ₗ[ℝ] ℝ).toContinuousLinearMap +
  (a*u) • (LinearMap.proj 1 : State →ₗ[ℝ] ℝ).toContinuousLinearMap +
  (b*legendre u) • (LinearMap.proj 2 : State →ₗ[ℝ] ℝ).toContinuousLinearMap

def branch (a b u : ℝ) : State →L[ℝ] State := (row a b u).smulRight (curve u)

@[simp] theorem branch_apply (a b u : ℝ) (z : State) :
    branch a b u z=likelihood a b u z • curve u := rfl

@[simp] theorem branch_mass (a b u : ℝ) (z : State) :
    mass (branch a b u z)=likelihood a b u z := by
  rw [branch_apply,map_smul]
  simp [mass,curve]

theorem branch_continuous (a b : ℝ) : Continuous (branch a b) := by
  unfold branch row legendre curve
  fun_prop

theorem legendre_abs (u : ℝ) (hu : u∈Set.Icc (-1:ℝ) 1) : |legendre u|≤1 := by
  apply abs_le.mpr
  dsimp [legendre]
  constructor <;> nlinarith [sq_nonneg u,hu.1,hu.2]

theorem likelihood_lower (a b ρ u : ℝ) (_hρ : 0≤ρ)
    (hab : |a|+|b|≤1-ρ) (hu : u∈Set.Icc (-1:ℝ) 1)
    {z : State} (hz : z∈normalized) : ρ≤likelihood a b u z := by
  have hb := normalized_bounds hz
  have hx : |u|≤1 := abs_le.mpr hu
  have hax : |a*u*z 1|≤|a| := by
    rw [abs_mul,abs_mul]
    calc
      |a| * |u| * |z 1|≤|a| * 1 * 1 := mul_le_mul (mul_le_mul_of_nonneg_left hx (abs_nonneg _)) hb.1 (abs_nonneg _) (by positivity)
      _=|a| := by ring
  have hby : |b*legendre u*z 2|≤|b| := by
    rw [abs_mul,abs_mul,abs_of_nonneg hb.2.1]
    calc
      |b| * |legendre u| * z 2≤|b| * 1 * 1 := mul_le_mul (mul_le_mul_of_nonneg_left (legendre_abs u hu) (abs_nonneg _)) hb.2.2 hb.2.1 (by positivity)
      _=|b| := by ring
  dsimp [likelihood]
  rw [hz.1]
  linarith [neg_abs_le (a*u*z 1),neg_abs_le (b*legendre u*z 2)]

theorem branch_positive (a b ρ u : ℝ) (hρ : 0≤ρ)
    (hab : |a|+|b|≤1-ρ) (hu : u∈Set.Icc (-1:ℝ) 1)
    {z : State} (hz : z∈cone) : branch a b u z∈cone := by
  by_cases hm : z 0=0
  · rw [cone_mass_zero hz hm,map_zero]
    exact cone_zero
  · have hp : 0<z 0 := probabilityCone.mass_pos hz (fun he => hm (by simp [he]))
    have hs : (z 0)⁻¹•z∈probabilityCone.base := by
      refine ⟨cone_smul (inv_nonneg.mpr hp.le) hz,?_⟩
      change (z 0)⁻¹*z 0=1
      exact inv_mul_cancel₀ hm
    have hl := likelihood_lower a b ρ u hρ hab hu (by rw [←base_eq_normalized];exact hs)
    have ho : branch a b u ((z 0)⁻¹•z)∈cone := by
      rw [branch_apply]
      exact cone_smul (hρ.trans hl) (curve_mem u hu)
    have he : z=z 0•((z 0)⁻¹•z) := by rw [smul_smul,mul_inv_cancel₀ hm,one_smul]
    rw [he,map_smul]
    exact cone_smul hp.le ho

theorem posterior_curve (a b u : ℝ) (z : State) (hp : 0<likelihood a b u z) :
    (mass (branch a b u z))⁻¹ • branch a b u z=curve u := by
  rw [branch_mass,branch_apply,smul_smul,inv_mul_cancel₀ hp.ne',one_smul]

/-- The measure need not be Lebesgue or discrete; its support and four moments are explicit. -/
structure Reference (μ : Measure ℝ) where
  probability : IsProbabilityMeasure μ
  support : ∀ᵐ u∂μ,u∈Set.Icc (-1:ℝ) 1
  first : (∫ u,u∂μ)=0
  second : (∫ u,u^2∂μ)=1/3
  third : (∫ u,u^3∂μ)=0
  fourth : (∫ u,u^4∂μ)=1/5

namespace Reference
variable {μ : Measure ℝ} (R : Reference μ)
include R

theorem continuous_integrable {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]
    {f : ℝ→F} (hf : Continuous f) : Integrable f μ := by
  let := R.probability
  have he : μ.restrict (Set.Icc (-1:ℝ) 1)=μ := Measure.restrict_eq_self_of_ae_mem R.support
  have hi : IntegrableOn f (Set.Icc (-1:ℝ) 1) μ := hf.continuousOn.integrableOn_compact isCompact_Icc
  simpa only [IntegrableOn,he] using hi

theorem integral_legendre : (∫ u,legendre u∂μ)=0 := by
  let := R.probability
  have hi := R.continuous_integrable (f:=fun u : ℝ => u^2) (by fun_prop)
  simp only [legendre,div_eq_mul_inv]
  rw [integral_mul_const,integral_sub (hi.const_mul _) (integrable_const _),integral_const_mul,R.second]
  norm_num

theorem integral_likelihood (a b : ℝ) (z : State) :
    (∫ u,likelihood a b u z∂μ)=mass z := by
  let := R.probability
  have h1 := R.continuous_integrable (f:=fun u : ℝ => u) continuous_id
  have hL := R.continuous_integrable (f:=legendre) (by unfold legendre; fun_prop)
  have hi1 : Integrable (fun u => z 0+a*u*z 1) μ := (integrable_const _).add ((h1.const_mul a).mul_const (z 1))
  have hi2 : Integrable (fun u => b*legendre u*z 2) μ := (hL.const_mul b).mul_const (z 2)
  simp only [likelihood]
  rw [integral_add hi1 hi2,
    integral_add (integrable_const _) ((h1.const_mul _).mul_const _),
    integral_mul_const,integral_const_mul,R.first,integral_mul_const,integral_const_mul,R.integral_legendre]
  simp

/-- Genuine operator-valued instrument on the full proper moment cone. -/
def instrument (a b ρ : ℝ) (hρ : 0≤ρ) (hab : |a|+|b|≤1-ρ) :
    ContinuousInstrument.DensityInstrument (A:=Unit) probabilityCone μ where
  op _ := branch a b
  measurable_op _ := (branch_continuous a b).measurable
  integrable_op _ := R.continuous_integrable (branch_continuous a b)
  positive _ := R.support.mono (fun u hu z hz => branch_positive a b ρ u hρ hab hu hz)
  mass_preserving _ z := by
    change mass ((∫ u,branch a b u∂μ) z)=mass z
    rw [ContinuousLinearMap.integral_apply (R.continuous_integrable (branch_continuous a b))]
    change ContinuousInstrument.massCLM probabilityCone (∫ u,branch a b u z∂μ)=mass z
    calc
      ContinuousInstrument.massCLM probabilityCone (∫ u,branch a b u z∂μ) =
          ∫ u,ContinuousInstrument.massCLM probabilityCone (branch a b u z)∂μ :=
        ((ContinuousInstrument.massCLM probabilityCone).integral_comp_comm
          ((ContinuousLinearMap.apply ℝ State z).integrable_comp
            (R.continuous_integrable (branch_continuous a b)))).symm
      _ = mass z := by
        change (∫ u,mass (branch a b u z)∂μ)=mass z
        simp_rw [branch_mass]
        exact R.integral_likelihood a b z

end Reference
end
end Komorebi.LSM.CurvedMoment
