import KomorebiQCOS.Acceptance
open KomorebiQCOS
example {p estimate : ℝ} (hp : Enclosed p 1 2) (he : Enclosed estimate 1 2) :
    |estimate - p| / p ≤ 1/100 := by
  exact multiplicativeBudget_relative_error hp he
