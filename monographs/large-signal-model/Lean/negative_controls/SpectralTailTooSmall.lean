import KomorebiLSM.Block14Examples
example : ‖(Komorebi.LSM.Spectral.leadingLeft
    (((2:ℝ) • ContinuousLinearMap.id ℝ ℝ).toLinearMap) 0 (by simp))ᗮ.starProjection.comp
    ((2:ℝ) • ContinuousLinearMap.id ℝ ℝ)‖ ≤ 1 := by
  rw [Komorebi.LSM.Block14Examples.discard_all_scalar_modes]
  norm_num
