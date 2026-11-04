import KCosCertification

open KCosCertification

-- Expected unsolved goal: a one-decade probability ratio is ten, so its
-- excess above one is nine. The deliberately asserted value one is false.
example : logWidthRatio 0 1 = 1 := by
  norm_num [logWidthRatio, Real.exp_log (by norm_num : (0 : ℝ) < 10)]
