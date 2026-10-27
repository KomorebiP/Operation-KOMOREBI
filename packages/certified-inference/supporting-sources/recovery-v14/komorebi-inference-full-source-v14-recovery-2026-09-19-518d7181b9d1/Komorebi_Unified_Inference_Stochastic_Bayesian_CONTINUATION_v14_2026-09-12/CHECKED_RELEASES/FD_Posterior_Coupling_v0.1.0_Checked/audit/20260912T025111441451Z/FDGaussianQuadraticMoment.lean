import Komorebi.FDGaussianTransport
import Mathlib.MeasureTheory.Function.L2Space

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open MeasureTheory ProbabilityTheory Matrix
open scoped ENNReal NNReal

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- Finite second moment, also for degenerate Gaussians. -/
theorem gaussian_norm_sq_integrable (m : EuclideanSpace ℝ ι) (P : Matrix ι ι ℝ) :
    Integrable (fun x => ‖x‖ ^ 2) (multivariateGaussian m P) := by
  exact IsGaussian.memLp_two_id.integrable_norm_pow (by norm_num)

/-- The coordinate second moment includes the mean square. -/
theorem gaussian_coordinate_second_moment
    (m : EuclideanSpace ℝ ι) (P : Matrix ι ι ℝ) (hP : P.PosSemidef) (i : ι) :
    (∫ x, (x i) ^ 2 ∂multivariateGaussian m P) = (m i) ^ 2 + P i i := by
  have hm : (∫ x, x i ∂multivariateGaussian m P) = m i := by
    change (∫ x, (EuclideanSpace.proj i) x ∂multivariateGaussian m P) = _
    rw [ContinuousLinearMap.integral_comp_id_comm IsGaussian.integrable_id (EuclideanSpace.proj i)]
    simp
  have hv := variance_eq_sub
    (IsGaussian.memLp_dual (multivariateGaussian m P) (EuclideanSpace.proj i) 2 (by simp))
  change variance (fun x => x i) (multivariateGaussian m P) =
    (∫ x, (x i) ^ 2 ∂multivariateGaussian m P) -
      (∫ x, x i ∂multivariateGaussian m P) ^ 2 at hv
  rw [variance_eval_multivariateGaussian hP, hm] at hv
  linarith

/-- Exact quadratic expectation: squared mean plus centered covariance trace. -/
theorem gaussian_integral_norm_sq (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (hP : P.PosSemidef) :
    (∫ x, ‖x‖ ^ 2 ∂multivariateGaussian m P) = ‖m‖ ^ 2 + P.trace := by
  simp_rw [EuclideanSpace.real_norm_sq_eq]
  rw [integral_finsetSum]
  · simp_rw [gaussian_coordinate_second_moment m P hP]
    rw [Finset.sum_add_distrib]
    rfl
  · intro i _
    exact (IsGaussian.memLp_dual (multivariateGaussian m P)
      (EuclideanSpace.proj i) 2 (by simp)).integrable_sq

/-- Nonnegative extended-integral form used by the transport cost. -/
theorem gaussian_lintegral_norm_sq (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (hP : P.PosSemidef) :
    (∫⁻ x, ENNReal.ofReal (‖x‖ ^ 2) ∂multivariateGaussian m P) =
      ENNReal.ofReal (‖m‖ ^ 2 + P.trace) := by
  rw [← ofReal_integral_eq_lintegral_ofReal (gaussian_norm_sq_integrable m P)
    (Filter.Eventually.of_forall (fun _ => sq_nonneg _)),
    gaussian_integral_norm_sq m P hP]

end Komorebi.FiniteDimensionalGaussianKalman
