import KomorebiPhysics.Relativistic3DCenteredConvergence
import Mathlib.Analysis.InnerProductSpace.Adjoint
import Mathlib.Analysis.CStarAlgebra.Spectrum
import Mathlib.Analysis.CStarAlgebra.ContinuousLinearMap

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000
open Filter
open scoped ComplexConjugate ENNReal BigOperators Topology lp LinearPMap

namespace KomorebiPhysics.Relativistic3DCenteredResolvent
variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E] [CompleteSpace E]

theorem shifted_isUnit (A : E →L[ℂ] E) (hA : IsSelfAdjoint A)
    (z : ℂ) (hz : z.im ≠ 0) : IsUnit (A - z • (1 : E →L[ℂ] E)) := by
  have hn : z ∉ spectrum ℂ A := fun h => hz (hA.im_eq_zero_of_mem_spectrum h)
  have hu := spectrum.notMem_iff.mp hn
  simpa only [Algebra.algebraMap_eq_smul_one, neg_sub] using hu.neg

omit [CompleteSpace E] in
theorem shifted_lower_bound (A : E →L[ℂ] E)
    (hA : (A : E →ₗ[ℂ] E).IsSymmetric) (z : ℂ) (v : E) :
    |z.im| * ‖v‖ ≤ ‖A v - z • v‖ := by
  by_cases hv : v = 0
  · simp [hv]
  have hvp : 0 < ‖v‖ := norm_pos_iff.mpr hv
  have him : (inner ℂ v (A v - z • v)).im = -z.im * ‖v‖ ^ 2 := by
    have hr : (inner ℂ v (A v)).im = 0 := hA.im_inner_self_apply v
    rw [inner_sub_right, inner_smul_right, inner_self_eq_norm_sq_to_K]
    change (inner ℂ v (A v)).im - (z * (Complex.ofReal ‖v‖) ^ 2).im = _
    simp [hr, Complex.mul_im, pow_two]
  have hb := (Complex.abs_im_le_norm (inner ℂ v (A v - z • v))).trans
    (norm_inner_le_norm v (A v - z • v))
  rw [him, abs_mul, abs_neg, abs_pow, abs_of_nonneg (norm_nonneg v)] at hb
  nlinarith

def modalResolvent (A : E →L[ℂ] E) (z : ℂ) : E →L[ℂ] E :=
  Ring.inverse (A - z • (1 : E →L[ℂ] E))

theorem shifted_modalResolvent (A : E →L[ℂ] E) (hA : IsSelfAdjoint A)
    (z : ℂ) (hz : z.im ≠ 0) (v : E) :
    A (modalResolvent A z v) - z • modalResolvent A z v = v := by
  have h := congrArg (fun B : E →L[ℂ] E => B v)
    (Ring.mul_inverse_cancel _ (shifted_isUnit A hA z hz))
  simpa only [mul_apply_eq_comp, sub_apply,
    smul_apply, one_apply_eq_self, modalResolvent] using h

theorem modalResolvent_shifted (A : E →L[ℂ] E) (hA : IsSelfAdjoint A)
    (z : ℂ) (hz : z.im ≠ 0) (v : E) :
    modalResolvent A z (A v - z • v) = v := by
  have h := congrArg (fun B : E →L[ℂ] E => B v)
    (Ring.inverse_mul_cancel _ (shifted_isUnit A hA z hz))
  simpa only [mul_apply_eq_comp, sub_apply,
    smul_apply, one_apply_eq_self, modalResolvent] using h

theorem modalResolvent_norm_le (A : E →L[ℂ] E)
    (hA : (A : E →ₗ[ℂ] E).IsSymmetric) (z : ℂ) (hz : z.im ≠ 0) (v : E) :
    ‖modalResolvent A z v‖ ≤ |z.im|⁻¹ * ‖v‖ := by
  have h := shifted_lower_bound A hA z (modalResolvent A z v)
  rw [shifted_modalResolvent A hA.isSelfAdjoint z hz] at h
  exact (le_inv_mul_iff₀ (abs_pos.mpr hz)).mpr h



