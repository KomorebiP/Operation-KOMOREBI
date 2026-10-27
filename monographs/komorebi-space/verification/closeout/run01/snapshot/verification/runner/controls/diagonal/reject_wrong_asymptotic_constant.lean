import KomorebiSpaceDiagonal

open KomorebiSpace.DiagonalRegularization Filter
open scoped Topology

-- Deliberate incorrect constant: the exact theorem must not elaborate at 1.
example : Tendsto (fun M : ℝ => M * KomorebiSpace.BudgetProfile.beta T w M)
    atTop (𝓝 (1 : ℝ)) := tendsto_actual_budget_product
