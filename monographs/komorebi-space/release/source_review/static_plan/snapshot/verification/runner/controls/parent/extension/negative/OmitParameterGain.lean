import KomorebiSpaceRegularization
noncomputable section
open KomorebiSpace.RegularizedHilbertRepair
example : ‖(1:ℝ)-correction (0 : ℝ →L[ℝ] ℝ) (1/4) (by norm_num) 0‖ ≤
    ‖gradient (0 : ℝ →L[ℝ] ℝ) (1/4) 0 1‖ := by
  norm_num [correction_zero, gradient, normal]
