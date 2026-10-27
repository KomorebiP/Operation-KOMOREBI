import KomorebiPhysics.Relativistic3DGeneratorBridge
import KomorebiPhysics.Relativistic3DCenteredConvergence
import KomorebiPhysics.Relativistic3DModalPerturbation
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds

/-!
# Global quadratic spacing estimates for the centered Dirac family

The moment in this module is a spatial third-order Fourier moment on the
unchanged infinite coefficient space. No finite sampled lattice is substituted.
Copyright (c) 2026 Komorebi P. Released under the MIT license.
-/

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000

open Filter
open scoped ENNReal BigOperators Topology lp LinearPMap

namespace KomorebiPhysics
namespace Relativistic3DCenteredRates

open Relativistic3DFourierGenerator
open Relativistic3DFourierHilbertStability
open Relativistic3DFullFourierEvolution
open Relativistic3DUnboundedDirac
open Relativistic3DWeightedDomain
open Relativistic3DTorusFourierEvolution
open Relativistic3DCenteredConvergence
open Relativistic3DModalPerturbation

abbrev CoeffL2 := Relativistic3DFullFourierEvolution.CoeffL2
abbrev Mode := Relativistic3DFullFourierEvolution.Mode
abbrev HilbertSpinor := Relativistic3DFourierHilbertStability.HilbertSpinor

/-- The global scalar bound includes the removable zero-spacing value. -/
theorem sinQuot_cubic_bound (k h : ℝ) :
    |sinQuot k h - k| ≤ h ^ 2 / 6 * |k| ^ 3 := by
  by_cases hh : h = 0
  · subst h
    simp
  have habs : |h| ≠ 0 := abs_ne_zero.mpr hh
  have he : sinQuot k h - k = (Real.sin (k * h) - k * h) / h := by
    simp only [sinQuot, Relativistic1DContinuumLimit.sinQuot, hh, ↓reduceIte]
    field_simp
  rw [he, abs_div]
  calc
    _ ≤ (|k * h| ^ 3 / 6) / |h| := by
      apply div_le_div_of_nonneg_right _ (abs_nonneg h)
      simpa only [abs_sub_comm] using Real.abs_sub_sin_le (k * h)
    _ = h ^ 2 / 6 * |k| ^ 3 := by
      rw [abs_mul, mul_pow]
      calc
        _ = |k| ^ 3 * |h| ^ 2 / 6 := by field_simp
        _ = h ^ 2 / 6 * |k| ^ 3 := by rw [sq_abs]; ring

/-- Squared scalar error in the form needed by the exact Clifford identity. -/
theorem sinQuot_cubic_bound_sq (k h : ℝ) :
    (sinQuot k h - k) ^ 2 ≤ (h ^ 2 / 6) ^ 2 * k ^ 6 := by
  have hsq := pow_le_pow_left₀ (abs_nonneg (sinQuot k h - k))
    (sinQuot_cubic_bound k h) 2
  have hk : (|k| ^ 3) ^ 2 = k ^ 6 := by
    calc
      _ = (|k| ^ 2) ^ 3 := by ring
      _ = (k ^ 2) ^ 3 := by rw [sq_abs]
      _ = k ^ 6 := by ring
  simpa only [sq_abs, mul_pow, hk] using hsq

/-- Exact homogeneous spatial weight used by the quadratic estimate. -/
def thirdOrderWeight (n : Mode) : ℝ :=
  modeMomentum n 0 ^ 6 + modeMomentum n 1 ^ 6 + modeMomentum n 2 ^ 6

theorem thirdOrderWeight_nonneg (n : Mode) : 0 ≤ thirdOrderWeight n := by
  unfold thirdOrderWeight
  positivity

/-- The summand of the third-order spatial Fourier moment. -/
def thirdOrderModeTerm (f : CoeffL2) (n : Mode) : ℝ :=
  thirdOrderWeight n * ‖f n‖ ^ 2

theorem thirdOrderModeTerm_nonneg (f : CoeffL2) (n : Mode) :
    0 ≤ thirdOrderModeTerm f n :=
  mul_nonneg (thirdOrderWeight_nonneg n) (sq_nonneg _)

/-- Finiteness is expressed by convergence of the actual nonnegative series. -/
def HasThirdOrderMoment (f : CoeffL2) : Prop :=
  Summable (thirdOrderModeTerm f)