open Relativistic3DFourierHilbertStability
open Relativistic3DFullFourierEvolution
open Relativistic3DUnboundedDirac
open Relativistic3DWeightedDomain
open Relativistic3DGeneratorBridge
open Relativistic3DCenteredConvergence
open Relativistic3DTorusFourierEvolution

abbrev Mode := Relativistic3DFullFourierEvolution.Mode
abbrev CoeffL2 := Relativistic3DFullFourierEvolution.CoeffL2
abbrev HilbertSpinor := Relativistic3DFourierHilbertStability.HilbertSpinor
abbrev TorusSpinorL2 := Relativistic3DTorusFourierEvolution.TorusSpinorL2

/-- The nonreal resolvent of the actual maximal continuum multiplier. -/
def continuumCoeffResolvent (m : ℝ) (z : ℂ) (hz : z.im ≠ 0) : CoeffL2 →L[ℂ] CoeffL2 :=
  boundedModewiseOperator (fun n => modalResolvent (continuumHilbertModeOperator m n) z)
    |z.im|⁻¹ (inv_nonneg.mpr (abs_nonneg _))
    (fun n ψ => modalResolvent_norm_le _ (continuumHilbertModeOperator_symmetric m n) z hz ψ)

/-- The centered modal resolvent, including its removable value at zero spacing. -/
def centeredCoeffResolvent (m h : ℝ) (z : ℂ) (hz : z.im ≠ 0) : CoeffL2 →L[ℂ] CoeffL2 :=
  boundedModewiseOperator (fun n => modalResolvent (centralHilbertModeOperator m h n) z)
    |z.im|⁻¹ (inv_nonneg.mpr (abs_nonneg _))
    (fun n ψ => modalResolvent_norm_le _ (centralHilbertModeOperator_symmetric m h n) z hz ψ)

@[simp] theorem continuumCoeffResolvent_apply (m : ℝ) (z : ℂ) (hz : z.im ≠ 0)
    (f : CoeffL2) (n : Mode) :
    continuumCoeffResolvent m z hz f n = modalResolvent (continuumHilbertModeOperator m n) z (f n) := rfl

@[simp] theorem centeredCoeffResolvent_apply (m h : ℝ) (z : ℂ) (hz : z.im ≠ 0)
    (f : CoeffL2) (n : Mode) :
    centeredCoeffResolvent m h z hz f n = modalResolvent (centralHilbertModeOperator m h n) z (f n) := rfl

theorem continuumCoeffResolvent_norm_le (m : ℝ) (z : ℂ) (hz : z.im ≠ 0) :
    ‖continuumCoeffResolvent m z hz‖ ≤ |z.im|⁻¹ :=
  boundedModewiseOperator_norm_le _ _ _ _

theorem centeredCoeffResolvent_norm_le (m h : ℝ) (z : ℂ) (hz : z.im ≠ 0) :
    ‖centeredCoeffResolvent m h z hz‖ ≤ |z.im|⁻¹ :=
  boundedModewiseOperator_norm_le _ _ _ _

/-- Resolvent range is in the genuine maximal graph domain. -/
theorem continuumCoeffResolvent_mem_domain (m : ℝ) (z : ℂ) (hz : z.im ≠ 0) (f : CoeffL2) :
    continuumCoeffResolvent m z hz f ∈ continuumDiracDomain m := by
  let g := continuumCoeffResolvent m z hz f
  have he : diracCoeff m g = fun n => (f + z • g) n := by
    funext n
    change continuumHilbertModeOperator m n (modalResolvent (continuumHilbertModeOperator m n) z (f n)) =
      f n + z • modalResolvent (continuumHilbertModeOperator m n) z (f n)
    exact eq_add_of_sub_eq (shifted_modalResolvent _ (continuumHilbertModeOperator_selfAdjoint m n) z hz (f n))
  change Memℓp (diracCoeff m g) 2
  rw [he]
  exact (f + z • g).prop

