import KomorebiLSM.Block12Examples
example : ‖(⊥ : Submodule ℝ ℝ).starProjection-(⊤ : Submodule ℝ ℝ).starProjection‖ ≤ 0 := by
  rw [Komorebi.LSM.Block12Examples.unequal_rank_full_gap_one]
  norm_num
