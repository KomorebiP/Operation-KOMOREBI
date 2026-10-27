import Komorebi.FDJointPacking
import Komorebi.FDJointCovPSD

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

def forwardStateLift (H : Matrix κ ι ℝ) : Matrix (κ ⊕ ι) ι ℝ :=
  Matrix.fromRows H 1

def forwardNoiseLift : Matrix (κ ⊕ ι) κ ℝ := Matrix.fromRows 1 0

def reverseEvidenceLift (K : Matrix ι κ ℝ) : Matrix (κ ⊕ ι) κ ℝ :=
  Matrix.fromRows 1 K

def reverseResidualLift : Matrix (κ ⊕ ι) ι ℝ := Matrix.fromRows 0 1

omit [DecidableEq κ] in
@[simp] theorem forwardStateLift_apply (H : Matrix κ ι ℝ) (x : EuclideanSpace ℝ ι) :
    matrixCLM (forwardStateLift H) x = pack (matrixCLM H x,x) := by
  rw [forwardStateLift, matrixCLM_fromRows]
  simp

omit [DecidableEq ι] in
@[simp] theorem forwardNoiseLift_apply (z : EuclideanSpace ℝ κ) :
    matrixCLM (forwardNoiseLift (ι := ι)) z = pack (z,0) := by
  rw [forwardNoiseLift, matrixCLM_fromRows]
  simp

omit [DecidableEq ι] in
@[simp] theorem reverseEvidenceLift_apply (K : Matrix ι κ ℝ) (y : EuclideanSpace ℝ κ) :
    matrixCLM (reverseEvidenceLift K) y = pack (y,matrixCLM K y) := by
  rw [reverseEvidenceLift, matrixCLM_fromRows]
  simp

omit [DecidableEq κ] in
@[simp] theorem reverseResidualLift_apply (z : EuclideanSpace ℝ ι) :
    matrixCLM (reverseResidualLift (κ := κ)) z = pack (0,z) := by
  rw [reverseResidualLift, matrixCLM_fromRows]
  simp

/-- Covariance of vertically stacked linear maps. -/
theorem stacked_covariance
    {a b n : Type*} [Fintype n]
    (A : Matrix a n ℝ) (B : Matrix b n ℝ) (P : Matrix n n ℝ) :
    Matrix.fromRows A B * P * (Matrix.fromRows A B).transpose =
      Matrix.fromBlocks (A*P*A.transpose) (A*P*B.transpose)
        (B*P*A.transpose) (B*P*B.transpose) := by
  rw [Matrix.fromRows_mul A B P, Matrix.transpose_fromRows, Matrix.fromRows_mul_fromCols]

/-- The independent forward construction has exactly the checked block covariance. -/
theorem forward_lift_covariance
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) :
    forwardStateLift H * P * (forwardStateLift H).transpose +
        forwardNoiseLift * R * (forwardNoiseLift (ι := ι)).transpose =
      forwardJointCov H P R := by
  rw [forwardStateLift, forwardNoiseLift, stacked_covariance, stacked_covariance,
    Matrix.fromBlocks_add]
  simp [forwardJointCov, innovationMatrix]

/-- The independent reverse construction has exactly the checked block covariance. -/
theorem reverse_lift_covariance
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) :
    reverseEvidenceLift (gainMatrix H P R) * innovationMatrix H P R *
          (reverseEvidenceLift (gainMatrix H P R)).transpose +
        reverseResidualLift * posteriorCovMatrix H P R *
          (reverseResidualLift (κ := κ)).transpose =
      reverseJointCov H P R := by
  rw [reverseEvidenceLift, reverseResidualLift, stacked_covariance, stacked_covariance,
    Matrix.fromBlocks_add]
  simp [reverseJointCov]

end Komorebi.FiniteDimensionalGaussianKalman
