import KomorebiSpace.RegularizationNoiseLimits

set_option autoImplicit false
noncomputable section
open KomorebiSpace

-- Every positive parameter has a concrete scalar operator attaining equality
-- for distinct data. This checks the factor 2 in the universal noise bound.
example (α : ℝ) (hα : 0 < α) :
    ‖RegularizedHilbertRepair.correction
        (RegularizationNoiseLimits.scalarSharpOperator α) α hα 1 -
      RegularizedHilbertRepair.correction
        (RegularizationNoiseLimits.scalarSharpOperator α) α hα 0‖ =
      1 / (2 * Real.sqrt α) := by
  simpa only [sub_zero, norm_one] using
    RegularizationNoiseLimits.data_noise_coefficient_attained α hα 1 0
