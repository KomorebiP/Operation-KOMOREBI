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
public import Komorebi.PosteriorInverse
@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.BayesianPosteriorPerturb

universe uX5 uY5
variable {X : Type uX5} {Y : Type uY5}
variable [NormedAddCommGroup X] [InnerProductSpace ℝ X] [CompleteSpace X]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]

/-- Explicit observation/innovation perturbation budget. -/
def innovationPerturbBudget
    (H H0 : X →L[ℝ] Y) (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y) : ℝ :=
  ‖H - H0‖ * ‖P‖ * ‖H‖ +
  ‖H0‖ * ‖P - P0‖ * ‖H‖ +
  ‖H0‖ * ‖P0‖ * ‖H - H0‖ +
  ‖R - R0‖

/-- Gain perturbation budget after propagating innovation error through inverse conditioning. -/
def gainPerturbBudget
    (H H0 : X →L[ℝ] Y) (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y)
    (Sinv Sinv0 : Y →L[ℝ] Y) : ℝ :=
  ‖P - P0‖ * ‖H‖ * ‖Sinv‖ +
  ‖P0‖ * ‖H - H0‖ * ‖Sinv‖ +
  ‖P0‖ * ‖H0‖ *
    (‖Sinv‖ * innovationPerturbBudget H H0 P P0 R R0 * ‖Sinv0‖)

/-- Closed-loop correction budget induced by the gain and observation residuals. -/
def closedLoopPerturbBudget
    (K0 : Y →L[ℝ] X) (H H0 : X →L[ℝ] Y) (gainBudget : ℝ) : ℝ :=
  gainBudget * ‖H‖ + ‖K0‖ * ‖H - H0‖

/-- End-to-end Joseph posterior covariance perturbation budget. -/
def posteriorCovPerturbBudget
    (K K0 : Y →L[ℝ] X) (H H0 : X →L[ℝ] Y)
    (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y)
    (gainBudget closedBudget : ℝ) : ℝ :=
  let A := kalmanClosedLoop K H
  let A0 := kalmanClosedLoop K0 H0
  closedBudget * ‖P‖ * ‖A‖ +
  ‖A0‖ * ‖P - P0‖ * ‖A‖ +
  ‖A0‖ * ‖P0‖ * closedBudget +
  gainBudget * ‖R‖ * ‖K‖ +
  ‖K0‖ * ‖R - R0‖ * ‖K‖ +
  ‖K0‖ * ‖R0‖ * gainBudget

/-- Innovation covariance error is bounded by the named observation residual budget. -/
theorem kalmanInnovationOp_sub_norm_le_budget
    (H H0 : X →L[ℝ] Y) (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y) :
    ‖kalmanInnovationOp H P R - kalmanInnovationOp H0 P0 R0‖ ≤
      innovationPerturbBudget H H0 P P0 R R0 := by
  exact kalmanInnovationOp_sub_norm_le H H0 P P0 R R0

/-- Gain error driven all the way back to prior/observation/noise residuals and inverse conditioning. -/
theorem kalmanGainOp_sub_norm_le_residual_budget
    (H H0 : X →L[ℝ] Y) (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y)
    (Sinv Sinv0 : Y →L[ℝ] Y)
    (hInv : Sinv.comp (kalmanInnovationOp H P R) = ContinuousLinearMap.id ℝ Y)
    (hInv0 : (kalmanInnovationOp H0 P0 R0).comp Sinv0 = ContinuousLinearMap.id ℝ Y) :
    ‖kalmanGainOp P H Sinv - kalmanGainOp P0 H0 Sinv0‖ ≤
      gainPerturbBudget H H0 P P0 R R0 Sinv Sinv0 := by
  let S := kalmanInnovationOp H P R
  let S0 := kalmanInnovationOp H0 P0 R0
  have hg := kalmanGainOp_sub_norm_le P P0 H H0 Sinv Sinv0
  have hi := inverse_sub_norm_le S S0 Sinv Sinv0 hInv hInv0
  have hs := kalmanInnovationOp_sub_norm_le_budget H H0 P P0 R R0
  unfold gainPerturbBudget
  calc
    ‖kalmanGainOp P H Sinv - kalmanGainOp P0 H0 Sinv0‖ ≤
      ‖P - P0‖ * ‖H‖ * ‖Sinv‖ +
      ‖P0‖ * ‖H - H0‖ * ‖Sinv‖ +
      ‖P0‖ * ‖H0‖ * ‖Sinv - Sinv0‖ := hg
    _ ≤ ‖P - P0‖ * ‖H‖ * ‖Sinv‖ +
      ‖P0‖ * ‖H - H0‖ * ‖Sinv‖ +
      ‖P0‖ * ‖H0‖ * (‖Sinv‖ * ‖S - S0‖ * ‖Sinv0‖) := by
        gcongr
    _ ≤ ‖P - P0‖ * ‖H‖ * ‖Sinv‖ +
      ‖P0‖ * ‖H - H0‖ * ‖Sinv‖ +
      ‖P0‖ * ‖H0‖ *
        (‖Sinv‖ * innovationPerturbBudget H H0 P P0 R R0 * ‖Sinv0‖) := by
        dsimp [S, S0] at hs ⊢
        gcongr

