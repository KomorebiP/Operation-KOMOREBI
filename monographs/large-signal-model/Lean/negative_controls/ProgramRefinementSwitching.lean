import KomorebiLSM.ProgramRefinement

-- A fixed all-zero/all-one child differs from resampling its identity at each step.
example : (1 / 2 : ℝ) * (1 * 1) + (1 / 2 : ℝ) * (0 * 0) =
    ((1 / 2 : ℝ) * 1 + (1 / 2 : ℝ) * 0) ^ 2 := by
  norm_num
