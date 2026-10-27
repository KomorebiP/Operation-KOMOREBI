import KomorebiPhysics.Relativistic3DFourierHilbertStability
import Mathlib.Analysis.SpecialFunctions.Exponential
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Analysis.Normed.Group.Bounded
import Mathlib.Tactic.Module
import Mathlib.Tactic.Ring

/-!
# Compact-time consistency for finite-cutoff Dirac propagation

This module develops the compact-time operator estimate required after
Hilbert stability.  The results are designed for warning-as-error compilation and clean replay.
-/

noncomputable section
set_option autoImplicit false
set_option linter.style.haveILetI false
set_option maxHeartbeats 800000

open Filter Asymptotics
open scoped Topology BigOperators

namespace KomorebiPhysics
namespace Relativistic3DFourierCompactTime

open Relativistic3DFourierHilbertStability

abbrev FourierMode := Relativistic3DFourierHilbertStability.Mode
abbrev sinQuot := Relativistic3DFourierGenerator.sinQuot
abbrev modeMomentum := Relativistic3DFourierGenerator.modeMomentum
abbrev TorusSpinorL2 := Relativistic3DFourierL2Generator.TorusSpinorL2
abbrev modeEmbedIsometry := Relativistic3DFourierL2Generator.modeEmbedIsometry

local instance : NormedAlgebra ℚ HilbertSpinorEnd :=
  NormedAlgebra.restrictScalars ℚ ℂ HilbertSpinorEnd

/-- The Banach-algebra exponential is Lipschitz on every nonempty closed ball
in the finite-dimensional four-spinor endomorphism algebra. -/
theorem exists_exp_lipschitz_closedBall (R : ℝ) (hR : 0 ≤ R) :
    ∃ C : ℝ, 0 ≤ C ∧
      ∀ X ∈ Metric.closedBall (0 : HilbertSpinorEnd) R,
        ∀ Y ∈ Metric.closedBall (0 : HilbertSpinorEnd) R,
          ‖NormedSpace.exp X - NormedSpace.exp Y‖ ≤ C * ‖X - Y‖ := by
  letI : ProperSpace HilbertSpinorEnd := FiniteDimensional.proper ℂ HilbertSpinorEnd
  have hcontDiff : ContDiff ℂ 1
      (NormedSpace.exp : HilbertSpinorEnd → HilbertSpinorEnd) := by
    rw [contDiff_iff_contDiffAt]
    intro X
    exact (NormedSpace.exp_analytic X).contDiffAt
  have hdf : Continuous
      (fderiv ℂ (NormedSpace.exp : HilbertSpinorEnd → HilbertSpinorEnd)) :=
    hcontDiff.continuous_fderiv (by norm_num)
  have hcompact : IsCompact (Metric.closedBall (0 : HilbertSpinorEnd) R) :=
    ProperSpace.isCompact_closedBall _ _
  have hdfOn : ContinuousOn
      (fderiv ℂ (NormedSpace.exp : HilbertSpinorEnd → HilbertSpinorEnd))
      (Metric.closedBall (0 : HilbertSpinorEnd) R) := by
    exact hdf.continuousOn
  obtain ⟨C, hC⟩ := IsCompact.exists_bound_of_continuousOn
    (E := HilbertSpinorEnd →L[ℂ] HilbertSpinorEnd) hcompact hdfOn
  have hzero : (0 : HilbertSpinorEnd) ∈ Metric.closedBall 0 R := by
    simpa [Metric.mem_closedBall] using hR
  have hC0 : 0 ≤ C :=
    (norm_nonneg (fderiv ℂ (NormedSpace.exp : HilbertSpinorEnd → HilbertSpinorEnd) 0)).trans
      (hC 0 hzero)
  refine ⟨C, hC0, ?_⟩
  intro X hX Y hY
  have hdiff := (convex_closedBall (0 : HilbertSpinorEnd) R).norm_image_sub_le_of_norm_fderiv_le
    (fun Z _ => (NormedSpace.exp_analytic Z).differentiableAt)
    (fun Z hZ => hC Z hZ) hY hX
  simpa [norm_neg, sub_eq_add_neg, add_comm] using hdiff