/-- The continuum resolvent with its derived domain witness. -/
def continuumResolventDomain (m : ℝ) (z : ℂ) (hz : z.im ≠ 0) (f : CoeffL2) : continuumDiracDomain m :=
  ⟨continuumCoeffResolvent m z hz f, continuumCoeffResolvent_mem_domain m z hz f⟩

theorem continuum_shift_resolvent (m : ℝ) (z : ℂ) (hz : z.im ≠ 0) (f : CoeffL2) :
    continuumDiracOutput m (continuumResolventDomain m z hz f) - z • continuumCoeffResolvent m z hz f = f := by
  apply lp.ext
  funext n
  exact shifted_modalResolvent _ (continuumHilbertModeOperator_selfAdjoint m n) z hz (f n)

theorem continuum_resolvent_shift (m : ℝ) (z : ℂ) (hz : z.im ≠ 0) (f : continuumDiracDomain m) :
    continuumCoeffResolvent m z hz (continuumDiracOutput m f - z • f.1) = f.1 := by
  apply lp.ext
  funext n
  exact modalResolvent_shifted _ (continuumHilbertModeOperator_selfAdjoint m n) z hz (f.1 n)

theorem centered_shift_resolvent (m h : ℝ) (hh : h ≠ 0) (z : ℂ) (hz : z.im ≠ 0) (f : CoeffL2) :
    centeredCoeffOperator m h (centeredCoeffResolvent m h z hz f) - z • centeredCoeffResolvent m h z hz f = f := by
  apply lp.ext
  funext n
  simp only [lp.coeFn_sub, Pi.sub_apply, lp.coeFn_smul, Pi.smul_apply,
    centeredCoeffOperator_apply m h hh, centeredCoeffResolvent_apply]
  exact shifted_modalResolvent _ (centralHilbertModeOperator_selfAdjoint m h n) z hz (f n)

theorem centered_resolvent_shift (m h : ℝ) (hh : h ≠ 0) (z : ℂ) (hz : z.im ≠ 0) (f : CoeffL2) :
    centeredCoeffResolvent m h z hz (centeredCoeffOperator m h f - z • f) = f := by
  apply lp.ext
  funext n
  simp only [centeredCoeffResolvent_apply, lp.coeFn_sub, Pi.sub_apply, lp.coeFn_smul, Pi.smul_apply,
    centeredCoeffOperator_apply m h hh]
  exact modalResolvent_shifted _ (centralHilbertModeOperator_selfAdjoint m h n) z hz (f n)

/-- Actual resolvent identity, with the continuum range-domain witness supplied. -/
theorem centered_resolvent_identity (m h : ℝ) (hh : h ≠ 0) (z : ℂ) (hz : z.im ≠ 0) (f : CoeffL2) :
    centeredCoeffResolvent m h z hz f - continuumCoeffResolvent m z hz f =
      centeredCoeffResolvent m h z hz
        (continuumDiracOutput m (continuumResolventDomain m z hz f) -
          centeredCoeffOperator m h (continuumCoeffResolvent m z hz f)) := by
  let g := continuumCoeffResolvent m z hz f
  have hc := continuum_shift_resolvent m z hz f
  have hhg := centered_resolvent_shift m h hh z hz g
  calc
    _ = centeredCoeffResolvent m h z hz
        (continuumDiracOutput m (continuumResolventDomain m z hz f) - z • g) -
        centeredCoeffResolvent m h z hz (centeredCoeffOperator m h g - z • g) := by rw [hc, hhg]
    _ = _ := by rw [← map_sub]; congr 1; abel

