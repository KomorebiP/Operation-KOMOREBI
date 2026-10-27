import Komorebi.FDGaussianTransport

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix ProbabilityTheory MeasureTheory
open scoped RealInnerProductSpace Matrix

/-- Independent Gaussian sums, including positive-semidefinite singular covariances. -/
theorem multivariateGaussian_conv
    {ι : Type*} [Fintype ι] [DecidableEq ι]
    (m n : EuclideanSpace ℝ ι) (P Q : Matrix ι ι ℝ)
    (hP : P.PosSemidef) (hQ : Q.PosSemidef) :
    (multivariateGaussian m P) ∗ (multivariateGaussian n Q) =
      multivariateGaussian (m+n) (P+Q) := by
  apply Measure.ext_of_charFun
  ext t
  rw [charFun_conv, charFun_multivariateGaussian hP, charFun_multivariateGaussian hQ,
    charFun_multivariateGaussian (hP.add hQ), ← Complex.exp_add]
  congr 1
  simp only [inner_add_right, Matrix.add_mulVec, dotProduct_add, Complex.ofReal_add]
  ring

/-- A joint independent input mapped by two rectangular matrices has the sum covariance. -/
theorem multivariateGaussian_map_linear_product
    {ι κ η : Type*} [Fintype ι] [Fintype κ] [Fintype η]
    [DecidableEq ι] [DecidableEq κ] [DecidableEq η]
    (m : EuclideanSpace ℝ ι) (n : EuclideanSpace ℝ κ)
    (P : Matrix ι ι ℝ) (Q : Matrix κ κ ℝ)
    (A : Matrix η ι ℝ) (B : Matrix η κ ℝ)
    (hP : P.PosSemidef) (hQ : Q.PosSemidef) :
    ((multivariateGaussian m P).prod (multivariateGaussian n Q)).map
      (fun z => matrixCLM A z.1 + matrixCLM B z.2) =
      multivariateGaussian (matrixCLM A m + matrixCLM B n)
        (A*P*A.transpose + B*Q*B.transpose) := by
  have hm :
      ((multivariateGaussian m P).prod (multivariateGaussian n Q)).map
          (fun z => matrixCLM A z.1 + matrixCLM B z.2) =
        ((multivariateGaussian m P).map (matrixCLM A)) ∗
          ((multivariateGaussian n Q).map (matrixCLM B)) := by
    rw [Measure.conv, Measure.map_prod_map _ _ (by fun_prop) (by fun_prop),
      Measure.map_map (by fun_prop) (by fun_prop)]
    rfl
  rw [hm, multivariateGaussian_map_matrixCLM A m P hP,
    multivariateGaussian_map_matrixCLM B n Q hQ,
    multivariateGaussian_conv _ _ _ _ (imageCov_posSemidef A P hP)
      (imageCov_posSemidef B Q hQ)]

/-- The affine version of independent Gaussian linear transport. -/
theorem multivariateGaussian_map_affine_product
    {ι κ η : Type*} [Fintype ι] [Fintype κ] [Fintype η]
    [DecidableEq ι] [DecidableEq κ] [DecidableEq η]
    (m : EuclideanSpace ℝ ι) (n : EuclideanSpace ℝ κ)
    (P : Matrix ι ι ℝ) (Q : Matrix κ κ ℝ)
    (A : Matrix η ι ℝ) (B : Matrix η κ ℝ) (c : EuclideanSpace ℝ η)
    (hP : P.PosSemidef) (hQ : Q.PosSemidef) :
    ((multivariateGaussian m P).prod (multivariateGaussian n Q)).map
      (fun z => c + (matrixCLM A z.1 + matrixCLM B z.2)) =
      multivariateGaussian (c + (matrixCLM A m + matrixCLM B n))
        (A*P*A.transpose + B*Q*B.transpose) := by
  change ((multivariateGaussian m P).prod (multivariateGaussian n Q)).map
      ((fun x => c+x) ∘ (fun z => matrixCLM A z.1 + matrixCLM B z.2)) = _
  rw [← Measure.map_map (by fun_prop) (by fun_prop),
    multivariateGaussian_map_linear_product m n P Q A B hP hQ,
    multivariateGaussian_map_const_add _ _ _
      ((imageCov_posSemidef A P hP).add (imageCov_posSemidef B Q hQ))]

end Komorebi.FiniteDimensionalGaussianKalman
