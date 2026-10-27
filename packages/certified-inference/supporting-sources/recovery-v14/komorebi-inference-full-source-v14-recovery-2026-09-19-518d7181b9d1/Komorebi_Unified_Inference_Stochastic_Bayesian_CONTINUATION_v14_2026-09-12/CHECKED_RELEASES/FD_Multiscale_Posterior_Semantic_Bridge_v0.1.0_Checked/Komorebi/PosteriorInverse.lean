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
public import Komorebi.PosteriorNorms
@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.BayesianPosteriorPerturb

universe uY4
variable {Y : Type uY4}
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]

omit [CompleteSpace Y] in
/-- Exact inverse perturbation identity from one left and one right inverse equation. -/
theorem inverse_sub_exact
    (S S0 Sinv Sinv0 : Y →L[ℝ] Y)
    (hInv : Sinv.comp S = ContinuousLinearMap.id ℝ Y)
    (hInv0 : S0.comp Sinv0 = ContinuousLinearMap.id ℝ Y) :
    Sinv - Sinv0 = Sinv.comp ((S0 - S).comp Sinv0) := by
  ext y
  have h1 := congrArg (fun T : Y →L[ℝ] Y => T (Sinv0 y)) hInv
  have h0 := congrArg (fun T : Y →L[ℝ] Y => T y) hInv0
  change Sinv (S (Sinv0 y)) = Sinv0 y at h1
  change S0 (Sinv0 y) = y at h0
  change Sinv y - Sinv0 y = Sinv (S0 (Sinv0 y) - S (Sinv0 y))
  rw [map_sub, h0, h1]

omit [CompleteSpace Y] in
/-- Standard inverse-conditioning bound. -/
theorem inverse_sub_norm_le
    (S S0 Sinv Sinv0 : Y →L[ℝ] Y)
    (hInv : Sinv.comp S = ContinuousLinearMap.id ℝ Y)
    (hInv0 : S0.comp Sinv0 = ContinuousLinearMap.id ℝ Y) :
    ‖Sinv - Sinv0‖ ≤ ‖Sinv‖ * ‖S - S0‖ * ‖Sinv0‖ := by
  rw [inverse_sub_exact S S0 Sinv Sinv0 hInv hInv0]
  have h := norm_comp_comp_le Sinv (S0 - S) Sinv0
  have hnorm : ‖S0 - S‖ = ‖S - S0‖ := by
    rw [← norm_neg (S - S0)]
    congr 1
    abel
  rw [hnorm] at h
  exact h

end Komorebi.BayesianPosteriorPerturb
