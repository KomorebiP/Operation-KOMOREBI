import Komorebi.FDGaussianSum
import Komorebi.FDGaussianKernel
import Komorebi.FDJointLiftAlgebra

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix ProbabilityTheory MeasureTheory

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- The actual prior/likelihood joint, ordered as observation then state, is Gaussian. -/
theorem forward_joint_gaussian
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosSemidef) :
    (((multivariateGaussian m P) ⊗ₘ gaussianAffineKernel H 0 R).map Prod.swap).map pack =
      multivariateGaussian (pack (matrixCLM H m,m)) (forwardJointCov H P R) := by
  rw [compProd_gaussianAffineKernel _ H 0 R hR,
    Measure.map_map (by fun_prop) (by fun_prop),
    Measure.map_map (by fun_prop) (by fun_prop)]
  change ((multivariateGaussian m P).prod (multivariateGaussian 0 R)).map
      (fun z => pack (0 + matrixCLM H z.1 + z.2,z.1)) = _
  simp only [zero_add]
  have hf : (fun z : EuclideanSpace ℝ ι × EuclideanSpace ℝ κ =>
      pack (matrixCLM H z.1 + z.2,z.1)) =
      fun z => matrixCLM (forwardStateLift H) z.1 + matrixCLM forwardNoiseLift z.2 := by
    funext z
    rw [forwardStateLift_apply, forwardNoiseLift_apply, ← pack_add]
    congr 1
    simp
  rw [hf, multivariateGaussian_map_linear_product m 0 P R
    (forwardStateLift H) forwardNoiseLift hP hR,
    forward_lift_covariance, forwardStateLift_apply, map_zero, add_zero]

end Komorebi.FiniteDimensionalGaussianKalman
