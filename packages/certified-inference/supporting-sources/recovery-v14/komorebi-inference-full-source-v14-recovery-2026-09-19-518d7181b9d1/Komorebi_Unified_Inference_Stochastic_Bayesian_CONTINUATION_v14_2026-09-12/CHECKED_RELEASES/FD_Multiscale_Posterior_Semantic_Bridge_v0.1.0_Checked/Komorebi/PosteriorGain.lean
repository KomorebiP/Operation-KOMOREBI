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
public import Komorebi.PosteriorAlgebra
@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.BayesianPosteriorPerturb

universe uX2 uY2 uZ uW
variable {X : Type uX2} {Y : Type uY2} {Z : Type uZ} {W : Type uW}
variable [NormedAddCommGroup X] [InnerProductSpace ℝ X] [CompleteSpace X]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
variable [NormedAddCommGroup Z] [NormedSpace ℝ Z]
variable [NormedAddCommGroup W] [NormedSpace ℝ W]

omit [CompleteSpace X] [CompleteSpace Y] in
/-- Three-fold composition has the expected operator-norm product bound. -/
theorem norm_comp_comp_le
    (A : Z →L[ℝ] W) (B : Y →L[ℝ] Z) (C : X →L[ℝ] Y) :
    ‖A.comp (B.comp C)‖ ≤ ‖A‖ * ‖B‖ * ‖C‖ := by
  calc
    ‖A.comp (B.comp C)‖ ≤ ‖A‖ * ‖B.comp C‖ :=
      ContinuousLinearMap.opNorm_comp_le _ _
    _ ≤ ‖A‖ * (‖B‖ * ‖C‖) := by
      gcongr
      exact ContinuousLinearMap.opNorm_comp_le _ _
    _ = ‖A‖ * ‖B‖ * ‖C‖ := by rw [mul_assoc]

/-- Norm invariance of an adjoint difference. -/
theorem norm_adjoint_sub_eq
    (A B : X →L[ℝ] Y) :
    ‖A.adjoint - B.adjoint‖ = ‖A - B‖ := by
  have h := ContinuousLinearMap.adjoint.map_sub A B
  rw [← h]
  exact ContinuousLinearMap.adjoint.norm_map (A - B)

/-- Coordinate-free Kalman gain. -/
def kalmanGainOp
    (P : X →L[ℝ] X) (H : X →L[ℝ] Y) (Sinv : Y →L[ℝ] Y) : Y →L[ℝ] X :=
  P.comp (H.adjoint.comp Sinv)

/-- Exact three-term perturbation identity for the Kalman gain. -/
theorem kalmanGainOp_sub_exact
    (P P0 : X →L[ℝ] X) (H H0 : X →L[ℝ] Y)
    (Sinv Sinv0 : Y →L[ℝ] Y) :
    kalmanGainOp P H Sinv - kalmanGainOp P0 H0 Sinv0 =
      (P - P0).comp (H.adjoint.comp Sinv) +
      P0.comp ((H.adjoint - H0.adjoint).comp Sinv) +
      P0.comp (H0.adjoint.comp (Sinv - Sinv0)) := by
  ext y
  simp [kalmanGainOp, ContinuousLinearMap.comp_apply]

/-- Quantitative gain perturbation certificate. -/
theorem kalmanGainOp_sub_norm_le
    (P P0 : X →L[ℝ] X) (H H0 : X →L[ℝ] Y)
    (Sinv Sinv0 : Y →L[ℝ] Y) :
    ‖kalmanGainOp P H Sinv - kalmanGainOp P0 H0 Sinv0‖ ≤
      ‖P - P0‖ * ‖H‖ * ‖Sinv‖ +
      ‖P0‖ * ‖H - H0‖ * ‖Sinv‖ +
      ‖P0‖ * ‖H0‖ * ‖Sinv - Sinv0‖ := by
  rw [kalmanGainOp_sub_exact]
  have h1 := norm_comp_comp_le (P - P0) H.adjoint Sinv
  have h2 := norm_comp_comp_le P0 (H.adjoint - H0.adjoint) Sinv
  have h3 := norm_comp_comp_le P0 H0.adjoint (Sinv - Sinv0)
  rw [ContinuousLinearMap.adjoint.norm_map H] at h1
  rw [norm_adjoint_sub_eq H H0] at h2
  rw [ContinuousLinearMap.adjoint.norm_map H0] at h3
  let t1 := (P - P0).comp (H.adjoint.comp Sinv)
  let t2 := P0.comp ((H.adjoint - H0.adjoint).comp Sinv)
  let t3 := P0.comp (H0.adjoint.comp (Sinv - Sinv0))
  change ‖t1 + t2 + t3‖ ≤ _
  have ht1 : ‖t1‖ ≤ ‖P - P0‖ * ‖H‖ * ‖Sinv‖ := by simpa [t1] using h1
  have ht2 : ‖t2‖ ≤ ‖P0‖ * ‖H - H0‖ * ‖Sinv‖ := by simpa [t2] using h2
  have ht3 : ‖t3‖ ≤ ‖P0‖ * ‖H0‖ * ‖Sinv - Sinv0‖ := by simpa [t3] using h3
  calc
    ‖t1 + t2 + t3‖ ≤ ‖t1 + t2‖ + ‖t3‖ := norm_add_le _ _
    _ ≤ (‖t1‖ + ‖t2‖) + ‖t3‖ := add_le_add (norm_add_le _ _) le_rfl
    _ ≤ _ := add_le_add (add_le_add ht1 ht2) ht3

