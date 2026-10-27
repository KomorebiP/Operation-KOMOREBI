import Komorebi.FDForwardJointLaw
import Komorebi.FDPosteriorKernel

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix ProbabilityTheory MeasureTheory

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- The evidence/candidate-posterior joint is the reverse block Gaussian. -/
theorem reverse_joint_gaussian
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    ((multivariateGaussian (matrixCLM H m) (innovationMatrix H P R)) ⊗ₘ
        fdPosteriorKernel H m P R).map pack =
      multivariateGaussian (pack (matrixCLM H m,m)) (reverseJointCov H P R) := by
  let K := gainMatrix H P R
  let c := m - matrixCLM K (matrixCLM H m)
  have hS := (innovationMatrix_posDef H P R hP hR).posSemidef
  have hC := posteriorCovMatrix_posSemidef H P R hP hR
  rw [fdPosteriorKernel, compProd_gaussianAffineKernel _ _ _ _ hC,
    Measure.map_map (by fun_prop) (by fun_prop)]
  change ((multivariateGaussian (matrixCLM H m) (innovationMatrix H P R)).prod
      (multivariateGaussian 0 (posteriorCovMatrix H P R))).map
      (fun z => pack (z.1,c + matrixCLM K z.1 + z.2)) = _
  have hf : (fun z : EuclideanSpace ℝ κ × EuclideanSpace ℝ ι =>
      pack (z.1,c + matrixCLM K z.1 + z.2)) =
      fun z => pack (0,c) +
        (matrixCLM (reverseEvidenceLift K) z.1 + matrixCLM reverseResidualLift z.2) := by
    funext z
    rw [reverseEvidenceLift_apply, reverseResidualLift_apply, ← pack_add, ← pack_add]
    congr 1
    ext i <;> simp [add_assoc]
  rw [hf, multivariateGaussian_map_affine_product _ 0 _ _
      (reverseEvidenceLift K) reverseResidualLift (pack (0,c)) hS hC]
  rw [show reverseEvidenceLift K * innovationMatrix H P R *
        (reverseEvidenceLift K).transpose + reverseResidualLift * posteriorCovMatrix H P R *
        (reverseResidualLift (κ := κ)).transpose = reverseJointCov H P R from
      reverse_lift_covariance H P R]
  congr 1
  rw [map_zero, add_zero, reverseEvidenceLift_apply, ← pack_add]
  congr 1
  ext i <;> simp [c]

end Komorebi.FiniteDimensionalGaussianKalman
