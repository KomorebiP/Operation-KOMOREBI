import KomorebiSpaceDiagonal

open KomorebiSpace.DiagonalRegularization Filter
open scoped Topology

example : Tendsto (fun M : ℝ => M * KomorebiSpace.BudgetProfile.beta T w M)
    atTop (𝓝 (Real.pi / 4)) := tendsto_actual_budget_product

example : Tendsto (fun N : ℕ => ‖hardPrefix N‖ * ‖w - T (hardPrefix N)‖)
    atTop (𝓝 1) := tendsto_hardPrefix_product

#print axioms sharp_diagonal_budget_asymptotic
