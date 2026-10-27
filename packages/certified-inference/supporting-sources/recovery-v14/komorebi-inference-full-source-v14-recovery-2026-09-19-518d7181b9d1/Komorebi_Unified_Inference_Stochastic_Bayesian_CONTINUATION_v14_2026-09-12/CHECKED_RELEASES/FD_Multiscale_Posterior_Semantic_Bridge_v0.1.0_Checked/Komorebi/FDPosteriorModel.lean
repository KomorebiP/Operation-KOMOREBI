import Komorebi.FDGaussianConditioning
import Komorebi.FDKalmanOperatorBridge
import Komorebi.FDCenteredCovariance

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix ProbabilityTheory MeasureTheory Komorebi.BayesianPosteriorPerturb

/-- A finite-dimensional linear-Gaussian model with explicit validity hypotheses. -/
structure GaussianModel (ι κ : Type*) [Fintype ι] [Fintype κ] where
  mean : EuclideanSpace ℝ ι
  priorCov : Matrix ι ι ℝ
  observation : Matrix κ ι ℝ
  noiseCov : Matrix κ κ ℝ
  prior_valid : priorCov.PosSemidef
  noise_valid : noiseCov.PosDef

namespace GaussianModel
variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

def priorOp (M : GaussianModel ι κ) := matrixCLM M.priorCov
def observationOp (M : GaussianModel ι κ) := matrixCLM M.observation
def noiseOp (M : GaussianModel ι κ) := matrixCLM M.noiseCov
def inverseInnovationOp (M : GaussianModel ι κ) :=
  matrixCLM (innovationMatrix M.observation M.priorCov M.noiseCov)⁻¹
def gainOp (M : GaussianModel ι κ) :=
  matrixCLM (gainMatrix M.observation M.priorCov M.noiseCov)

/-- The everywhere-defined explicit posterior version supplied by disintegration. -/
def posteriorLaw (M : GaussianModel ι κ) (y : EuclideanSpace ℝ κ) :
    Measure (EuclideanSpace ℝ ι) :=
  fdPosteriorKernel M.observation M.mean M.priorCov M.noiseCov y

/-- The actual observation law, already identified with the likelihood/prior marginal. -/
def evidenceLaw (M : GaussianModel ι κ) : Measure (EuclideanSpace ℝ κ) :=
  multivariateGaussian (M.observationOp M.mean)
    (innovationMatrix M.observation M.priorCov M.noiseCov)

/-- Mathlib's selected conditional kernel for this model. -/
def canonicalKernel (M : GaussianModel ι κ) :
    Kernel (EuclideanSpace ℝ κ) (EuclideanSpace ℝ ι) :=
  posterior (gaussianAffineKernel M.observation 0 M.noiseCov)
    (multivariateGaussian M.mean M.priorCov)

/-- No law identity is assumed by the model record. It is inherited from disintegration. -/
theorem posteriorLaw_ae_eq_canonical (M : GaussianModel ι κ) :
    M.posteriorLaw =ᵐ[M.evidenceLaw] M.canonicalKernel := by
  exact fdPosteriorKernel_eq_canonical M.observation M.mean M.priorCov M.noiseCov
    M.prior_valid M.noise_valid

/-- This is a genuine probability measure with a finite second moment. -/
theorem posteriorLaw_memLp_two (M : GaussianModel ι κ) (y : EuclideanSpace ℝ κ) :
    MemLp id 2 (M.posteriorLaw y) := by
  rw [posteriorLaw, fdPosteriorKernel_apply]
  exact IsGaussian.memLp_two_id

theorem gainOp_eq_operator (M : GaussianModel ι κ) :
    M.gainOp = kalmanGainOp M.priorOp M.observationOp M.inverseInnovationOp := by
  exact matrixCLM_gain M.observation M.priorCov M.noiseCov

theorem innovation_left_inverse (M : GaussianModel ι κ) :
    M.inverseInnovationOp.comp (kalmanInnovationOp M.observationOp M.priorOp M.noiseOp) =
      ContinuousLinearMap.id ℝ (EuclideanSpace ℝ κ) := by
  exact matrixCLM_innovation_left_inverse M.observation M.priorCov M.noiseCov
    M.prior_valid M.noise_valid

theorem innovation_right_inverse (M : GaussianModel ι κ) :
    (kalmanInnovationOp M.observationOp M.priorOp M.noiseOp).comp M.inverseInnovationOp =
      ContinuousLinearMap.id ℝ (EuclideanSpace ℝ κ) := by
  exact matrixCLM_innovation_right_inverse M.observation M.priorCov M.noiseCov
    M.prior_valid M.noise_valid

/-- The actual posterior expectation is the existing operator update. -/
theorem posterior_expectation (M : GaussianModel ι κ) (y : EuclideanSpace ℝ κ) :
    (∫ x, x ∂M.posteriorLaw y) =
      kalmanPosteriorMean M.gainOp M.observationOp M.mean y := by
  rw [posteriorLaw, fdPosteriorKernel_apply, integral_id_multivariateGaussian]
  rfl

/-- The actual centered posterior covariance is the proved Schur matrix. -/
theorem posterior_covariance_matrix (M : GaussianModel ι κ) (y : EuclideanSpace ℝ κ) :
    centeredCovOp (M.posteriorLaw y) =
      matrixCLM (posteriorCovMatrix M.observation M.priorCov M.noiseCov) := by
  rw [posteriorLaw, fdPosteriorKernel_apply]
  exact centeredCovOp_multivariateGaussian _ _
    (posteriorCovMatrix_posSemidef M.observation M.priorCov M.noiseCov
      M.prior_valid M.noise_valid)

/-- The actual centered posterior covariance is the existing Joseph operator. -/
theorem posterior_covariance_operator (M : GaussianModel ι κ) (y : EuclideanSpace ℝ κ) :
    centeredCovOp (M.posteriorLaw y) =
      josephPosteriorCov M.gainOp M.observationOp M.priorOp M.noiseOp := by
  rw [posterior_covariance_matrix]
  exact matrixCLM_posteriorCov M.observation M.priorCov M.noiseCov
    M.prior_valid M.noise_valid

/-- The centered covariance is independent of the observed value, without requiring zero mean. -/
theorem posterior_covariance_observation_invariant (M : GaussianModel ι κ)
    (y z : EuclideanSpace ℝ κ) :
    centeredCovOp (M.posteriorLaw y) = centeredCovOp (M.posteriorLaw z) := by
  rw [posterior_covariance_matrix, posterior_covariance_matrix]

/-- Each canonical moment statement keeps its own evidence measure. -/
theorem canonical_moments_ae (M : GaussianModel ι κ) :
    ∀ᵐ y ∂M.evidenceLaw,
      (∫ x, x ∂M.canonicalKernel y) =
        kalmanPosteriorMean M.gainOp M.observationOp M.mean y ∧
      centeredCovOp (M.canonicalKernel y) =
        josephPosteriorCov M.gainOp M.observationOp M.priorOp M.noiseOp := by
  filter_upwards [M.posteriorLaw_ae_eq_canonical] with y hy
  rw [← hy]
  exact ⟨M.posterior_expectation y, M.posterior_covariance_operator y⟩

end GaussianModel
end Komorebi.FiniteDimensionalGaussianKalman
