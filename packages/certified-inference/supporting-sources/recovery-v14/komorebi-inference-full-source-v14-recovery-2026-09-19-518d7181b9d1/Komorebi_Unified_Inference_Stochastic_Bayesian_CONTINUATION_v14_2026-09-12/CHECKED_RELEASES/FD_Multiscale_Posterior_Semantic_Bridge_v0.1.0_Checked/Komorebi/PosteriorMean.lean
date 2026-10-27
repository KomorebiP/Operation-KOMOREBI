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
public import Komorebi.PosteriorBudgets
@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.BayesianPosteriorPerturb

universe uX6 uY6
variable {X : Type uX6} {Y : Type uY6}
variable [NormedAddCommGroup X] [InnerProductSpace ℝ X] [CompleteSpace X]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]

/-- Coordinate-free Kalman posterior mean update. -/
def kalmanPosteriorMean
    (K : Y →L[ℝ] X) (H : X →L[ℝ] Y) (m : X) (y : Y) : X :=
  m + K (y - H m)

omit [CompleteSpace X] [CompleteSpace Y] in
/-- Exact posterior-mean residual identity. -/
theorem kalmanPosteriorMean_sub_exact
    (K K0 : Y →L[ℝ] X) (H H0 : X →L[ℝ] Y)
    (m m0 : X) (y y0 : Y) :
    kalmanPosteriorMean K H m y - kalmanPosteriorMean K0 H0 m0 y0 =
      (m - m0) +
      (K - K0) (y - H m) +
      K0 ((y - y0) - (H - H0) m - H0 (m - m0)) := by
  simp [kalmanPosteriorMean]
  abel

omit [CompleteSpace X] [CompleteSpace Y] in
/-- Posterior mean perturbation bound in terms of gain, observation-model,
state-prior, and observed-data residuals. -/
theorem kalmanPosteriorMean_sub_norm_le
    (K K0 : Y →L[ℝ] X) (H H0 : X →L[ℝ] Y)
    (m m0 : X) (y y0 : Y) :
    ‖kalmanPosteriorMean K H m y - kalmanPosteriorMean K0 H0 m0 y0‖ ≤
      ‖m - m0‖ +
      ‖K - K0‖ * ‖y - H m‖ +
      ‖K0‖ * (‖y - y0‖ + ‖H - H0‖ * ‖m‖ + ‖H0‖ * ‖m - m0‖) := by
  rw [kalmanPosteriorMean_sub_exact]
  let dm := m - m0
  let innov := y - H m
  let corr := (y - y0) - (H - H0) m - H0 (m - m0)
  change ‖dm + (K - K0) innov + K0 corr‖ ≤ _
  have hk : ‖(K - K0) innov‖ ≤ ‖K - K0‖ * ‖innov‖ :=
    ContinuousLinearMap.le_opNorm (K - K0) innov
  have hk0 : ‖K0 corr‖ ≤ ‖K0‖ * ‖corr‖ :=
    ContinuousLinearMap.le_opNorm K0 corr
  have hDH : ‖(H - H0) m‖ ≤ ‖H - H0‖ * ‖m‖ :=
    ContinuousLinearMap.le_opNorm (H - H0) m
  have hH0 : ‖H0 (m - m0)‖ ≤ ‖H0‖ * ‖m - m0‖ :=
    ContinuousLinearMap.le_opNorm H0 (m - m0)
  have hcorr : ‖corr‖ ≤ ‖y - y0‖ + ‖H - H0‖ * ‖m‖ + ‖H0‖ * ‖m - m0‖ := by
    dsimp [corr]
    calc
      ‖(y - y0) - (H - H0) m - H0 (m - m0)‖ ≤
        ‖(y - y0) - (H - H0) m‖ + ‖H0 (m - m0)‖ := norm_sub_le _ _
      _ ≤ (‖y - y0‖ + ‖(H - H0) m‖) + ‖H0 (m - m0)‖ :=
        add_le_add (norm_sub_le _ _) le_rfl
      _ ≤ _ := add_le_add (add_le_add le_rfl hDH) hH0
  calc
    ‖dm + (K - K0) innov + K0 corr‖ ≤ ‖dm + (K - K0) innov‖ + ‖K0 corr‖ := norm_add_le _ _
    _ ≤ (‖dm‖ + ‖(K - K0) innov‖) + ‖K0 corr‖ := add_le_add (norm_add_le _ _) le_rfl
    _ ≤ (‖dm‖ + ‖K - K0‖ * ‖innov‖) + ‖K0‖ * ‖corr‖ :=
      add_le_add (add_le_add le_rfl hk) hk0
    _ ≤ _ := by
      dsimp [dm, innov]
      gcongr

/-- End-to-end posterior-mean perturbation theorem using the derived gain budget. -/
theorem kalmanPosteriorMean_sub_norm_le_residual_budget
    (H H0 : X →L[ℝ] Y) (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y)
    (Sinv Sinv0 : Y →L[ℝ] Y)
    (m m0 : X) (y y0 : Y)
    (hInv : Sinv.comp (kalmanInnovationOp H P R) = ContinuousLinearMap.id ℝ Y)
    (hInv0 : (kalmanInnovationOp H0 P0 R0).comp Sinv0 = ContinuousLinearMap.id ℝ Y) :
    let K := kalmanGainOp P H Sinv
    let K0 := kalmanGainOp P0 H0 Sinv0
    let gB := gainPerturbBudget H H0 P P0 R R0 Sinv Sinv0
    ‖kalmanPosteriorMean K H m y - kalmanPosteriorMean K0 H0 m0 y0‖ ≤
      ‖m - m0‖ +
      gB * ‖y - H m‖ +
      ‖K0‖ * (‖y - y0‖ + ‖H - H0‖ * ‖m‖ + ‖H0‖ * ‖m - m0‖) := by
  dsimp only
  let K := kalmanGainOp P H Sinv
  let K0 := kalmanGainOp P0 H0 Sinv0
  let gB := gainPerturbBudget H H0 P P0 R R0 Sinv Sinv0
  have hm := kalmanPosteriorMean_sub_norm_le K K0 H H0 m m0 y y0
  have hk : ‖K - K0‖ ≤ gB := by
    dsimp [K, K0, gB]
    exact kalmanGainOp_sub_norm_le_residual_budget H H0 P P0 R R0 Sinv Sinv0 hInv hInv0
  exact hm.trans (by gcongr)

end Komorebi.BayesianPosteriorPerturb
