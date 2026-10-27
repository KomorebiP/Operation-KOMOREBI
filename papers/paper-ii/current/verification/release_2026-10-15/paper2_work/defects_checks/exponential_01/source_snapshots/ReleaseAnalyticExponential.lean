import KomorebiVerification.PaperII.TypedLinearDefects
import Mathlib.Analysis.SpecialFunctions.Exponential
import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus

set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.ReleaseAnalyticExponential
open scoped Topology
open MeasureTheory
open TypedLinearDefects
universe u v w
variable {𝕜 : Type u} [RCLike 𝕜]
variable {Ef : Type v} {Ec : Type w}
variable [NormedAddCommGroup Ef] [NormedAddCommGroup Ec]
variable [NormedSpace 𝕜 Ef] [NormedSpace 𝕜 Ec]
variable [CompleteSpace Ef] [CompleteSpace Ec]

/-- The genuinely rectangular operator path whose endpoint difference is the
exponential defect. -/
def exponentialPath (C : Ef →L[𝕜] Ec)
    (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec) (t s : 𝕜) : Ef →L[𝕜] Ec :=
  (NormedSpace.exp ((t - s) • Tc)).comp
    (C.comp (NormedSpace.exp (s • Tf)))

/-- The Duhamel integrand, retaining coarse/fine multiplication order. -/
def exponentialKernel (C : Ef →L[𝕜] Ec)
    (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec) (t s : 𝕜) : Ef →L[𝕜] Ec :=
  (NormedSpace.exp ((t - s) • Tc)).comp
    ((continuousDefect C Tf Tc).comp (NormedSpace.exp (s • Tf)))

/-- Actual Banach-algebra exponential differentiation and the typed bilinear
composition product rule produce the Duhamel kernel. -/
theorem hasDerivAt_exponentialPath
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec) (t s : 𝕜) :
    HasDerivAt (exponentialPath C Tf Tc t) (exponentialKernel C Tf Tc t s) s := by
  have hc := (NormedSpace.hasDerivAt_exp_smul_const Tc (t - s)).scomp s
    ((hasDerivAt_id s).const_sub t)
  have hf := NormedSpace.hasDerivAt_exp_smul_const' Tf s
  have h := hc.clm_comp ((hasDerivAt_const s C).clm_comp hf)
  convert h using 1
  · rfl
  · ext x
    simp [exponentialKernel, continuousDefect, ContinuousLinearMap.mul_apply,
      sub_eq_add_neg, map_add, map_neg]

/-- Continuity is derived from the actual exponential maps, not supplied as
an integration certificate. -/
theorem continuous_exponentialKernel
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec) (t : 𝕜) :
    Continuous (exponentialKernel C Tf Tc t) := by
  have hf := (NormedSpace.differentiable_exp_smul_const 𝕜 Tf).continuous
  have hc := (NormedSpace.differentiable_exp_smul_const 𝕜 Tc).continuous.comp
    (continuous_const.sub continuous_id)
  exact hc.clm_comp (continuous_const.clm_comp hf)

@[simp] theorem exponentialPath_zero
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec) (t : 𝕜) :
    exponentialPath C Tf Tc t 0 = (NormedSpace.exp (t • Tc)).comp C := by
  simp [exponentialPath, NormedSpace.exp_zero, ContinuousLinearMap.one_def]

@[simp] theorem exponentialPath_self
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec) (t : 𝕜) :
    exponentialPath C Tf Tc t t = C.comp (NormedSpace.exp (t • Tf)) := by
  simp [exponentialPath, NormedSpace.exp_zero, ContinuousLinearMap.one_def]

/-- The pointwise estimate used inside the integral, requiring no relation
between the fine and coarse operator norms. -/
theorem norm_exponentialKernel_le
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec) (t s : 𝕜) :
    ‖exponentialKernel C Tf Tc t s‖ ≤
      ‖continuousDefect C Tf Tc‖ *
        (‖NormedSpace.exp ((t-s) • Tc)‖ * ‖NormedSpace.exp (s • Tf)‖) := by
  unfold exponentialKernel
  calc
    _ ≤ ‖NormedSpace.exp ((t-s) • Tc)‖ *
        ‖(continuousDefect C Tf Tc).comp (NormedSpace.exp (s • Tf))‖ :=
      ContinuousLinearMap.opNorm_comp_le _ _
    _ ≤ ‖NormedSpace.exp ((t-s) • Tc)‖ *
        (‖continuousDefect C Tf Tc‖ * ‖NormedSpace.exp (s • Tf)‖) :=
      mul_le_mul_of_nonneg_left (ContinuousLinearMap.opNorm_comp_le _ _) (norm_nonneg _)
    _ = _ := by ac_rfl

section RealParameter
variable [NormedSpace ℝ Ef] [NormedSpace ℝ Ec]
variable [IsScalarTower ℝ 𝕜 Ef] [IsScalarTower ℝ 𝕜 Ec]

