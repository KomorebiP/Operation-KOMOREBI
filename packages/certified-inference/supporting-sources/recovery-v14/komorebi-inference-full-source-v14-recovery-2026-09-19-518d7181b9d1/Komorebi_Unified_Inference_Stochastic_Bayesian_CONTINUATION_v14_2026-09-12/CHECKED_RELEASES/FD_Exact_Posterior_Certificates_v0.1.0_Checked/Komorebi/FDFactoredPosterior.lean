import Komorebi.FDGainSampler
import Komorebi.FDMatrixEnergyBounds

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open MeasureTheory ProbabilityTheory Matrix Komorebi.QuadraticTransport
open scoped ENNReal NNReal

/-- Two compatible latent input spaces permit a declared shared-noise coupling.
Prior covariance validity follows from its factor; the observation noise is definite. -/
structure FactoredGaussianModel (ι κ τ δ : Type*)
    [Fintype ι] [Fintype κ] [Fintype τ] [Fintype δ] where
  mean : EuclideanSpace ℝ ι
  observation : Matrix κ ι ℝ
  priorFactor : Matrix ι τ ℝ
  noiseFactor : Matrix κ δ ℝ
  noise_valid : (noiseFactor*noiseFactor.transpose).PosDef

namespace FactoredGaussianModel
variable {ι κ τ δ : Type*} [Fintype ι] [Fintype κ] [Fintype τ] [Fintype δ]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq τ] [DecidableEq δ]

def priorCov (M : FactoredGaussianModel ι κ τ δ) := M.priorFactor*M.priorFactor.transpose
def noiseCov (M : FactoredGaussianModel ι κ τ δ) := M.noiseFactor*M.noiseFactor.transpose
def gain (M : FactoredGaussianModel ι κ τ δ) := gainMatrix M.observation M.priorCov M.noiseCov
def meanAt (M : FactoredGaussianModel ι κ τ δ) (y : EuclideanSpace ℝ κ) :=
  gainMean M.observation M.mean M.gain y
def stateFactor (M : FactoredGaussianModel ι κ τ δ) : Matrix ι τ ℝ :=
  ((1 : Matrix ι ι ℝ)-M.gain*M.observation)*M.priorFactor
def obsFactor (M : FactoredGaussianModel ι κ τ δ) : Matrix ι δ ℝ := M.gain*M.noiseFactor

def posteriorLaw (M : FactoredGaussianModel ι κ τ δ) (y : EuclideanSpace ℝ κ) :=
  fdPosteriorKernel M.observation M.mean M.priorCov M.noiseCov y

omit [DecidableEq ι] [DecidableEq κ] [DecidableEq τ] [DecidableEq δ] in
theorem prior_valid (M : FactoredGaussianModel ι κ τ δ) : M.priorCov.PosSemidef := by
  simpa only [priorCov, Matrix.conjTranspose_eq_transpose_of_trivial] using
    Matrix.posSemidef_self_mul_conjTranspose M.priorFactor

omit [DecidableEq τ] [DecidableEq δ] in
/-- The posterior factors have exactly the Bayesian posterior covariance. -/
theorem posterior_factor_cov (M : FactoredGaussianModel ι κ τ δ) :
    M.stateFactor*M.stateFactor.transpose + M.obsFactor*M.obsFactor.transpose =
      posteriorCovMatrix M.observation M.priorCov M.noiseCov := by
  rw [← josephCovMatrix_eq_posteriorCovMatrix M.observation M.priorCov M.noiseCov
    M.prior_valid M.noise_valid]
  simp only [stateFactor, obsFactor, priorCov, noiseCov, josephCovMatrix, gain,
    Matrix.transpose_mul, Matrix.mul_assoc]

omit [DecidableEq τ] [DecidableEq δ] in
/-- Explicit posterior versions equal the selected canonical posterior on the proper evidence law. -/
theorem posterior_ae_canonical (M : FactoredGaussianModel ι κ τ δ) :
    M.posteriorLaw =ᵐ[multivariateGaussian (matrixCLM M.observation M.mean)
        (innovationMatrix M.observation M.priorCov M.noiseCov)]
      posterior (gaussianAffineKernel M.observation 0 M.noiseCov)
        (multivariateGaussian M.mean M.priorCov) := by
  exact fdPosteriorKernel_eq_canonical _ _ _ _ M.prior_valid M.noise_valid

/-- The full factor sampler has the actual Bayesian posterior law. The shared noise sign
convention is positive in both models; centered Gaussian symmetry makes this a Joseph sampler. -/
theorem factor_sampler_law (M : FactoredGaussianModel ι κ τ δ) (y : EuclideanSpace ℝ κ) :
    (gaussianNoiseSource (1 : Matrix τ τ ℝ) (1 : Matrix δ δ ℝ)).map
      (affineNoiseSample (M.meanAt y) M.stateFactor M.obsFactor) = M.posteriorLaw y := by
  rw [affineNoiseSample_law _ _ Matrix.PosSemidef.one Matrix.PosSemidef.one]
  simp only [Matrix.mul_one]
  rw [M.posterior_factor_cov, posteriorLaw, fdPosteriorKernel_apply]
  rfl

end FactoredGaussianModel
end Komorebi.FiniteDimensionalGaussianKalman
