import KomorebiSpaceRegularization
noncomputable section
example : ∃! a : ℝ, ∀ b : ℝ,
    KomorebiSpace.RegularizedHilbertRepair.objective (0 : ℝ →L[ℝ] ℝ) 0 0 a ≤
      KomorebiSpace.RegularizedHilbertRepair.objective (0 : ℝ →L[ℝ] ℝ) 0 0 b := by
  exact KomorebiSpace.RegularizedHilbertRepair.exists_unique_minimizer _ 0 (by norm_num) 0