/-- Duhamel's identity for every real time, including negative time, on real
or complex Banach spaces with their compatible real scalar structures. -/
theorem exponential_defect_real
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec) (t : ℝ) :
    C.comp (NormedSpace.exp ((t : 𝕜) • Tf)) -
        (NormedSpace.exp ((t : 𝕜) • Tc)).comp C =
      ∫ s : ℝ in 0..t, exponentialKernel C Tf Tc (t : 𝕜) (s : 𝕜) := by
  have hd (s : ℝ) :
      HasDerivAt (fun r : ℝ => exponentialPath C Tf Tc (t : 𝕜) (r : 𝕜))
        (exponentialKernel C Tf Tc (t : 𝕜) (s : 𝕜)) s := by
    simpa using (hasDerivAt_exponentialPath C Tf Tc (t : 𝕜) (s : 𝕜)).scomp s
      (RCLike.ofRealCLM (K := 𝕜)).hasDerivAt
  have hi : IntervalIntegrable
      (fun s : ℝ => exponentialKernel C Tf Tc (t : 𝕜) (s : 𝕜)) volume 0 t :=
    ((continuous_exponentialKernel C Tf Tc (t : 𝕜)).comp RCLike.continuous_ofReal).intervalIntegrable _ _
  simpa using (intervalIntegral.integral_eq_sub_of_hasDerivAt (fun s hs => hd s) hi).symm

/-- The complex-time statement uses the actual straight-segment
parameterization s=u*t, so the integral includes the tangent factor t. -/
theorem exponential_defect_segment
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec) (t : 𝕜) :
    C.comp (NormedSpace.exp (t • Tf)) - (NormedSpace.exp (t • Tc)).comp C =
      ∫ s : ℝ in (0:ℝ)..1, t • exponentialKernel C Tf Tc t (s • t) := by
  have hd (s : ℝ) :
      HasDerivAt (fun r : ℝ => exponentialPath C Tf Tc t (r • t))
        (t • exponentialKernel C Tf Tc t (s • t)) s := by
    simpa using (hasDerivAt_exponentialPath C Tf Tc t (s • t)).scomp s
      ((hasDerivAt_id s).smul_const t)
  have hi : IntervalIntegrable
      (fun s : ℝ => t • exponentialKernel C Tf Tc t (s • t)) volume 0 1 :=
    (continuous_const.smul ((continuous_exponentialKernel C Tf Tc t).comp
      (continuous_id.smul continuous_const))).intervalIntegrable _ _
  simpa using (intervalIntegral.integral_eq_sub_of_hasDerivAt (fun s hs => hd s) hi).symm

/-- The exact manuscript norm estimate for real nonnegative time. -/
theorem norm_exponential_defect_real_le
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec)
    (t : ℝ) (ht : 0 ≤ t) :
    ‖C.comp (NormedSpace.exp ((t : 𝕜) • Tf)) -
        (NormedSpace.exp ((t : 𝕜) • Tc)).comp C‖ ≤
      ‖continuousDefect C Tf Tc‖ *
        ∫ s : ℝ in 0..t,
          ‖NormedSpace.exp (((t : 𝕜) - (s : 𝕜)) • Tc)‖ *
          ‖NormedSpace.exp ((s : 𝕜) • Tf)‖ := by
  rw [exponential_defect_real]
  have hf : Continuous (fun s : ℝ => NormedSpace.exp ((s : 𝕜) • Tf)) :=
    (NormedSpace.differentiable_exp_smul_const 𝕜 Tf).continuous.comp RCLike.continuous_ofReal
  have hc : Continuous (fun s : ℝ => NormedSpace.exp (((t : 𝕜) - (s : 𝕜)) • Tc)) :=
    (NormedSpace.differentiable_exp_smul_const 𝕜 Tc).continuous.comp
      (continuous_const.sub RCLike.continuous_ofReal)
  calc
    _ ≤ ∫ s : ℝ in 0..t, ‖continuousDefect C Tf Tc‖ *
          (‖NormedSpace.exp (((t : 𝕜) - (s : 𝕜)) • Tc)‖ *
           ‖NormedSpace.exp ((s : 𝕜) • Tf)‖) := by
      apply intervalIntegral.norm_integral_le_of_norm_le ht
      · exact Filter.Eventually.of_forall (fun s hs => norm_exponentialKernel_le C Tf Tc _ _)
      · exact (continuous_const.mul (hc.norm.mul hf.norm)).intervalIntegrable _ _
    _ = _ := intervalIntegral.integral_const_mul _ _

/-- A zero one-step defect gives the exact complex/real exponential
compatibility, using the segment formula just proved. -/
theorem exponential_compatible_of_defect_eq_zero
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec)
    (h : continuousDefect C Tf Tc = 0) (t : 𝕜) :
    C.comp (NormedSpace.exp (t • Tf)) = (NormedSpace.exp (t • Tc)).comp C := by
  apply sub_eq_zero.mp
  rw [exponential_defect_segment]
  simp [exponentialKernel, h]
end RealParameter
end Komorebi.PaperII.ReleaseAnalyticExponential
