import KomorebiSpace.RegularizationLimits

set_option autoImplicit false
noncomputable section
open Filter
open scoped Topology
open KomorebiSpace

-- Deliberately invalid promotion from a right-hand limit to a two-sided limit.
-- At nonpositive parameters the total path is zero, so the filter matters.
example : Tendsto (fun α : ℝ => (ContinuousLinearMap.id ℝ ℝ)
    (RegularizationLimits.path (ContinuousLinearMap.id ℝ ℝ) 1 α))
    (𝓝 (0 : ℝ)) (𝓝 (BudgetProfile.projectedDatum (ContinuousLinearMap.id ℝ ℝ) 1)) := by
  exact RegularizationLimits.fitted_tendsto_projectedDatum (ContinuousLinearMap.id ℝ ℝ) 1