/-- Exact Hilbert-space generator residual; the mass contribution cancels. -/
theorem centralHilbertModeOperator_sub_continuum (m h : ℝ) (n : FourierMode) :
    centralHilbertModeOperator m h n - continuumHilbertModeOperator m n =
      (((sinQuot (modeMomentum n 0) h - modeMomentum n 0 : ℝ) : ℂ) •
          alphaXHilbertOperator +
       ((sinQuot (modeMomentum n 1) h - modeMomentum n 1 : ℝ) : ℂ) •
          alphaYHilbertOperator +
       ((sinQuot (modeMomentum n 2) h - modeMomentum n 2 : ℝ) : ℂ) •
          alphaZHilbertOperator) := by
  simp only [centralHilbertModeOperator, continuumHilbertModeOperator, Complex.ofReal_sub]
  module

/-- Scalar multiplication of a fixed Hilbert-space endomorphism as a continuous linear map. -/
def smulHilbertOperatorCLM (A : HilbertSpinorEnd) : ℂ →L[ℂ] HilbertSpinorEnd :=
  ContinuousLinearMap.smulRight (ContinuousLinearMap.id ℂ ℂ) A

@[simp] theorem smulHilbertOperatorCLM_apply (A : HilbertSpinorEnd) (z : ℂ) :
    smulHilbertOperatorCLM A z = z • A := rfl

/-- A sine-quotient residual times a fixed Hilbert-space endomorphism remains quadratic. -/
theorem sinQuot_residual_hilbert_operator_isBigO (k : ℝ) (A : HilbertSpinorEnd) :
    (fun h : ℝ => (((sinQuot k h - k : ℝ) : ℂ) • A)) =O[𝓝[>] 0]
      (fun h : ℝ => h ^ 2) := by
  have hc0 := Complex.ofRealCLM.isBigO_comp
    (fun h : ℝ => sinQuot k h - k) (𝓝[>] 0)
  have hc : (fun h : ℝ => ((sinQuot k h - k : ℝ) : ℂ)) =O[𝓝[>] 0]
      (fun h : ℝ => h ^ 2) :=
    hc0.trans (Relativistic1DContinuumLimit.sinQuot_expansion_isBigO k)
  have hop := (smulHilbertOperatorCLM A).isBigO_comp
    (fun h : ℝ => ((sinQuot k h - k : ℝ) : ℂ)) (𝓝[>] 0)
  simpa only [smulHilbertOperatorCLM_apply] using hop.trans hc

/-- The Hilbert-space central mode generator converges in operator norm with quadratic order. -/
theorem centralHilbertModeOperator_sub_continuum_isBigO (m : ℝ) (n : FourierMode) :
    (fun h : ℝ => centralHilbertModeOperator m h n - continuumHilbertModeOperator m n)
      =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
  have hx := sinQuot_residual_hilbert_operator_isBigO
    (modeMomentum n 0) alphaXHilbertOperator
  have hy := sinQuot_residual_hilbert_operator_isBigO
    (modeMomentum n 1) alphaYHilbertOperator
  have hz := sinQuot_residual_hilbert_operator_isBigO
    (modeMomentum n 2) alphaZHilbertOperator
  exact ((hx.add hy).add hz).congr_left (by
    intro h
    exact (centralHilbertModeOperator_sub_continuum m h n).symm)

/-- Operator-norm convergence of the Hilbert-space central mode generator. -/
theorem tendsto_centralHilbertModeOperator (m : ℝ) (n : FourierMode) :
    Tendsto (fun h : ℝ => centralHilbertModeOperator m h n)
      (𝓝[>] 0) (𝓝 (continuumHilbertModeOperator m n)) := by
  have herr := (centralHilbertModeOperator_sub_continuum_isBigO m n).trans_tendsto (by
    have hid : Tendsto (fun h : ℝ => h) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 2)
  have hc : Tendsto (fun _ : ℝ => continuumHilbertModeOperator m n)
      (𝓝[>] 0) (𝓝 (continuumHilbertModeOperator m n)) := tendsto_const_nhds
  simpa only [sub_add_cancel, zero_add] using herr.add hc

