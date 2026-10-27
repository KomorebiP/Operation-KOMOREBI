import KomorebiSpaceRegularization
noncomputable section
open KomorebiSpace
example : RegularizedHilbertRepair.objective (0 : ℝ →L[ℝ] ℝ) 1 1 0 ≤
    RegularizationCertificates.dual (0 : ℝ →L[ℝ] ℝ) 1 1 3 := by
  norm_num [RegularizedHilbertRepair.objective, RegularizationCertificates.dual]
