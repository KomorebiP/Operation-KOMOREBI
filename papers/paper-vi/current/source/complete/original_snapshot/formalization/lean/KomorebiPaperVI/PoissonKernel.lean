import KomorebiPaperVI.SpectralPackets
import Mathlib.Analysis.SpecialFunctions.Gaussian.GaussianIntegral

/-! Author: Komorebi P. Normalized subordination density and convergence, including the zero mode.
The positive-mode Laplace identity is proved in PoissonSubordination. -/
namespace KomorebiPaperVI.PoissonKernel
open Set MeasureTheory
open scoped BigOperators

noncomputable def kernel (t s : ℝ) : ℝ :=
  t/(2*Real.sqrt Real.pi)*s^(-3/2:ℝ)*Real.exp (-t^2/(4*s))
noncomputable def heatIntegrand (t lam s : ℝ) : ℝ := kernel t s*Real.exp (-s*lam)

theorem inverse_half_square (s : ℝ) (hs : 0 ≤ s) : (s^(-1/2:ℝ))^2=s⁻¹ := by
  rw [← Real.rpow_natCast,← Real.rpow_mul hs]
  norm_num [Real.rpow_neg_one]

theorem kernel_substitution (t s : ℝ) (hs : 0 ≤ s) :
    kernel t s=t/Real.sqrt Real.pi *
      ((|(-1/2:ℝ)| *s^((-1/2:ℝ)-1)) • Real.exp (-(t^2/4)*(s^(-1/2:ℝ))^2)) := by
  unfold kernel
  rw [inverse_half_square s hs]
  norm_num
  have he : -(t^2/4*s⁻¹)=-t^2/(4*s) := by ring
  rw [he]
  ring

theorem kernel_integrable (t : ℝ) (ht : 0 < t) : IntegrableOn (kernel t) (Ioi 0) := by
  have hg := (integrable_exp_neg_mul_sq (b := t^2/4) (by positivity)).integrableOn (s := Ioi 0)
  have hi := (integrableOn_Ioi_comp_rpow_iff (fun u : ℝ => Real.exp (-(t^2/4)*u^2))
    (p := -1/2) (by norm_num)).mpr hg
  rw [integrableOn_congr_fun (fun s hs => kernel_substitution t s hs.le) measurableSet_Ioi]
  exact hi.const_mul (t/Real.sqrt Real.pi)

theorem kernel_mass (t : ℝ) (ht : 0 < t) : (∫ s in Ioi 0,kernel t s)=1 := by
  rw [setIntegral_congr_fun measurableSet_Ioi (fun s hs => kernel_substitution t s hs.le)]
  rw [integral_const_mul,integral_comp_rpow_Ioi (fun u : ℝ => Real.exp (-(t^2/4)*u^2)) (p := -1/2) (by norm_num),integral_gaussian_Ioi]
  have hp : Real.sqrt Real.pi≠0 := (Real.sqrt_pos.mpr Real.pi_pos).ne'
  rw [Real.sqrt_div Real.pi_pos.le,Real.sqrt_div (sq_nonneg t),Real.sqrt_sq_eq_abs,abs_of_pos ht]
  norm_num
  field_simp

theorem kernel_nonnegative (t s : ℝ) (ht : 0 ≤ t) (hs : 0 ≤ s) : 0 ≤ kernel t s := by
  unfold kernel
  positivity

theorem heat_integrand_bounds (t lam s : ℝ) (ht : 0 ≤ t) (hl : 0 ≤ lam) (hs : 0 ≤ s) :
    0 ≤ heatIntegrand t lam s ∧ heatIntegrand t lam s ≤ kernel t s := by
  have hk := kernel_nonnegative t s ht hs
  constructor
  · exact mul_nonneg hk (Real.exp_pos _).le
  · exact mul_le_of_le_one_right hk (Real.exp_le_one_iff.mpr (by nlinarith))

theorem heat_integrand_integrable (t lam : ℝ) (ht : 0 < t) (hl : 0 ≤ lam) :
    IntegrableOn (heatIntegrand t lam) (Ioi 0) := by
  have hc : ContinuousOn (heatIntegrand t lam) (Ioi 0) := by
    intro s hs
    unfold heatIntegrand kernel
    apply ContinuousAt.continuousWithinAt
    have hs0 : s≠0 := hs.ne'
    fun_prop (disch := simp_all)
  apply (kernel_integrable t ht).mono' (hc.aestronglyMeasurable measurableSet_Ioi)
  filter_upwards [ae_restrict_mem measurableSet_Ioi] with s hs
  rw [Real.norm_of_nonneg (heat_integrand_bounds t lam s ht.le hl hs.le).1]
  exact (heat_integrand_bounds t lam s ht.le hl hs.le).2

theorem zero_mode_subordination (t : ℝ) (ht : 0 < t) :
    (∫ s in Ioi 0,heatIntegrand t 0 s)=Real.exp (-t*Real.sqrt 0) := by
  simpa [heatIntegrand] using kernel_mass t ht

variable {I E : Type*} [Fintype I] [NormedAddCommGroup E] [NormedSpace ℝ E]
theorem finite_spectral_integrable (P : I → E) (lam : I → ℝ) (hl : ∀ i,0 ≤ lam i)
    (t : ℝ) (ht : 0 < t) :
    IntegrableOn (fun s => ∑ i,heatIntegrand t (lam i) s • P i) (Ioi 0) :=
  integrable_finsetSum _ (fun i _ => (heat_integrand_integrable t (lam i) ht (hl i)).smul_const (P i))

end KomorebiPaperVI.PoissonKernel
