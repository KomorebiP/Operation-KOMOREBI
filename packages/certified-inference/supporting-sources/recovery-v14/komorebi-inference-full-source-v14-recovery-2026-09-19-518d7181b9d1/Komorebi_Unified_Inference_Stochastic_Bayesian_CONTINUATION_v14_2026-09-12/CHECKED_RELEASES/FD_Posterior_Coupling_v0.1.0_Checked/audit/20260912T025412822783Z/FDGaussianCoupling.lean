import Komorebi.FDGaussianSum
import Komorebi.FDGaussianQuadraticMoment
import Komorebi.FDMatrixOperatorCompat
import Komorebi.QuadraticTransport

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open MeasureTheory ProbabilityTheory Matrix Komorebi.QuadraticTransport
open scoped ENNReal NNReal

variable {ι κ η : Type*} [Fintype ι] [Fintype κ] [Fintype η]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq η]

/-- Shared independent centered input, including singular input covariances. -/
def gaussianNoiseSource (P : Matrix ι ι ℝ) (Q : Matrix κ κ ℝ) :
    Measure (EuclideanSpace ℝ ι × EuclideanSpace ℝ κ) :=
  (multivariateGaussian 0 P).prod (multivariateGaussian 0 Q)

/-- An affine sampler on the shared independent input. -/
def affineNoiseSample (c : EuclideanSpace ℝ η)
    (A : Matrix η ι ℝ) (B : Matrix η κ ℝ)
    (z : EuclideanSpace ℝ ι × EuclideanSpace ℝ κ) : EuclideanSpace ℝ η :=
  c + (matrixCLM A z.1 + matrixCLM B z.2)

/-- This is an equality of actual probability measures, not just of moments. -/
theorem affineNoiseSample_law (P : Matrix ι ι ℝ) (Q : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hQ : Q.PosSemidef) (c : EuclideanSpace ℝ η)
    (A : Matrix η ι ℝ) (B : Matrix η κ ℝ) :
    (gaussianNoiseSource P Q).map (affineNoiseSample c A B) =
      multivariateGaussian c (A*P*A.transpose + B*Q*B.transpose) := by
  change ((multivariateGaussian 0 P).prod (multivariateGaussian 0 Q)).map
    (fun z => c + (matrixCLM A z.1 + matrixCLM B z.2)) = _
  simpa only [map_zero, add_zero] using
    multivariateGaussian_map_affine_product 0 0 P Q A B c hP hQ

omit [DecidableEq η] in
/-- The difference sampler is an affine sampler with the difference coefficients. -/
theorem affineNoiseSample_sub (c c0 : EuclideanSpace ℝ η)
    (A A0 : Matrix η ι ℝ) (B B0 : Matrix η κ ℝ)
    (z : EuclideanSpace ℝ ι × EuclideanSpace ℝ κ) :
    affineNoiseSample c A B z - affineNoiseSample c0 A0 B0 z =
      affineNoiseSample (c-c0) (A-A0) (B-B0) z := by
  simp only [affineNoiseSample, matrixCLM_sub, sub_apply]
  abel

/-- Law of the common-noise difference. -/
theorem affineNoiseSample_difference_law
    (P : Matrix ι ι ℝ) (Q : Matrix κ κ ℝ) (hP : P.PosSemidef) (hQ : Q.PosSemidef)
    (c c0 : EuclideanSpace ℝ η) (A A0 : Matrix η ι ℝ) (B B0 : Matrix η κ ℝ) :
    (gaussianNoiseSource P Q).map
      (fun z => affineNoiseSample c A B z - affineNoiseSample c0 A0 B0 z) =
      multivariateGaussian (c-c0)
        ((A-A0)*P*(A-A0).transpose + (B-B0)*Q*(B-B0).transpose) := by
  simp_rw [affineNoiseSample_sub]
  exact affineNoiseSample_law P Q hP hQ (c-c0) (A-A0) (B-B0)

