import Komorebi.FDGaussianCoupling
import Komorebi.FDInexactGainAlgebra
import Komorebi.FDGaussianConditioning

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open MeasureTheory ProbabilityTheory Matrix Komorebi.QuadraticTransport
open scoped ENNReal NNReal

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- Innovation-form mean for an arbitrary gain. -/
def gainMean (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (B : Matrix ι κ ℝ) (y : EuclideanSpace ℝ κ) : EuclideanSpace ℝ ι :=
  m + matrixCLM B (y - matrixCLM H m)

/-- A valid Gaussian approximation when model covariances are valid.
An arbitrary gain is not claimed to be exact Bayesian conditioning. -/
def gainPosteriorLaw (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) : Measure (EuclideanSpace ℝ ι) :=
  multivariateGaussian (gainMean H m B y) (gainJoseph H P R B)

/-- Centered-input pathwise Joseph sampler. Its source is a product of actual Gaussian laws. -/
def gainSample (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (B : Matrix ι κ ℝ) (y : EuclideanSpace ℝ κ) :=
  affineNoiseSample (gainMean H m B y) ((1 : Matrix ι ι ℝ)-B*H) (-B)

/-- Actual law of the approximate-gain sampler. -/
theorem gainSample_law (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosSemidef) :
    (gaussianNoiseSource P R).map (gainSample H m B y) =
      gainPosteriorLaw H m P R B y := by
  unfold gainSample gainPosteriorLaw
  rw [affineNoiseSample_law P R hP hR]
  simp only [Matrix.transpose_neg, Matrix.neg_mul, Matrix.mul_neg, neg_neg, gainJoseph]

/-- The exact gain's sampler law is the posterior version already proved by disintegration. -/
theorem gainPosteriorLaw_exact (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (y : EuclideanSpace ℝ κ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    gainPosteriorLaw H m P R (gainMatrix H P R) y = fdPosteriorKernel H m P R y := by
  rw [gainPosteriorLaw, gainJoseph_exact H P R hP hR, fdPosteriorKernel_apply]
  rfl

theorem gainSample_exact_posterior_law (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (y : EuclideanSpace ℝ κ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    (gaussianNoiseSource P R).map (gainSample H m (gainMatrix H P R) y) =
      fdPosteriorKernel H m P R y := by
  rw [gainSample_law H m P R _ y hP hR.posSemidef,
    gainPosteriorLaw_exact H m P R y hP hR]

/-- The posterior/approximation coupling is an explicitly constructed measure. -/
def inexactGainCoupling (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) : Measure (EuclideanSpace ℝ ι × EuclideanSpace ℝ ι) :=
  (gaussianNoiseSource P R).map
    (fun z => (gainSample H m (gainMatrix H P R) y z, gainSample H m B y z))

/-- Both marginals are proved; posterior equality is not a hypothesis. -/
theorem inexactGainCoupling_isTransportPlan (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosDef) :
    IsTransportPlan (fdPosteriorKernel H m P R y) (gainPosteriorLaw H m P R B y)
      (inexactGainCoupling H m P R B y) := by
  have h := sharedMap_isTransportPlan (gaussianNoiseSource P R)
    (gainSample H m (gainMatrix H P R) y) (gainSample H m B y)
    (by unfold gainSample affineNoiseSample; fun_prop)
    (by unfold gainSample affineNoiseSample; fun_prop)
  rw [gainSample_exact_posterior_law H m P R y hP hR,
    gainSample_law H m P R B y hP hR.posSemidef] at h
  exact h

/-- Mean difference of two gain samplers. -/
theorem gainMean_sub (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (B B0 : Matrix ι κ ℝ) (y : EuclideanSpace ℝ κ) :
    gainMean H m B y - gainMean H m B0 y =
      matrixCLM (B-B0) (y-matrixCLM H m) := by
  simp only [gainMean, matrixCLM_sub, _root_.sub_apply]
  abel

omit [DecidableEq κ] in
/-- Covariance of the difference under shared noises. -/
theorem gainNoiseDifferenceCov (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (R : Matrix κ κ ℝ) (B B0 : Matrix ι κ ℝ) :
    ((1-B*H)-(1-B0*H))*P*((1-B*H)-(1-B0*H)).transpose +
      ((-B)-(-B0))*R*((-B)-(-B0)).transpose =
      (B-B0)*innovationMatrix H P R*(B-B0).transpose := by
  have hA : ((1 : Matrix ι ι ℝ)-B*H)-(1-B0*H) = -(B-B0)*H := by
    simp only [Matrix.neg_mul, Matrix.sub_mul]
    abel
  have hB : -B - -B0 = -(B-B0) := by abel
  rw [hA, hB]
  simp only [Matrix.transpose_mul, Matrix.transpose_neg, Matrix.neg_mul,
    Matrix.mul_neg, neg_neg, innovationMatrix, Matrix.mul_add, Matrix.add_mul, Matrix.mul_assoc]

end Komorebi.FiniteDimensionalGaussianKalman
