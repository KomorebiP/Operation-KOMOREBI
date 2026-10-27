module
public import Mathlib.Analysis.Normed.Operator.Basic
public import Mathlib.Analysis.ODE.Gronwall
public import Mathlib.Analysis.Normed.Algebra.Exponential
public import Mathlib.Analysis.Normed.Operator.NormedSpace
public import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus
public import Mathlib.Analysis.Calculus.Deriv.Mul
public import Mathlib.Tactic.FunProp
public import Mathlib.Algebra.BigOperators.Group.Finset.Basic
public import Mathlib.Analysis.InnerProductSpace.Adjoint
public import Mathlib.Tactic.Abel
public import Komorebi.PosteriorMean
@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.BayesianPosteriorPerturb

open Komorebi.AbstractProjectorRefinement
open scoped BigOperators

universe uPX uPY uPC uPF
variable {X : Type uPX} {Y : Type uPY}
variable [NormedAddCommGroup X] [InnerProductSpace ℝ X] [CompleteSpace X]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
variable {coarseLane : Type uPC} {fineLane : Type uPF}
variable [Fintype coarseLane] [Fintype fineLane] [DecidableEq coarseLane]

/-- Posterior covariance error operator for two Kalman/Joseph updates. -/
def posteriorCovErrorOp
    (K K0 : Y →L[ℝ] X) (H H0 : X →L[ℝ] Y)
    (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y) : X →L[ℝ] X :=
  josephPosteriorCov K H P R - josephPosteriorCov K0 H0 P0 R0

/-- Exact coarse-to-fine refinement of a posterior covariance error block. -/
theorem posteriorCovError_opBlock_refinement
    (C : ProjectorFamily X coarseLane) (F : ProjectorFamily X fineLane)
    (ρ : fineLane → coarseLane) (hR : Refines C F ρ)
    (K K0 : Y →L[ℝ] X) (H H0 : X →L[ℝ] Y)
    (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y)
    (a b : coarseLane) :
    opBlock C (posteriorCovErrorOp K K0 H H0 P P0 R R0) a b =
      descendantOpBlockSum F ρ (posteriorCovErrorOp K K0 H H0 P P0 R R0) a b := by
  exact opBlock_refinement C F ρ hR
    (posteriorCovErrorOp K K0 H H0 P P0 R R0) a b

/-- No-cancellation theorem for posterior covariance error under orthogonal refinement. -/
theorem posteriorCovError_opBlock_zero_iff_descendants_zero
    (C : ProjectorFamily X coarseLane) (F : ProjectorFamily X fineLane)
    (ρ : fineLane → coarseLane) (hR : Refines C F ρ)
    (K K0 : Y →L[ℝ] X) (H H0 : X →L[ℝ] Y)
    (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y)
    (a b : coarseLane) :
    opBlock C (posteriorCovErrorOp K K0 H H0 P P0 R R0) a b = 0 ↔
      ∀ c d, ρ c = a → ρ d = b →
        (F.proj c).comp
          ((posteriorCovErrorOp K K0 H H0 P P0 R R0).comp (F.proj d)) = 0 := by
  exact opBlock_zero_iff_descendants_zero C F ρ hR
    (posteriorCovErrorOp K K0 H H0 P P0 R R0) a b

/-- Adaptive Bayesian refinement trigger: a coarse posterior covariance-error
corner is nonzero iff some fine descendant posterior-error corner is nonzero. -/
theorem posteriorCovError_opBlock_ne_zero_iff_exists_descendant
    (C : ProjectorFamily X coarseLane) (F : ProjectorFamily X fineLane)
    (ρ : fineLane → coarseLane) (hR : Refines C F ρ)
    (K K0 : Y →L[ℝ] X) (H H0 : X →L[ℝ] Y)
    (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y)
    (a b : coarseLane) :
    opBlock C (posteriorCovErrorOp K K0 H H0 P P0 R R0) a b ≠ 0 ↔
      ∃ c d, ρ c = a ∧ ρ d = b ∧
        (F.proj c).comp
          ((posteriorCovErrorOp K K0 H H0 P P0 R R0).comp (F.proj d)) ≠ 0 := by
  exact opBlock_ne_zero_iff_exists_descendant_ne_zero C F ρ hR
    (posteriorCovErrorOp K K0 H H0 P P0 R R0) a b

