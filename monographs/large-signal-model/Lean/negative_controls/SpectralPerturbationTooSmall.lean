import KomorebiLSM.Block14Examples
example : |((2:ℝ) • (LinearMap.id : ℝ →ₗ[ℝ] ℝ)).singularValues 0 -
    (0 : ℝ →ₗ[ℝ] ℝ).singularValues 0| ≤ 1 := by
  rw [Komorebi.LSM.Block14Examples.double_first_singular]
  norm_num
