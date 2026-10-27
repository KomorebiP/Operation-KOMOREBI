import Mathlib.Probability.Distributions.Gaussian.Multivariate

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix ProbabilityTheory MeasureTheory
open scoped RealInnerProductSpace Matrix

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- Rectangular matrices acting on Euclidean coordinate spaces. -/
def matrixCLM (A : Matrix κ ι ℝ) : EuclideanSpace ℝ ι →L[ℝ] EuclideanSpace ℝ κ :=
  A.toEuclideanLin.toContinuousLinearMap

omit [DecidableEq κ] in
@[simp] theorem matrixCLM_apply (A : Matrix κ ι ℝ) (x : EuclideanSpace ℝ ι) :
    matrixCLM A x = WithLp.toLp 2 (A *ᵥ x) := rfl

@[simp] theorem matrixCLM_adjoint (A : Matrix κ ι ℝ) :
    (matrixCLM A).adjoint = matrixCLM A.transpose := by
  symm
  apply (ContinuousLinearMap.eq_adjoint_iff _ _).2
  intro x y
  simp only [matrixCLM_apply, EuclideanSpace.inner_eq_star_dotProduct,
    star_trivial]
  rw [Matrix.dotProduct_mulVec, Matrix.vecMul_transpose]

omit [DecidableEq ι] [DecidableEq κ] in
/-- A rectangular image covariance is positive semidefinite. -/
theorem imageCov_posSemidef (A : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (hP : P.PosSemidef) : (A * P * A.transpose).PosSemidef := by
  simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using
    hP.mul_mul_conjTranspose_same A

/-- Exact Gaussian pushforward by an arbitrary rectangular linear map. -/
theorem multivariateGaussian_map_matrixCLM
    (A : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι) (P : Matrix ι ι ℝ)
    (hP : P.PosSemidef) :
    (multivariateGaussian m P).map (matrixCLM A) =
      multivariateGaussian (matrixCLM A m) (A * P * A.transpose) := by
  apply IsGaussian.ext
  · simp only [id_eq]
    rw [ContinuousLinearMap.integral_id_map]
    · simp
    · exact IsGaussian.integrable_id
  · ext x y
    rw [covarianceBilin_map IsGaussian.memLp_two_id,
      matrixCLM_adjoint, covarianceBilin_multivariateGaussian hP,
      covarianceBilin_multivariateGaussian (imageCov_posSemidef A P hP)]
    simp only [matrixCLM_apply, WithLp.ofLp_toLp]
    rw [Matrix.mulVec_transpose]
    simp only [Matrix.mulVec_mulVec, Matrix.dotProduct_mulVec, Matrix.vecMul_vecMul, Matrix.mul_assoc]

/-- Translations change the Gaussian mean but not its covariance. -/
theorem multivariateGaussian_map_const_add
    (c m : EuclideanSpace ℝ ι) (P : Matrix ι ι ℝ) (hP : P.PosSemidef) :
    (multivariateGaussian m P).map (fun x => c + x) = multivariateGaussian (c+m) P := by
  apply IsGaussian.ext
  · simp only [id_eq]
    rw [integral_map (by fun_prop) (by fun_prop),
      integral_add (integrable_const _) IsGaussian.integrable_fun_id]
    simp
  · rw [covarianceBilin_map_const_add]
    ext x y
    rw [covarianceBilin_multivariateGaussian hP, covarianceBilin_multivariateGaussian hP]

end Komorebi.FiniteDimensionalGaussianKalman