/-- The common-noise pair has the required two Gaussian marginals. -/
theorem affineNoiseSample_transportPlan
    (P : Matrix ι ι ℝ) (Q : Matrix κ κ ℝ) (hP : P.PosSemidef) (hQ : Q.PosSemidef)
    (c c0 : EuclideanSpace ℝ η) (A A0 : Matrix η ι ℝ) (B B0 : Matrix η κ ℝ) :
    IsTransportPlan
      (multivariateGaussian c (A*P*A.transpose + B*Q*B.transpose))
      (multivariateGaussian c0 (A0*P*A0.transpose + B0*Q*B0.transpose))
      ((gaussianNoiseSource P Q).map
        (fun z => (affineNoiseSample c A B z, affineNoiseSample c0 A0 B0 z))) := by
  have hp := sharedMap_isTransportPlan (gaussianNoiseSource P Q)
    (affineNoiseSample c A B) (affineNoiseSample c0 A0 B0)
    (by unfold affineNoiseSample; fun_prop) (by unfold affineNoiseSample; fun_prop)
  rw [affineNoiseSample_law P Q hP hQ, affineNoiseSample_law P Q hP hQ] at hp
  exact hp

/-- Exact nonnegative quadratic cost of the exhibited Gaussian coupling. -/
theorem affineNoiseSample_coupling_cost
    (P : Matrix ι ι ℝ) (Q : Matrix κ κ ℝ) (hP : P.PosSemidef) (hQ : Q.PosSemidef)
    (c c0 : EuclideanSpace ℝ η) (A A0 : Matrix η ι ℝ) (B B0 : Matrix η κ ℝ) :
    quadraticCost ((gaussianNoiseSource P Q).map
        (fun z => (affineNoiseSample c A B z, affineNoiseSample c0 A0 B0 z))) =
      ENNReal.ofReal (‖c-c0‖^2 +
        ((A-A0)*P*(A-A0).transpose + (B-B0)*Q*(B-B0).transpose).trace) := by
  rw [quadraticCost_sharedMap _ _ _ (by unfold affineNoiseSample; fun_prop)
    (by unfold affineNoiseSample; fun_prop)]
  rw [← lintegral_map (f := fun x : EuclideanSpace ℝ η => ENNReal.ofReal (‖x‖^2))
    (g := fun z => affineNoiseSample c A B z - affineNoiseSample c0 A0 B0 z)
    (by fun_prop) (by unfold affineNoiseSample; fun_prop)]
  rw [affineNoiseSample_difference_law P Q hP hQ,
    gaussian_lintegral_norm_sq _ _
      ((imageCov_posSemidef _ P hP).add (imageCov_posSemidef _ Q hQ))]

/-- A distribution-level bound on the standard all-coupling 2-Wasserstein infimum. -/
theorem gaussian_affine_wasserstein2Sq_le
    (P : Matrix ι ι ℝ) (Q : Matrix κ κ ℝ) (hP : P.PosSemidef) (hQ : Q.PosSemidef)
    (c c0 : EuclideanSpace ℝ η) (A A0 : Matrix η ι ℝ) (B B0 : Matrix η κ ℝ) :
    wasserstein2Sq
      (multivariateGaussian c (A*P*A.transpose + B*Q*B.transpose))
      (multivariateGaussian c0 (A0*P*A0.transpose + B0*Q*B0.transpose)) ≤
      ENNReal.ofReal (‖c-c0‖^2 +
        ((A-A0)*P*(A-A0).transpose + (B-B0)*Q*(B-B0).transpose).trace) := by
  calc
    _ ≤ quadraticCost ((gaussianNoiseSource P Q).map
        (fun z => (affineNoiseSample c A B z, affineNoiseSample c0 A0 B0 z))) :=
      wasserstein2Sq_le_cost _ _ _
        (affineNoiseSample_transportPlan P Q hP hQ c c0 A A0 B B0)
    _ = _ := affineNoiseSample_coupling_cost P Q hP hQ c c0 A A0 B B0

end Komorebi.FiniteDimensionalGaussianKalman
