import KomorebiLSM.Block13Examples
example : 0 < Komorebi.LSM.Spectral.leastPositive (0 : ℝ →ₗ[ℝ] ℝ) := by
  rw [Komorebi.LSM.Block13Examples.zero_has_no_positive_singular_value]
  norm_num