/-- Exact norm of the Schrödinger time coefficient. -/
theorem norm_schrodingerCoefficient (t : ℝ) :
    ‖-(Complex.I * (t : ℂ))‖ = |t| := by
  simp

/-- Uniform quadratic propagator consistency for one fixed Fourier mode on a
compact time window.  The constant is independent of `t` for `|t| ≤ T`. -/
theorem exists_compactTime_mode_propagator_bound (m T : ℝ) (n : FourierMode)
    (hT : 0 ≤ T) :
    ∃ K : ℝ, 0 ≤ K ∧
      ∀ᶠ h in 𝓝[>] (0 : ℝ), ∀ t : ℝ, |t| ≤ T →
        ‖centralHilbertModePropagator m h n t -
            continuumHilbertModePropagator m n t‖ ≤ K * ‖h ^ 2‖ := by
  let H : HilbertSpinorEnd := continuumHilbertModeOperator m n
  have hgen := centralHilbertModeOperator_sub_continuum_isBigO m n
  obtain ⟨c, hc0, hc⟩ := hgen.exists_nonneg
  have hnear : ∀ᶠ h in 𝓝[>] (0 : ℝ),
      centralHilbertModeOperator m h n ∈ Metric.ball H 1 :=
    (tendsto_centralHilbertModeOperator m n).eventually
      (Metric.ball_mem_nhds H zero_lt_one)
  let R : ℝ := T * (‖H‖ + 1)
  have hR : 0 ≤ R := by
    dsimp [R]
    positivity
  obtain ⟨C, hC0, hLip⟩ := exists_exp_lipschitz_closedBall R hR
  refine ⟨C * T * c, by positivity, ?_⟩
  filter_upwards [hc.bound, hnear] with h hh hclose
  intro t ht
  have hcentral : ‖centralHilbertModeOperator m h n‖ ≤ ‖H‖ + 1 := by
    have hd : ‖centralHilbertModeOperator m h n - H‖ < 1 := by
      simpa [Metric.mem_ball, dist_eq_norm] using hclose
    calc
      ‖centralHilbertModeOperator m h n‖ =
          ‖(centralHilbertModeOperator m h n - H) + H‖ := by rw [sub_add_cancel]
      _ ≤ ‖centralHilbertModeOperator m h n - H‖ + ‖H‖ := norm_add_le _ _
      _ ≤ 1 + ‖H‖ := by nlinarith [le_of_lt hd]
      _ = ‖H‖ + 1 := by ring
  have hH : ‖H‖ ≤ ‖H‖ + 1 := by linarith
  have hscaledCentral :
      ‖hilbertTimeScaledOperator t (centralHilbertModeOperator m h n)‖ ≤ R := by
    rw [hilbertTimeScaledOperator, norm_smul, norm_schrodingerCoefficient]
    dsimp [R]
    exact mul_le_mul ht hcentral (norm_nonneg _) hT
  have hscaledH : ‖hilbertTimeScaledOperator t H‖ ≤ R := by
    rw [hilbertTimeScaledOperator, norm_smul, norm_schrodingerCoefficient]
    dsimp [R]
    exact mul_le_mul ht hH (norm_nonneg _) hT
  have hballCentral : hilbertTimeScaledOperator t (centralHilbertModeOperator m h n) ∈
      Metric.closedBall (0 : HilbertSpinorEnd) R := by
    simpa [Metric.mem_closedBall, dist_eq_norm] using hscaledCentral
  have hballH : hilbertTimeScaledOperator t H ∈
      Metric.closedBall (0 : HilbertSpinorEnd) R := by
    simpa [Metric.mem_closedBall, dist_eq_norm] using hscaledH
  have hscaledExact :
      hilbertTimeScaledOperator t (centralHilbertModeOperator m h n) -
          hilbertTimeScaledOperator t H =
        (-(Complex.I * (t : ℂ))) •
          (centralHilbertModeOperator m h n - H) := by
    simp only [hilbertTimeScaledOperator]
    module
  have hscaledDiff :
      ‖hilbertTimeScaledOperator t (centralHilbertModeOperator m h n) -
          hilbertTimeScaledOperator t H‖ ≤
        T * ‖centralHilbertModeOperator m h n - H‖ := by
    rw [hscaledExact, norm_smul, norm_schrodingerCoefficient]
    exact mul_le_mul_of_nonneg_right ht (norm_nonneg _)
  have hexp := hLip
    (hilbertTimeScaledOperator t (centralHilbertModeOperator m h n)) hballCentral
    (hilbertTimeScaledOperator t H) hballH
  change ‖NormedSpace.exp
      (hilbertTimeScaledOperator t (centralHilbertModeOperator m h n)) -
      NormedSpace.exp (hilbertTimeScaledOperator t H)‖ ≤ _
  calc
    ‖NormedSpace.exp
        (hilbertTimeScaledOperator t (centralHilbertModeOperator m h n)) -
        NormedSpace.exp (hilbertTimeScaledOperator t H)‖
        ≤ C * ‖hilbertTimeScaledOperator t (centralHilbertModeOperator m h n) -
          hilbertTimeScaledOperator t H‖ := hexp
    _ ≤ C * (T * ‖centralHilbertModeOperator m h n - H‖) :=
      mul_le_mul_of_nonneg_left hscaledDiff hC0
    _ ≤ C * (T * (c * ‖h ^ 2‖)) := by
      gcongr
    _ = (C * T * c) * ‖h ^ 2‖ := by ring


