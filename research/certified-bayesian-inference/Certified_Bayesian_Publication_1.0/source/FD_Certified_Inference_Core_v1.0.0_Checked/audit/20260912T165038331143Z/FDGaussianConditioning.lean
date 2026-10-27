import Komorebi.FDReverseJointLaw

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix ProbabilityTheory MeasureTheory

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- Exact disintegration: both sides are actual joint probability measures. -/
theorem fd_joint_disintegration
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    (multivariateGaussian (matrixCLM H m) (innovationMatrix H P R)) ⊗ₘ
        fdPosteriorKernel H m P R =
      ((multivariateGaussian m P) ⊗ₘ gaussianAffineKernel H 0 R).map Prod.swap := by
  apply map_pack_injective
  rw [reverse_joint_gaussian H m P R hP hR,
    forward_joint_gaussian H m P R hP hR.posSemidef,
    reverseJointCov_eq_forwardJointCov H P R hP hR]

/-- The observation distribution is the genuine marginal of the prior/likelihood joint. -/
theorem fd_observation_evidence
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    gaussianAffineKernel H 0 R ∘ₘ multivariateGaussian m P =
      multivariateGaussian (matrixCLM H m) (innovationMatrix H P R) := by
  have h := congrArg Measure.fst (fd_joint_disintegration H m P R hP hR)
  simpa only [Measure.fst_compProd, Measure.fst_map_swap, Measure.snd_compProd] using h.symm

/-- The explicit Kalman kernel agrees with Mathlib's canonical Bayesian posterior a.e. -/
theorem fdPosteriorKernel_eq_canonical
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    fdPosteriorKernel H m P R =ᵐ[
      multivariateGaussian (matrixCLM H m) (innovationMatrix H P R)]
      posterior (gaussianAffineKernel H 0 R) (multivariateGaussian m P) := by
  have h := ae_eq_posterior_of_compProd_eq
    (κ := gaussianAffineKernel H 0 R) (μ := multivariateGaussian m P)
    (η := fdPosteriorKernel H m P R) (by
      rw [fd_observation_evidence H m P R hP hR]
      exact fd_joint_disintegration H m P R hP hR)
  rwa [fd_observation_evidence H m P R hP hR] at h

/-- Finite-dimensional Gaussian conditioning, with singular prior covariance permitted.
The observation noise remains positive definite. Equality is evidence-almost everywhere. -/
theorem canonicalPosterior_eq_multivariateGaussian
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    ∀ᵐ y ∂multivariateGaussian (matrixCLM H m) (innovationMatrix H P R),
      posterior (gaussianAffineKernel H 0 R) (multivariateGaussian m P) y =
        multivariateGaussian
          (m + matrixCLM (gainMatrix H P R) (y - matrixCLM H m))
          (posteriorCovMatrix H P R) := by
  filter_upwards [fdPosteriorKernel_eq_canonical H m P R hP hR] with y hy
  rw [← hy, fdPosteriorKernel_apply]

/-- The same actual posterior in Joseph covariance form. -/
theorem canonicalPosterior_eq_josephGaussian
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    ∀ᵐ y ∂multivariateGaussian (matrixCLM H m) (innovationMatrix H P R),
      posterior (gaussianAffineKernel H 0 R) (multivariateGaussian m P) y =
        multivariateGaussian
          (m + matrixCLM (gainMatrix H P R) (y - matrixCLM H m))
          (josephCovMatrix H P R) := by
  rw [josephCovMatrix_eq_posteriorCovMatrix H P R hP hR]
  exact canonicalPosterior_eq_multivariateGaussian H m P R hP hR

end Komorebi.FiniteDimensionalGaussianKalman