/-- The exact homogeneous moment M₃, meaningful for the rate under finiteness. -/
def thirdOrderMoment (f : CoeffL2) : ℝ :=
  Real.sqrt (∑' n, thirdOrderModeTerm f n)

theorem thirdOrderMoment_nonneg (f : CoeffL2) : 0 ≤ thirdOrderMoment f :=
  Real.sqrt_nonneg _

theorem thirdOrderMoment_sq (f : CoeffL2) :
    thirdOrderMoment f ^ 2 = ∑' n, thirdOrderModeTerm f n := by
  exact Real.sq_sqrt (tsum_nonneg (thirdOrderModeTerm_nonneg f))

theorem sq_le_one_add_sixth (x : ℝ) : x ^ 2 ≤ 1 + x ^ 6 := by
  have h := mul_nonneg (sq_nonneg (x ^ 2 - 1)) (show 0 ≤ x ^ 2 + 1 by positivity)
  nlinarith [sq_nonneg (x ^ 2)]

/-- The third-order hypothesis supplies the domain needed to apply H. -/
theorem HasThirdOrderMoment.mem_continuumDiracDomain {f : CoeffL2}
    (hf : HasThirdOrderMoment f) (m : ℝ) : f ∈ continuumDiracDomain m := by
  rw [mem_continuumDiracDomain_iff_summable_weighted, summable_weighted_iff_momentum]
  have hs : Summable (fun n => 3 * ‖f n‖ ^ 2 + thirdOrderModeTerm f n) :=
    ((summable_coeff_norm_sq f).mul_left 3).add hf
  apply hs.of_nonneg_of_le
  · intro n
    unfold momentumModeTerm momentumNormSq
    positivity
  · intro n
    have h0 := sq_le_one_add_sixth (modeMomentum n 0)
    have h1 := sq_le_one_add_sixth (modeMomentum n 1)
    have h2 := sq_le_one_add_sixth (modeMomentum n 2)
    have hw : momentumNormSq n ≤ 3 + thirdOrderWeight n := by
      unfold momentumNormSq thirdOrderWeight
      linarith
    have hb := mul_le_mul_of_nonneg_right hw (sq_nonneg ‖f n‖)
    simpa only [momentumModeTerm, thirdOrderModeTerm, add_mul] using hb

/-- Lift a squared coordinate estimate using the convergent moment series. -/
theorem norm_le_thirdOrderMoment {f u : CoeffL2} (hf : HasThirdOrderMoment f)
    {C : ℝ} (hC : 0 ≤ C)
    (hb : ∀ n, ‖u n‖ ^ 2 ≤ C ^ 2 * thirdOrderModeTerm f n) :
    ‖u‖ ≤ C * thirdOrderMoment f := by
  have hu : Summable (fun n => ‖u n‖ ^ 2) := summable_coeff_norm_sq u
  have hr : Summable (fun n => C ^ 2 * thirdOrderModeTerm f n) := hf.mul_left _
  have hs := hu.tsum_le_tsum hb hr
  have he : ‖u‖ ^ 2 = ∑' n, ‖u n‖ ^ 2 := by
    simpa using lp.norm_rpow_eq_tsum (by norm_num : 0 < (2 : ENNReal).toReal) u
  rw [← he, tsum_mul_left, ← thirdOrderMoment_sq] at hs
  have hp : 0 ≤ C * thirdOrderMoment f := mul_nonneg hC (thirdOrderMoment_nonneg f)
  exact (sq_le_sq₀ (norm_nonneg u) hp).mp (by simpa only [mul_pow] using hs)

/-- The exact Clifford identity retains the three coordinate errors in quadrature. -/
theorem centered_mode_quadratic_sq (m h : ℝ) (n : Mode) (ψ : HilbertSpinor) :
    ‖centralHilbertModeOperator m h n ψ - continuumHilbertModeOperator m n ψ‖ ^ 2 ≤
      (h ^ 2 / 6) ^ 2 * (thirdOrderWeight n * ‖ψ‖ ^ 2) := by
  rw [norm_centered_mode_sub_sq]
  have h0 := sinQuot_cubic_bound_sq (modeMomentum n 0) h
  have h1 := sinQuot_cubic_bound_sq (modeMomentum n 1) h
  have h2 := sinQuot_cubic_bound_sq (modeMomentum n 2) h
  have he :
      (sinQuot (modeMomentum n 0) h - modeMomentum n 0) ^ 2 +
      (sinQuot (modeMomentum n 1) h - modeMomentum n 1) ^ 2 +
      (sinQuot (modeMomentum n 2) h - modeMomentum n 2) ^ 2 ≤
      (h ^ 2 / 6) ^ 2 * thirdOrderWeight n := by
    unfold thirdOrderWeight
    nlinarith
  simpa only [mul_assoc] using mul_le_mul_of_nonneg_right he (sq_nonneg ‖ψ‖)

/-- A uniform modal perturbation envelope, valid at every real spacing. -/
theorem centered_mode_quadratic_bound (m h : ℝ) (n : Mode) (ψ : HilbertSpinor) :
    ‖centralHilbertModeOperator m h n ψ - continuumHilbertModeOperator m n ψ‖ ≤
      (h ^ 2 / 6 * Real.sqrt (thirdOrderWeight n)) * ‖ψ‖ := by
  have hs := centered_mode_quadratic_sq m h n ψ
  have hw := Real.sq_sqrt (thirdOrderWeight_nonneg n)
  have hp : 0 ≤ h ^ 2 / 6 * Real.sqrt (thirdOrderWeight n) * ‖ψ‖ := by positivity
  apply (sq_le_sq₀ (norm_nonneg _) hp).mp
  calc
    _ ≤ (h ^ 2 / 6) ^ 2 * (thirdOrderWeight n * ‖ψ‖ ^ 2) := hs
    _ = (h ^ 2 / 6 * Real.sqrt (thirdOrderWeight n) * ‖ψ‖) ^ 2 := by
      simp only [mul_pow, hw]
      ring

/-- Global O(h²) generator estimate on the actual maximal domain. -/
theorem centered_generator_quadratic_bound (m h : ℝ) (hh : h ≠ 0)
    (f : CoeffL2) (hf : HasThirdOrderMoment f) :
    ‖centeredCoeffOperator m h f -
      continuumDiracOutput m ⟨f, hf.mem_continuumDiracDomain m⟩‖ ≤
      h ^ 2 / 6 * thirdOrderMoment f := by
  apply norm_le_thirdOrderMoment hf (by positivity)
  intro n
  simpa only [lp.coeFn_sub, Pi.sub_apply, centeredCoeffOperator_apply m h hh,
    continuumDiracOutput_apply, thirdOrderModeTerm] using centered_mode_quadratic_sq m h n (f n)

/-- The propagator estimate uses a noncommutative perturbation argument. -/
theorem centered_mode_propagator_quadratic_bound (m h t : ℝ) (n : Mode)
    (ψ : HilbertSpinor) :
    ‖centralHilbertModePropagator m h n t ψ - continuumHilbertModePropagator m n t ψ‖ ≤
      |t| * (h ^ 2 / 6 * Real.sqrt (thirdOrderWeight n)) * ‖ψ‖ := by
  apply modal_perturbation_bound
    (centralHilbertModeOperator m h n) (continuumHilbertModeOperator m n)
    (centralHilbertModeOperator_selfAdjoint m h n)
    (continuumHilbertModeOperator_selfAdjoint m n)
    (h ^ 2 / 6 * Real.sqrt (thirdOrderWeight n)) (by positivity)
  intro φ
  change ‖centralHilbertModeOperator m h n φ - continuumHilbertModeOperator m n φ‖ ≤ _
  exact centered_mode_quadratic_bound m h n φ

/-- The sharp global quadratic propagator estimate for arbitrary signed time. -/
theorem centered_propagator_quadratic_bound (m h t : ℝ) (f : CoeffL2)
    (hf : HasThirdOrderMoment f) :
    ‖centralCoeffPropagator m h t f - continuumCoeffPropagator m t f‖ ≤
      (|t| * h ^ 2 / 6) * thirdOrderMoment f := by
  apply norm_le_thirdOrderMoment hf (by positivity)
  intro n
  have hs := pow_le_pow_left₀ (norm_nonneg _)
    (centered_mode_propagator_quadratic_bound m h t n (f n)) 2
  have hw := Real.sq_sqrt (thirdOrderWeight_nonneg n)
  simp only [lp.coeFn_sub, Pi.sub_apply, centralCoeffPropagator_apply,
    continuumCoeffPropagator_apply]
  calc
    _ ≤ (|t| * (h ^ 2 / 6 * Real.sqrt (thirdOrderWeight n)) * ‖f n‖) ^ 2 := hs
    _ = (|t| * h ^ 2 / 6) ^ 2 * thirdOrderModeTerm f n := by
      simp only [thirdOrderModeTerm, mul_pow, hw]
      ring

/-- One quadratic envelope works simultaneously on every compact time interval. -/
theorem centered_propagator_compactTime_bound (m h T : ℝ) (_hT : 0 ≤ T)
    (f : CoeffL2) (hf : HasThirdOrderMoment f) :
    ∀ t ∈ Set.Icc (-T) T,
      ‖centralCoeffPropagator m h t f - continuumCoeffPropagator m t f‖ ≤
        (T * h ^ 2 / 6) * thirdOrderMoment f := by
  intro t ht
  have habs : |t| ≤ T := abs_le.mpr ht
  have hM := thirdOrderMoment_nonneg f
  calc
    _ ≤ (|t| * h ^ 2 / 6) * thirdOrderMoment f :=
      centered_propagator_quadratic_bound m h t f hf
    _ ≤ (T * h ^ 2 / 6) * thirdOrderMoment f := by gcongr

/-- Exact Fourier transport of the generator rate to physical torus fields. -/
theorem physical_generator_quadratic_bound (m h : ℝ) (hh : h ≠ 0)
    (φ : Relativistic3DTorusFourierEvolution.TorusSpinorL2)
    (hφ : HasThirdOrderMoment (torusFourierEquiv φ)) :
    ‖physicalCenteredOperator m h φ - physicalDiracPMap m
      ⟨φ, hφ.mem_continuumDiracDomain m⟩‖ ≤
      h ^ 2 / 6 * thirdOrderMoment (torusFourierEquiv φ) := by
  rw [← torusFourierEquiv.norm_map
    (physicalCenteredOperator m h φ - physicalDiracPMap m
      ⟨φ, hφ.mem_continuumDiracDomain m⟩)]
  simp only [map_sub, torusFourierEquiv_physicalCenteredOperator_apply,
    torusFourierEquiv_physicalDiracPMap_apply]
  change ‖centeredCoeffOperator m h (torusFourierEquiv φ) -
    continuumDiracOutput m ⟨torusFourierEquiv φ, hφ.mem_continuumDiracDomain m⟩‖ ≤ _
  exact centered_generator_quadratic_bound m h hh (torusFourierEquiv φ) hφ

/-- The same sharp signed-time rate holds in physical torus L². -/
theorem physical_propagator_quadratic_bound (m h t : ℝ)
    (φ : Relativistic3DTorusFourierEvolution.TorusSpinorL2)
    (hφ : HasThirdOrderMoment (torusFourierEquiv φ)) :
    ‖centralTorusUnitary m h t φ - continuumTorusUnitary m t φ‖ ≤
      (|t| * h ^ 2 / 6) * thirdOrderMoment (torusFourierEquiv φ) := by
  rw [← torusFourierEquiv.norm_map
    (centralTorusUnitary m h t φ - continuumTorusUnitary m t φ)]
  simpa only [map_sub, torusFourierEquiv_centralTorusUnitary_apply,
    torusFourierEquiv_continuumTorusUnitary_apply, centralCoeffUnitary_apply,
    continuumCoeffUnitary_apply] using
    centered_propagator_quadratic_bound m h t (torusFourierEquiv φ) hφ

/-- Physical compact-time uniform estimate with its nonnegative horizon explicit. -/
theorem physical_propagator_compactTime_bound (m h T : ℝ) (_hT : 0 ≤ T)
    (φ : Relativistic3DTorusFourierEvolution.TorusSpinorL2)
    (hφ : HasThirdOrderMoment (torusFourierEquiv φ)) :
    ∀ t ∈ Set.Icc (-T) T,
      ‖centralTorusUnitary m h t φ - continuumTorusUnitary m t φ‖ ≤
        (T * h ^ 2 / 6) * thirdOrderMoment (torusFourierEquiv φ) := by
  intro t ht
  have habs : |t| ≤ T := abs_le.mpr ht
  have hM := thirdOrderMoment_nonneg (torusFourierEquiv φ)
  calc
    _ ≤ (|t| * h ^ 2 / 6) * thirdOrderMoment (torusFourierEquiv φ) :=
      physical_propagator_quadratic_bound m h t φ hφ
    _ ≤ (T * h ^ 2 / 6) * thirdOrderMoment (torusFourierEquiv φ) := by gcongr

end Relativistic3DCenteredRates
end KomorebiPhysics