/-- The finite-packet compact-time propagator residual in torus `L²`. -/
def compactTimePacketResidualL2 (m h t : ℝ) (S : Finset FourierMode)
    (a : FourierMode → HilbertSpinor) : TorusSpinorL2 :=
  centralHilbertPropagatedPacketL2 m h t S a -
    continuumHilbertPropagatedPacketL2 m t S a

/-- Exact decomposition of the finite-packet propagator residual into mode residuals. -/
theorem compactTimePacketResidualL2_eq_sum (m h t : ℝ) (S : Finset FourierMode)
    (a : FourierMode → HilbertSpinor) :
    compactTimePacketResidualL2 m h t S a =
      ∑ n ∈ S, modeEmbedIsometry n
        ((centralHilbertModePropagator m h n t -
          continuumHilbertModePropagator m n t) (a n)) := by
  rw [compactTimePacketResidualL2, centralHilbertPropagatedPacketL2,
    continuumHilbertPropagatedPacketL2]
  rw [← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro n hn
  simp only [map_sub, sub_apply]

/-- Every fixed finite Fourier packet admits one quadratic propagator-error
constant valid throughout the compact time interval `|t| ≤ T`. -/
theorem exists_compactTime_packet_propagator_bound (m T : ℝ)
    (S : Finset FourierMode) (a : FourierMode → HilbertSpinor) (hT : 0 ≤ T) :
    ∃ K : ℝ, 0 ≤ K ∧
      ∀ᶠ h in 𝓝[>] (0 : ℝ), ∀ t : ℝ, |t| ≤ T →
        ‖compactTimePacketResidualL2 m h t S a‖ ≤ K * ‖h ^ 2‖ := by
  classical
  let Kmode : FourierMode → ℝ := fun n =>
    Classical.choose (exists_compactTime_mode_propagator_bound m T n hT)
  have hKmode0 : ∀ n, 0 ≤ Kmode n := by
    intro n
    exact (Classical.choose_spec
      (exists_compactTime_mode_propagator_bound m T n hT)).1
  have hKmodeEvent : ∀ n, ∀ᶠ h in 𝓝[>] (0 : ℝ), ∀ t : ℝ, |t| ≤ T →
      ‖centralHilbertModePropagator m h n t -
        continuumHilbertModePropagator m n t‖ ≤ Kmode n * ‖h ^ 2‖ := by
    intro n
    exact (Classical.choose_spec
      (exists_compactTime_mode_propagator_bound m T n hT)).2
  have hall : ∀ᶠ h in 𝓝[>] (0 : ℝ), ∀ n ∈ S, ∀ t : ℝ, |t| ≤ T →
      ‖centralHilbertModePropagator m h n t -
        continuumHilbertModePropagator m n t‖ ≤ Kmode n * ‖h ^ 2‖ := by
    exact (Finset.eventually_all S).2 (fun n _ => hKmodeEvent n)
  let K : ℝ := ∑ n ∈ S, Kmode n * ‖a n‖
  have hK0 : 0 ≤ K := by
    dsimp [K]
    exact Finset.sum_nonneg fun n _ => mul_nonneg (hKmode0 n) (norm_nonneg _)
  refine ⟨K, hK0, ?_⟩
  filter_upwards [hall] with h hh
  intro t ht
  rw [compactTimePacketResidualL2_eq_sum]
  calc
    ‖∑ n ∈ S, modeEmbedIsometry n
        ((centralHilbertModePropagator m h n t -
          continuumHilbertModePropagator m n t) (a n))‖
        ≤ ∑ n ∈ S, ‖modeEmbedIsometry n
          ((centralHilbertModePropagator m h n t -
            continuumHilbertModePropagator m n t) (a n))‖ := norm_sum_le _ _
    _ ≤ ∑ n ∈ S, (Kmode n * ‖a n‖) * ‖h ^ 2‖ := by
      apply Finset.sum_le_sum
      intro n hn
      calc
        ‖modeEmbedIsometry n
            ((centralHilbertModePropagator m h n t -
              continuumHilbertModePropagator m n t) (a n))‖
            = ‖(centralHilbertModePropagator m h n t -
              continuumHilbertModePropagator m n t) (a n)‖ := by
                rw [Relativistic3DFourierL2Generator.modeEmbedIsometry_apply,
                  Relativistic3DFourierL2Generator.norm_modeEmbed]
        _ ≤ ‖centralHilbertModePropagator m h n t -
              continuumHilbertModePropagator m n t‖ * ‖a n‖ :=
            ContinuousLinearMap.le_opNorm _ _
        _ ≤ (Kmode n * ‖h ^ 2‖) * ‖a n‖ :=
            mul_le_mul_of_nonneg_right (hh n hn t ht) (norm_nonneg _)
        _ = (Kmode n * ‖a n‖) * ‖h ^ 2‖ := by ring
    _ = K * ‖h ^ 2‖ := by
      dsimp [K]
      rw [Finset.sum_mul]

/-- Exact unitary two-tail estimate used to remove a finite approximation cutoff. -/
theorem norm_sub_le_two_tail {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    (U V : E →L[ℂ] E) (f g : E)
    (hU : ∀ x, ‖U x‖ = ‖x‖) (hV : ∀ x, ‖V x‖ = ‖x‖) :
    ‖U f - V f‖ ≤ 2 * ‖f - g‖ + ‖U g - V g‖ := by
  have hdecomp :
      U f - V f = U (f - g) + (U g - V g) + V (g - f) := by
    simp only [map_sub]
    module
  rw [hdecomp]
  calc
    ‖U (f - g) + (U g - V g) + V (g - f)‖
        ≤ ‖U (f - g) + (U g - V g)‖ + ‖V (g - f)‖ := norm_add_le _ _
    _ ≤ (‖U (f - g)‖ + ‖U g - V g‖) + ‖V (g - f)‖ := by
      gcongr
      exact norm_add_le _ _
    _ = 2 * ‖f - g‖ + ‖U g - V g‖ := by
      rw [hU, hV, norm_sub_rev]
      ring

/-- Compact-window cutoff-removal estimate from exact norm preservation and a
uniform estimate on one finite approximation `g`. -/
theorem norm_sub_le_two_tail_of_compact_core {E : Type*}
    [NormedAddCommGroup E] [NormedSpace ℂ E]
    (Uh U : ℝ → E →L[ℂ] E) (T ε : ℝ) (f g : E)
    (hUh : ∀ t x, ‖Uh t x‖ = ‖x‖) (hU : ∀ t x, ‖U t x‖ = ‖x‖)
    (hcore : ∀ t, |t| ≤ T → ‖Uh t g - U t g‖ ≤ ε) :
    ∀ t, |t| ≤ T → ‖Uh t f - U t f‖ ≤ 2 * ‖f - g‖ + ε := by
  intro t ht
  exact (norm_sub_le_two_tail (Uh t) (U t) f g (hUh t) (hU t)).trans
    (add_le_add_right (hcore t ht) _)

end Relativistic3DFourierCompactTime
end KomorebiPhysics
