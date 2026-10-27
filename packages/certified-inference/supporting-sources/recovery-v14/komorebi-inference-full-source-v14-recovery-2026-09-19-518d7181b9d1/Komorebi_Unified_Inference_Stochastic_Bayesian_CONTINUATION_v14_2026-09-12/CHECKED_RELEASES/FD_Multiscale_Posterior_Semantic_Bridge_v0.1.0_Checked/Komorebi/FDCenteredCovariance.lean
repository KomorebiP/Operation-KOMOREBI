import Komorebi.FDGaussianTransport

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix ProbabilityTheory MeasureTheory InnerProductSpace
open scoped RealInnerProductSpace

section General
variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
  [CompleteSpace E] [MeasurableSpace E] [BorelSpace E]

/-- The centered covariance operator, defined from the probability covariance form.
This definition does not use a supplied covariance matrix or a Kalman formula. -/
def centeredCovOp (μ : Measure E) : E →L[ℝ] E :=
  continuousLinearMapOfBilin (covarianceBilin μ)

/-- The centered operator represents the centered probability bilinear form. -/
theorem centeredCovOp_inner (μ : Measure E) (x y : E) :
    ⟪centeredCovOp μ x, y⟫ = covarianceBilin μ x y := by
  exact continuousLinearMapOfBilin_apply (covarianceBilin μ) x y

/-- Explicit centered-integral semantics, with the second-moment hypothesis retained. -/
theorem centeredCovOp_inner_integral (μ : Measure E) [IsFiniteMeasure μ]
    (hμ : MemLp id 2 μ) (x y : E) :
    ⟪centeredCovOp μ x, y⟫ =
      ∫ z, ⟪x, z - μ[id]⟫ * ⟪y, z - μ[id]⟫ ∂μ := by
  rw [centeredCovOp_inner, covarianceBilin_apply hμ]

/-- Equality of centered covariance forms gives equality of centered operators. -/
theorem centeredCovOp_congr {μ ν : Measure E}
    (h : covarianceBilin μ = covarianceBilin ν) : centeredCovOp μ = centeredCovOp ν := by
  unfold centeredCovOp
  rw [h]

/-- Translating a probability measure does not change its centered covariance. -/
theorem centeredCovOp_map_const_add (μ : Measure E) [IsProbabilityMeasure μ] (c : E) :
    centeredCovOp (μ.map (fun x => c + x)) = centeredCovOp μ := by
  exact centeredCovOp_congr (covarianceBilin_map_const_add c)

end General

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- A Gaussian measure's actual centered covariance operator is its covariance matrix
acting on the Euclidean space. Singular positive semidefinite covariance is permitted. -/
theorem centeredCovOp_multivariateGaussian
    (m : EuclideanSpace ℝ ι) (P : Matrix ι ι ℝ) (hP : P.PosSemidef) :
    centeredCovOp (multivariateGaussian m P) = matrixCLM P := by
  apply ContinuousLinearMap.ext
  intro x
  apply (unique_continuousLinearMapOfBilin (covarianceBilin (multivariateGaussian m P)) ?_).symm
  intro y
  rw [covarianceBilin_comm, covarianceBilin_multivariateGaussian hP]
  simp only [matrixCLM_apply, EuclideanSpace.inner_eq_star_dotProduct,
    star_trivial]

end Komorebi.FiniteDimensionalGaussianKalman
