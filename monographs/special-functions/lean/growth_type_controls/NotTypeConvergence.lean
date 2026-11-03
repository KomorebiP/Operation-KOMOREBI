import CoupledGrowthTypes
open Filter Komorebi.SpecialFunctions.Coupled.Scales
open scoped Topology
example (f : ℝ → ℝ) (ρ lo hi : ℝ) (hlo : 0 < lo) (hhi : 0 < hi)
    (hh : ∀ᶠ R in atTop, lo ≤ Real.log (f R) / R ^ ρ ∧ Real.log (f R) / R ^ ρ ≤ hi) :
    Tendsto (fun R => Real.log (f R) / R ^ ρ) atTop (𝓝 ρ) := by
  exact tendsto_loglog_of_ratio_bounds hlo hhi hh
