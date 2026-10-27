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
public import Komorebi.PosteriorGain
@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.BayesianPosteriorPerturb

universe uX3 uY3 uE
variable {X : Type uX3} {Y : Type uY3} {E : Type uE}
variable [NormedAddCommGroup X] [InnerProductSpace ℝ X] [CompleteSpace X]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
variable [NormedAddCommGroup E]

omit [NormedAddCommGroup X] [InnerProductSpace ℝ X] [CompleteSpace X]
  [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y] in
/-- Six-term triangle inequality, used to expose each posterior residual separately. -/
theorem norm_add_six_le (a b c d e f : E) :
    ‖a + b + c + d + e + f‖ ≤
      ‖a‖ + ‖b‖ + ‖c‖ + ‖d‖ + ‖e‖ + ‖f‖ := by
  calc
    ‖a + b + c + d + e + f‖ ≤ ‖a + b + c + d + e‖ + ‖f‖ := norm_add_le _ _
    _ ≤ (‖a + b + c + d‖ + ‖e‖) + ‖f‖ := add_le_add (norm_add_le _ _) le_rfl
    _ ≤ ((‖a + b + c‖ + ‖d‖) + ‖e‖) + ‖f‖ := by
      gcongr
      exact norm_add_le _ _
    _ ≤ (((‖a + b‖ + ‖c‖) + ‖d‖) + ‖e‖) + ‖f‖ := by
      gcongr
      exact norm_add_le _ _
    _ ≤ ((((‖a‖ + ‖b‖) + ‖c‖) + ‖d‖) + ‖e‖) + ‖f‖ := by
      gcongr
      exact norm_add_le _ _

omit [CompleteSpace X] [CompleteSpace Y] in
/-- Closed-loop correction error is controlled by gain and observation errors. -/
theorem kalmanClosedLoop_sub_norm_le
    (K K0 : Y →L[ℝ] X) (H H0 : X →L[ℝ] Y) :
    ‖kalmanClosedLoop K H - kalmanClosedLoop K0 H0‖ ≤
      ‖K - K0‖ * ‖H‖ + ‖K0‖ * ‖H - H0‖ := by
  rw [kalmanClosedLoop_sub, norm_neg]
  calc
    ‖(K - K0).comp H + K0.comp (H - H0)‖ ≤
      ‖(K - K0).comp H‖ + ‖K0.comp (H - H0)‖ := norm_add_le _ _
    _ ≤ ‖K - K0‖ * ‖H‖ + ‖K0‖ * ‖H - H0‖ :=
      add_le_add (ContinuousLinearMap.opNorm_comp_le _ _)
        (ContinuousLinearMap.opNorm_comp_le _ _)

/-- Raw posterior covariance perturbation bound in terms of closed-loop and gain errors. -/
theorem josephPosteriorCov_sub_norm_le
    (K K0 : Y →L[ℝ] X) (H H0 : X →L[ℝ] Y)
    (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y) :
    let A := kalmanClosedLoop K H
    let A0 := kalmanClosedLoop K0 H0
    ‖josephPosteriorCov K H P R - josephPosteriorCov K0 H0 P0 R0‖ ≤
      ‖A - A0‖ * ‖P‖ * ‖A‖ +
      ‖A0‖ * ‖P - P0‖ * ‖A‖ +
      ‖A0‖ * ‖P0‖ * ‖A - A0‖ +
      ‖K - K0‖ * ‖R‖ * ‖K‖ +
      ‖K0‖ * ‖R - R0‖ * ‖K‖ +
      ‖K0‖ * ‖R0‖ * ‖K - K0‖ := by
  dsimp only
  rw [josephPosteriorCov_sub_exact]
  let A := kalmanClosedLoop K H
  let A0 := kalmanClosedLoop K0 H0
  let t1 := (A - A0).comp (P.comp A.adjoint)
  let t2 := A0.comp ((P - P0).comp A.adjoint)
  let t3 := A0.comp (P0.comp (A.adjoint - A0.adjoint))
  let t4 := (K - K0).comp (R.comp K.adjoint)
  let t5 := K0.comp ((R - R0).comp K.adjoint)
  let t6 := K0.comp (R0.comp (K.adjoint - K0.adjoint))
  change ‖t1 + t2 + t3 + t4 + t5 + t6‖ ≤ _
  have h1 := norm_comp_comp_le (A - A0) P A.adjoint
  have h2 := norm_comp_comp_le A0 (P - P0) A.adjoint
  have h3 := norm_comp_comp_le A0 P0 (A.adjoint - A0.adjoint)
  have h4 := norm_comp_comp_le (K - K0) R K.adjoint
  have h5 := norm_comp_comp_le K0 (R - R0) K.adjoint
  have h6 := norm_comp_comp_le K0 R0 (K.adjoint - K0.adjoint)
  rw [ContinuousLinearMap.adjoint.norm_map A] at h1 h2
  rw [norm_adjoint_sub_eq A A0] at h3
  rw [ContinuousLinearMap.adjoint.norm_map K] at h4 h5
  rw [norm_adjoint_sub_eq K K0] at h6
  have ht1 : ‖t1‖ ≤ ‖A - A0‖ * ‖P‖ * ‖A‖ := by simpa [t1] using h1
  have ht2 : ‖t2‖ ≤ ‖A0‖ * ‖P - P0‖ * ‖A‖ := by simpa [t2] using h2
  have ht3 : ‖t3‖ ≤ ‖A0‖ * ‖P0‖ * ‖A - A0‖ := by simpa [t3] using h3
  have ht4 : ‖t4‖ ≤ ‖K - K0‖ * ‖R‖ * ‖K‖ := by simpa [t4] using h4
  have ht5 : ‖t5‖ ≤ ‖K0‖ * ‖R - R0‖ * ‖K‖ := by simpa [t5] using h5
  have ht6 : ‖t6‖ ≤ ‖K0‖ * ‖R0‖ * ‖K - K0‖ := by simpa [t6] using h6
  have htri := norm_add_six_le t1 t2 t3 t4 t5 t6
  exact htri.trans (add_le_add (add_le_add (add_le_add (add_le_add (add_le_add ht1 ht2) ht3) ht4) ht5) ht6)

end Komorebi.BayesianPosteriorPerturb
