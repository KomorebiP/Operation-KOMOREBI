import KomorebiPaperVI.Semigroups
import Mathlib.Analysis.SpecialFunctions.ImproperIntegrals
import Mathlib.MeasureTheory.Integral.Bochner.ContinuousLinearMap

/-! Author: Komorebi P. Laplace inversion from an explicit exponential-growth bound.
The spectral-abscissa-to-growth bridge for arbitrary finite matrices is not assumed proved. -/
namespace KomorebiPaperVI.MemoryLaplace
open Set Filter MeasureTheory
open scoped Topology
open KomorebiPaperVI.Semigroups
variable {R : Type*} [NormedRing R] [NormedAlgebra ℝ R] [CompleteSpace R]

theorem decay_integrable (B : R) (M d : ℝ) (hd : 0 < d)
    (hB : ∀ t,0 ≤ t → ‖transfer B t‖ ≤ M*Real.exp (-d*t)) :
    IntegrableOn (transfer B) (Ioi 0) := by
  apply ((integrableOn_exp_mul_Ioi (a := -d) (by linarith) 0).const_mul M).mono'
    (transfer_continuous B).aestronglyMeasurable
  filter_upwards [ae_restrict_mem measurableSet_Ioi] with t ht
  exact hB t ht.le

omit [CompleteSpace R] in
theorem decay_tendsto_zero (B : R) (M d : ℝ) (hd : 0 < d)
    (hB : ∀ t,0 ≤ t → ‖transfer B t‖ ≤ M*Real.exp (-d*t)) :
    Tendsto (transfer B) atTop (𝓝 0) := by
  apply tendsto_zero_iff_norm_tendsto_zero.mpr
  have ht : Tendsto (fun t : ℝ => M*Real.exp (-d*t)) atTop (𝓝 0) := by
    simpa using (Real.tendsto_exp_atBot.comp
      (tendsto_id.const_mul_atTop_of_neg (by linarith : -d < 0))).const_mul M
  apply squeeze_zero' (Eventually.of_forall (fun t => norm_nonneg (transfer B t))) ?_ ht
  filter_upwards [eventually_ge_atTop (0:ℝ)] with t ht
  exact hB t ht

theorem integral_generator_transfer (B : R) (M d : ℝ) (hd : 0 < d)
    (hB : ∀ t,0 ≤ t → ‖transfer B t‖ ≤ M*Real.exp (-d*t)) :
    B*(∫ t in Ioi 0,transfer B t)=-1 := by
  have hi := decay_integrable B M d hd hB
  have hprod : IntegrableOn (fun t => B*transfer B t) (Ioi 0) :=
    (ContinuousLinearMap.mul ℝ R B).integrable_comp hi
  have hf := integral_Ioi_of_hasDerivAt_of_tendsto'
    (fun t (_ : t∈Ici (0:ℝ)) => transfer_derivative_left B t)
    hprod (decay_tendsto_zero B M d hd hB)
  rw [integral_const_mul_of_integrable hi,transfer_zero,zero_sub] at hf
  exact hf

theorem shifted_laplace_right_inverse (A : R) (z M d : ℝ) (hd : 0 < d)
    (hB : ∀ t,0 ≤ t → ‖transfer (A-z • 1) t‖ ≤ M*Real.exp (-d*t)) :
    (z • 1-A)*(∫ t in Ioi 0,transfer (A-z • 1) t)=1 := by
  have h := integral_generator_transfer (A-z • 1) M d hd hB
  rw [show z • (1:R)-A=-(A-z • 1) by abel,neg_mul,h,neg_neg]

theorem memory_integral (B U V : R) (M d : ℝ) (hd : 0 < d)
    (hB : ∀ t,0 ≤ t → ‖transfer B t‖ ≤ M*Real.exp (-d*t)) :
    (∫ t in Ioi 0,U*transfer B t*V)=U*(∫ t in Ioi 0,transfer B t)*V := by
  have hi := decay_integrable B M d hd hB
  have hu : IntegrableOn (fun t => U*transfer B t) (Ioi 0) :=
    (ContinuousLinearMap.mul ℝ R U).integrable_comp hi
  rw [integral_mul_const_of_integrable hu,integral_const_mul_of_integrable hi]

end KomorebiPaperVI.MemoryLaplace
