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
public import Komorebi.PosteriorRefinementNorms
@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.BayesianPosteriorPerturb

universe uX uY
variable {X : Type uX} {Y : Type uY}
variable [NormedAddCommGroup X] [InnerProductSpace ℝ X] [CompleteSpace X]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]

/-- Closed-loop observation correction operator `I - K H`. -/
def kalmanClosedLoop (K : Y →L[ℝ] X) (H : X →L[ℝ] Y) : X →L[ℝ] X :=
  ContinuousLinearMap.id ℝ X - K.comp H

/-- Joseph-form posterior covariance as a coordinate-free bounded operator. -/
def josephPosteriorCov
    (K : Y →L[ℝ] X) (H : X →L[ℝ] Y)
    (P : X →L[ℝ] X) (R : Y →L[ℝ] Y) : X →L[ℝ] X :=
  let A := kalmanClosedLoop K H
  A.comp (P.comp A.adjoint) + K.comp (R.comp K.adjoint)

omit [CompleteSpace X] [CompleteSpace Y] in
/-- Exact residual identity for the closed-loop correction map. -/
theorem kalmanClosedLoop_sub
    (K K0 : Y →L[ℝ] X) (H H0 : X →L[ℝ] Y) :
    kalmanClosedLoop K H - kalmanClosedLoop K0 H0 =
      - ((K - K0).comp H + K0.comp (H - H0)) := by
  ext x
  simp [kalmanClosedLoop, ContinuousLinearMap.comp_apply]

/-- Exact three-term telescoping identity for the state/Joseph term. -/
theorem josephStateTerm_sub
    (A A0 P P0 : X →L[ℝ] X) :
    A.comp (P.comp A.adjoint) - A0.comp (P0.comp A0.adjoint) =
      (A - A0).comp (P.comp A.adjoint) +
      A0.comp ((P - P0).comp A.adjoint) +
      A0.comp (P0.comp (A.adjoint - A0.adjoint)) := by
  ext x
  simp [ContinuousLinearMap.comp_apply]

/-- Exact three-term telescoping identity for the observation-noise term. -/
theorem josephNoiseTerm_sub
    (K K0 : Y →L[ℝ] X) (R R0 : Y →L[ℝ] Y) :
    K.comp (R.comp K.adjoint) - K0.comp (R0.comp K0.adjoint) =
      (K - K0).comp (R.comp K.adjoint) +
      K0.comp ((R - R0).comp K.adjoint) +
      K0.comp (R0.comp (K.adjoint - K0.adjoint)) := by
  ext x
  simp [ContinuousLinearMap.comp_apply]

/-- Exact six-term posterior covariance perturbation identity. -/
theorem josephPosteriorCov_sub_exact
    (K K0 : Y →L[ℝ] X) (H H0 : X →L[ℝ] Y)
    (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y) :
    let A := kalmanClosedLoop K H
    let A0 := kalmanClosedLoop K0 H0
    josephPosteriorCov K H P R - josephPosteriorCov K0 H0 P0 R0 =
      (A - A0).comp (P.comp A.adjoint) +
      A0.comp ((P - P0).comp A.adjoint) +
      A0.comp (P0.comp (A.adjoint - A0.adjoint)) +
      (K - K0).comp (R.comp K.adjoint) +
      K0.comp ((R - R0).comp K.adjoint) +
      K0.comp (R0.comp (K.adjoint - K0.adjoint)) := by
  dsimp only
  unfold josephPosteriorCov
  dsimp only
  rw [sub_eq_iff_eq_add]
  -- split the two Joseph summands and use the exact telescoping identities
  have hs := josephStateTerm_sub (kalmanClosedLoop K H) (kalmanClosedLoop K0 H0) P P0
  have hn := josephNoiseTerm_sub K K0 R R0
  -- rearrange the two exact differences
  rw [sub_eq_iff_eq_add] at hs hn
  rw [hs, hn]
  abel

end Komorebi.BayesianPosteriorPerturb
