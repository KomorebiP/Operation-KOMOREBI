import KomorebiQCOS.Acceptance
open KomorebiQCOS
example : MultiplicativeBudget (100 - 10) (100 + 10) (1/9 : ℝ) := by
  norm_num [MultiplicativeBudget]
