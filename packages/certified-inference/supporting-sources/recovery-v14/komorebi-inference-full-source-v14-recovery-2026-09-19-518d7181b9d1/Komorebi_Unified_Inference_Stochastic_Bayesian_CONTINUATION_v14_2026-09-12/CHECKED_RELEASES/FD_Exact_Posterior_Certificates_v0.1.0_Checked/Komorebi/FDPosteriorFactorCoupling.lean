import Komorebi.FDFactoredPosterior

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman.FactoredGaussianModel
open MeasureTheory ProbabilityTheory Matrix Komorebi.QuadraticTransport
open scoped ENNReal NNReal

variable {ι κ τ δ : Type*} [Fintype ι] [Fintype κ] [Fintype τ] [Fintype δ]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq τ] [DecidableEq δ]

/-- The displayed squared error certificate for a fixed, declared factor coupling. -/
def factorErrorBudget (M M0 : FactoredGaussianModel ι κ τ δ)
    (y y0 : EuclideanSpace ℝ κ) : ℝ :=
  ‖M.meanAt y-M0.meanAt y0‖^2 +
    frobeniusSq (M.stateFactor-M0.stateFactor) + frobeniusSq (M.obsFactor-M0.obsFactor)

/-- Explicit common-standard-noise joint measure for the two actual posteriors. -/
def factorCoupling (M M0 : FactoredGaussianModel ι κ τ δ)
    (y y0 : EuclideanSpace ℝ κ) : Measure (EuclideanSpace ℝ ι × EuclideanSpace ℝ ι) :=
  (gaussianNoiseSource (1 : Matrix τ τ ℝ) (1 : Matrix δ δ ℝ)).map
    (fun z => (affineNoiseSample (M.meanAt y) M.stateFactor M.obsFactor z,
      affineNoiseSample (M0.meanAt y0) M0.stateFactor M0.obsFactor z))

/-- Both marginals are actual posterior versions, independently derived from model validity. -/
theorem factorCoupling_isTransportPlan (M M0 : FactoredGaussianModel ι κ τ δ)
    (y y0 : EuclideanSpace ℝ κ) :
    IsTransportPlan (M.posteriorLaw y) (M0.posteriorLaw y0) (M.factorCoupling M0 y y0) := by
  have h := sharedMap_isTransportPlan
    (gaussianNoiseSource (1 : Matrix τ τ ℝ) (1 : Matrix δ δ ℝ))
    (affineNoiseSample (M.meanAt y) M.stateFactor M.obsFactor)
    (affineNoiseSample (M0.meanAt y0) M0.stateFactor M0.obsFactor)
    (by unfold affineNoiseSample; fun_prop) (by unfold affineNoiseSample; fun_prop)
  rw [M.factor_sampler_law y, M0.factor_sampler_law y0] at h
  exact h

/-- Exact quadratic cost: mean error plus two Frobenius factor errors. -/
theorem factorCoupling_cost (M M0 : FactoredGaussianModel ι κ τ δ)
    (y y0 : EuclideanSpace ℝ κ) :
    quadraticCost (M.factorCoupling M0 y y0) = ENNReal.ofReal (M.factorErrorBudget M0 y y0) := by
  unfold factorCoupling
  rw [affineNoiseSample_coupling_cost _ _ Matrix.PosSemidef.one Matrix.PosSemidef.one]
  simp only [Matrix.mul_one, Matrix.trace_add, trace_mul_transpose_eq_frobeniusSq,
    factorErrorBudget, add_assoc]

/-- Full two-model posterior-distribution certificate. Factors are explicit inputs,
not silently recovered from covariance discrepancies. No optimality of this coupling is claimed. -/
theorem posterior_wasserstein2Sq_le_factors (M M0 : FactoredGaussianModel ι κ τ δ)
    (y y0 : EuclideanSpace ℝ κ) :
    wasserstein2Sq (M.posteriorLaw y) (M0.posteriorLaw y0) ≤
      ENNReal.ofReal (M.factorErrorBudget M0 y y0) := by
  calc
    _ ≤ quadraticCost (M.factorCoupling M0 y y0) :=
      wasserstein2Sq_le_cost _ _ _ (M.factorCoupling_isTransportPlan M0 y y0)
    _ = _ := M.factorCoupling_cost M0 y y0

end Komorebi.FiniteDimensionalGaussianKalman.FactoredGaussianModel