/-- Closed-loop error inherits the end-to-end residual gain budget. -/
theorem kalmanClosedLoop_sub_norm_le_residual_budget
    (H H0 : X →L[ℝ] Y) (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y)
    (Sinv Sinv0 : Y →L[ℝ] Y)
    (hInv : Sinv.comp (kalmanInnovationOp H P R) = ContinuousLinearMap.id ℝ Y)
    (hInv0 : (kalmanInnovationOp H0 P0 R0).comp Sinv0 = ContinuousLinearMap.id ℝ Y) :
    let K := kalmanGainOp P H Sinv
    let K0 := kalmanGainOp P0 H0 Sinv0
    ‖kalmanClosedLoop K H - kalmanClosedLoop K0 H0‖ ≤
      closedLoopPerturbBudget K0 H H0
        (gainPerturbBudget H H0 P P0 R R0 Sinv Sinv0) := by
  dsimp only
  have hA := kalmanClosedLoop_sub_norm_le
    (kalmanGainOp P H Sinv) (kalmanGainOp P0 H0 Sinv0) H H0
  have hK := kalmanGainOp_sub_norm_le_residual_budget H H0 P P0 R R0 Sinv Sinv0 hInv hInv0
  unfold closedLoopPerturbBudget
  exact hA.trans (by gcongr)

/-- **End-to-end linear-Gaussian/Kalman posterior covariance perturbation theorem.**
The posterior covariance error is bounded solely by named prior covariance,
observation-operator, observation-noise residuals and the actual inverse
conditioning factors of the two innovation operators. -/
theorem josephPosteriorCov_sub_norm_le_residual_budget
    (H H0 : X →L[ℝ] Y) (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y)
    (Sinv Sinv0 : Y →L[ℝ] Y)
    (hInv : Sinv.comp (kalmanInnovationOp H P R) = ContinuousLinearMap.id ℝ Y)
    (hInv0 : (kalmanInnovationOp H0 P0 R0).comp Sinv0 = ContinuousLinearMap.id ℝ Y) :
    let K := kalmanGainOp P H Sinv
    let K0 := kalmanGainOp P0 H0 Sinv0
    let gB := gainPerturbBudget H H0 P P0 R R0 Sinv Sinv0
    let aB := closedLoopPerturbBudget K0 H H0 gB
    ‖josephPosteriorCov K H P R - josephPosteriorCov K0 H0 P0 R0‖ ≤
      posteriorCovPerturbBudget K K0 H H0 P P0 R R0 gB aB := by
  dsimp only
  let K := kalmanGainOp P H Sinv
  let K0 := kalmanGainOp P0 H0 Sinv0
  let gB := gainPerturbBudget H H0 P P0 R R0 Sinv Sinv0
  let aB := closedLoopPerturbBudget K0 H H0 gB
  let A := kalmanClosedLoop K H
  let A0 := kalmanClosedLoop K0 H0
  have hraw := josephPosteriorCov_sub_norm_le K K0 H H0 P P0 R R0
  have hK : ‖K - K0‖ ≤ gB := by
    dsimp [K, K0, gB]
    exact kalmanGainOp_sub_norm_le_residual_budget H H0 P P0 R R0 Sinv Sinv0 hInv hInv0
  have hA : ‖A - A0‖ ≤ aB := by
    dsimp [A, A0, aB, K, K0, gB]
    exact kalmanClosedLoop_sub_norm_le_residual_budget H H0 P P0 R R0 Sinv Sinv0 hInv hInv0
  dsimp [posteriorCovPerturbBudget, A, A0] at hraw ⊢
  exact hraw.trans (by
    gcongr)

end Komorebi.BayesianPosteriorPerturb