/-- Quantitative posterior refinement certificate: coarse posterior covariance
error is bounded by the sum of its fine descendant error-corner norms. -/
theorem posteriorCovError_opBlock_norm_le_descendantBudget
    (C : ProjectorFamily X coarseLane) (F : ProjectorFamily X fineLane)
    (ρ : fineLane → coarseLane) (hR : Refines C F ρ)
    (K K0 : Y →L[ℝ] X) (H H0 : X →L[ℝ] Y)
    (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y)
    (a b : coarseLane) :
    ‖opBlock C (posteriorCovErrorOp K K0 H H0 P P0 R R0) a b‖ ≤
      descendantNormBudget F ρ (posteriorCovErrorOp K K0 H H0 P P0 R R0) a b := by
  change ‖rawOpBlock C.proj (posteriorCovErrorOp K K0 H H0 P P0 R R0) a b‖ ≤ _
  exact rawOpBlock_norm_le_descendant_norm_sum C.proj F.proj ρ
    (Refines.coarse_eq_fine_sum hR)
    (posteriorCovErrorOp K K0 H H0 P P0 R R0) a b

omit [CompleteSpace X] [DecidableEq coarseLane] in
/-- A coarse corner formed by contractive projectors cannot exceed the global
operator norm. -/
theorem opBlock_norm_le_global_of_contractive
    (C : ProjectorFamily X coarseLane)
    (hC : ∀ a, ‖C.proj a‖ ≤ 1)
    (T : X →L[ℝ] X) (a b : coarseLane) :
    ‖opBlock C T a b‖ ≤ ‖T‖ := by
  unfold opBlock
  have h1 := ContinuousLinearMap.opNorm_comp_le (C.proj a) (T.comp (C.proj b))
  have h2 := ContinuousLinearMap.opNorm_comp_le T (C.proj b)
  calc
    ‖(C.proj a).comp (T.comp (C.proj b))‖ ≤
      ‖C.proj a‖ * ‖T.comp (C.proj b)‖ := h1
    _ ≤ ‖C.proj a‖ * (‖T‖ * ‖C.proj b‖) := by gcongr
    _ ≤ 1 * (‖T‖ * 1) := by
      gcongr
      · exact hC a
      · exact hC b
    _ = ‖T‖ := by ring

omit [DecidableEq coarseLane] in
/-- **End-to-end multiscale Bayesian posterior covariance certificate.**
Under actual innovation inverse equations, every coarse posterior covariance
error block is controlled by the global named-residual posterior budget. -/
theorem posteriorCovError_opBlock_norm_le_residual_budget
    (C : ProjectorFamily X coarseLane) (hC : ∀ a, ‖C.proj a‖ ≤ 1)
    (H H0 : X →L[ℝ] Y) (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y)
    (Sinv Sinv0 : Y →L[ℝ] Y)
    (hInv : Sinv.comp (kalmanInnovationOp H P R) = ContinuousLinearMap.id ℝ Y)
    (hInv0 : (kalmanInnovationOp H0 P0 R0).comp Sinv0 = ContinuousLinearMap.id ℝ Y)
    (a b : coarseLane) :
    let K := kalmanGainOp P H Sinv
    let K0 := kalmanGainOp P0 H0 Sinv0
    let gB := gainPerturbBudget H H0 P P0 R R0 Sinv Sinv0
    let aB := closedLoopPerturbBudget K0 H H0 gB
    ‖opBlock C (posteriorCovErrorOp K K0 H H0 P P0 R R0) a b‖ ≤
      posteriorCovPerturbBudget K K0 H H0 P P0 R R0 gB aB := by
  dsimp only
  let K := kalmanGainOp P H Sinv
  let K0 := kalmanGainOp P0 H0 Sinv0
  let gB := gainPerturbBudget H H0 P P0 R R0 Sinv Sinv0
  let aB := closedLoopPerturbBudget K0 H H0 gB
  have hblock : ‖opBlock C (posteriorCovErrorOp K K0 H H0 P P0 R R0) a b‖ ≤
      ‖posteriorCovErrorOp K K0 H H0 P P0 R R0‖ :=
    opBlock_norm_le_global_of_contractive C hC _ a b
  have hpost : ‖posteriorCovErrorOp K K0 H H0 P P0 R R0‖ ≤
      posteriorCovPerturbBudget K K0 H H0 P P0 R R0 gB aB := by
    dsimp [posteriorCovErrorOp, K, K0, gB, aB]
    exact josephPosteriorCov_sub_norm_le_residual_budget H H0 P P0 R R0 Sinv Sinv0 hInv hInv0
  exact hblock.trans hpost

end Komorebi.BayesianPosteriorPerturb