/-- Sharp nonreal resolvent estimate reduces convergence to the graph-domain error. -/
theorem centered_resolvent_error_le (m h : ℝ) (hh : h ≠ 0) (z : ℂ) (hz : z.im ≠ 0) (f : CoeffL2) :
    ‖centeredCoeffResolvent m h z hz f - continuumCoeffResolvent m z hz f‖ ≤
      |z.im|⁻¹ * ‖continuumDiracOutput m (continuumResolventDomain m z hz f) -
        centeredCoeffOperator m h (continuumCoeffResolvent m z hz f)‖ := by
  rw [centered_resolvent_identity m h hh z hz f]
  exact (ContinuousLinearMap.le_opNorm _ _).trans
    (mul_le_mul_of_nonneg_right (centeredCoeffResolvent_norm_le m h z hz) (norm_nonneg _))

/-- Strong resolvent convergence for every square-summable vector and every nonreal parameter. -/
theorem centered_resolvent_tendsto (m : ℝ) (z : ℂ) (hz : z.im ≠ 0) (f : CoeffL2) :
    Tendsto (fun h => centeredCoeffResolvent m h z hz f) (𝓝[≠] 0)
      (𝓝 (continuumCoeffResolvent m z hz f)) := by
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  have hg := centered_graph_tendsto m (continuumResolventDomain m z hz f)
  have hc : Tendsto (fun _ : ℝ => continuumDiracOutput m (continuumResolventDomain m z hz f))
      (𝓝[≠] 0) (𝓝 (continuumDiracOutput m (continuumResolventDomain m z hz f))) := tendsto_const_nhds
  have hb := (hc.sub hg).norm.const_mul (|z.im|⁻¹)
  simp only [sub_self, norm_zero, mul_zero] at hb
  apply squeeze_zero' (Filter.Eventually.of_forall (fun _ => norm_nonneg _)) ?_ hb
  filter_upwards [self_mem_nhdsWithin] with h hh
  exact centered_resolvent_error_le m h hh z hz f

/-- Physical torus resolvent, conjugated by the existing unitary Fourier map. -/
def physicalContinuumResolvent (m : ℝ) (z : ℂ) (hz : z.im ≠ 0) : TorusSpinorL2 →L[ℂ] TorusSpinorL2 :=
  torusFourierEquiv.symm.toContinuousLinearEquiv.toContinuousLinearMap.comp
    ((continuumCoeffResolvent m z hz).comp torusFourierEquiv.toContinuousLinearEquiv.toContinuousLinearMap)

def physicalCenteredResolvent (m h : ℝ) (z : ℂ) (hz : z.im ≠ 0) : TorusSpinorL2 →L[ℂ] TorusSpinorL2 :=
  torusFourierEquiv.symm.toContinuousLinearEquiv.toContinuousLinearMap.comp
    ((centeredCoeffResolvent m h z hz).comp torusFourierEquiv.toContinuousLinearEquiv.toContinuousLinearMap)

@[simp] theorem fourier_physicalContinuumResolvent (m : ℝ) (z : ℂ) (hz : z.im ≠ 0) (f : TorusSpinorL2) :
    torusFourierEquiv (physicalContinuumResolvent m z hz f) = continuumCoeffResolvent m z hz (torusFourierEquiv f) := by
  change torusFourierEquiv (torusFourierEquiv.symm _) = _
  exact torusFourierEquiv.apply_symm_apply _

@[simp] theorem fourier_physicalCenteredResolvent (m h : ℝ) (z : ℂ) (hz : z.im ≠ 0) (f : TorusSpinorL2) :
    torusFourierEquiv (physicalCenteredResolvent m h z hz f) = centeredCoeffResolvent m h z hz (torusFourierEquiv f) := by
  change torusFourierEquiv (torusFourierEquiv.symm _) = _
  exact torusFourierEquiv.apply_symm_apply _