/-- Innovation covariance operator. -/
def kalmanInnovationOp
    (H : X →L[ℝ] Y) (P : X →L[ℝ] X) (R : Y →L[ℝ] Y) : Y →L[ℝ] Y :=
  H.comp (P.comp H.adjoint) + R

/-- Exact perturbation identity for the innovation covariance. -/
theorem kalmanInnovationOp_sub_exact
    (H H0 : X →L[ℝ] Y) (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y) :
    kalmanInnovationOp H P R - kalmanInnovationOp H0 P0 R0 =
      (H - H0).comp (P.comp H.adjoint) +
      H0.comp ((P - P0).comp H.adjoint) +
      H0.comp (P0.comp (H.adjoint - H0.adjoint)) +
      (R - R0) := by
  ext y
  simp [kalmanInnovationOp, ContinuousLinearMap.comp_apply]
  abel

/-- Quantitative innovation covariance perturbation certificate. -/
theorem kalmanInnovationOp_sub_norm_le
    (H H0 : X →L[ℝ] Y) (P P0 : X →L[ℝ] X) (R R0 : Y →L[ℝ] Y) :
    ‖kalmanInnovationOp H P R - kalmanInnovationOp H0 P0 R0‖ ≤
      ‖H - H0‖ * ‖P‖ * ‖H‖ +
      ‖H0‖ * ‖P - P0‖ * ‖H‖ +
      ‖H0‖ * ‖P0‖ * ‖H - H0‖ +
      ‖R - R0‖ := by
  rw [kalmanInnovationOp_sub_exact]
  have h1 := norm_comp_comp_le (H - H0) P H.adjoint
  have h2 := norm_comp_comp_le H0 (P - P0) H.adjoint
  have h3 := norm_comp_comp_le H0 P0 (H.adjoint - H0.adjoint)
  rw [ContinuousLinearMap.adjoint.norm_map H] at h1 h2
  rw [norm_adjoint_sub_eq H H0] at h3
  let t1 := (H - H0).comp (P.comp H.adjoint)
  let t2 := H0.comp ((P - P0).comp H.adjoint)
  let t3 := H0.comp (P0.comp (H.adjoint - H0.adjoint))
  let t4 := R - R0
  change ‖t1 + t2 + t3 + t4‖ ≤ _
  have ht1 : ‖t1‖ ≤ ‖H - H0‖ * ‖P‖ * ‖H‖ := by simpa [t1] using h1
  have ht2 : ‖t2‖ ≤ ‖H0‖ * ‖P - P0‖ * ‖H‖ := by simpa [t2] using h2
  have ht3 : ‖t3‖ ≤ ‖H0‖ * ‖P0‖ * ‖H - H0‖ := by simpa [t3] using h3
  calc
    ‖t1 + t2 + t3 + t4‖ ≤ ‖t1 + t2 + t3‖ + ‖t4‖ := norm_add_le _ _
    _ ≤ (‖t1 + t2‖ + ‖t3‖) + ‖t4‖ := add_le_add (norm_add_le _ _) le_rfl
    _ ≤ ((‖t1‖ + ‖t2‖) + ‖t3‖) + ‖t4‖ := by
      gcongr
      exact norm_add_le _ _
    _ ≤ _ := by
      have h123 := add_le_add (add_le_add ht1 ht2) ht3
      have h1234 := add_le_add h123 (le_refl ‖t4‖)
      simpa [t4] using h1234

end Komorebi.BayesianPosteriorPerturb