theorem physicalContinuumResolvent_mem_domain (m : ℝ) (z : ℂ) (hz : z.im ≠ 0) (f : TorusSpinorL2) :
    physicalContinuumResolvent m z hz f ∈ physicalDiracDomain m := by
  change torusFourierEquiv (physicalContinuumResolvent m z hz f) ∈ continuumDiracDomain m
  rw [fourier_physicalContinuumResolvent]
  exact continuumCoeffResolvent_mem_domain m z hz (torusFourierEquiv f)

/-- The physical continuum resolvent is a right inverse with an actual domain witness. -/
theorem physical_continuum_shift_resolvent (m : ℝ) (z : ℂ) (hz : z.im ≠ 0) (f : TorusSpinorL2) :
    physicalDiracPMap m ⟨physicalContinuumResolvent m z hz f,
      physicalContinuumResolvent_mem_domain m z hz f⟩ - z • physicalContinuumResolvent m z hz f = f := by
  apply torusFourierEquiv.injective
  apply lp.ext
  funext n
  simp only [map_sub, map_smul, lp.coeFn_sub, Pi.sub_apply, lp.coeFn_smul, Pi.smul_apply,
    physicalDiracPMap_apply_coeff, fourier_physicalContinuumResolvent, continuumCoeffResolvent_apply]
  exact shifted_modalResolvent _ (continuumHilbertModeOperator_selfAdjoint m n) z hz (torusFourierEquiv f n)

theorem physical_continuum_resolvent_shift (m : ℝ) (z : ℂ) (hz : z.im ≠ 0) (f : physicalDiracDomain m) :
    physicalContinuumResolvent m z hz (physicalDiracPMap m f - z • f.1) = f.1 := by
  apply torusFourierEquiv.injective
  rw [fourier_physicalContinuumResolvent, map_sub, map_smul]
  change continuumCoeffResolvent m z hz
    (torusFourierEquiv (torusFourierEquiv.symm
      (continuumDiracOutput m (physicalToCoeffDomain m f))) - z • torusFourierEquiv f.1) = _
  rw [torusFourierEquiv.apply_symm_apply]
  exact continuum_resolvent_shift m z hz (physicalToCoeffDomain m f)

theorem physical_centered_shift_resolvent (m h : ℝ) (hh : h ≠ 0) (z : ℂ) (hz : z.im ≠ 0) (f : TorusSpinorL2) :
    physicalCenteredOperator m h (physicalCenteredResolvent m h z hz f) - z • physicalCenteredResolvent m h z hz f = f := by
  apply torusFourierEquiv.injective
  simp only [map_sub, map_smul, torusFourierEquiv_physicalCenteredOperator_apply,
    fourier_physicalCenteredResolvent]
  exact centered_shift_resolvent m h hh z hz (torusFourierEquiv f)

theorem physical_centered_resolvent_shift (m h : ℝ) (hh : h ≠ 0) (z : ℂ) (hz : z.im ≠ 0) (f : TorusSpinorL2) :
    physicalCenteredResolvent m h z hz (physicalCenteredOperator m h f - z • f) = f := by
  apply torusFourierEquiv.injective
  rw [fourier_physicalCenteredResolvent, map_sub, map_smul,
    torusFourierEquiv_physicalCenteredOperator_apply]
  exact centered_resolvent_shift m h hh z hz (torusFourierEquiv f)

/-- The same all-vector, all-nonreal-parameter limit holds in actual physical torus L². -/
theorem physical_centered_resolvent_tendsto (m : ℝ) (z : ℂ) (hz : z.im ≠ 0) (f : TorusSpinorL2) :
    Tendsto (fun h => physicalCenteredResolvent m h z hz f) (𝓝[≠] 0)
      (𝓝 (physicalContinuumResolvent m z hz f)) := by
  have hc := torusFourierEquiv.symm.continuous.tendsto
    (continuumCoeffResolvent m z hz (torusFourierEquiv f))
  exact hc.comp (centered_resolvent_tendsto m z hz (torusFourierEquiv f))

end KomorebiPhysics.Relativistic3DCenteredResolvent
