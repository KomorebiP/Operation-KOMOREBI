import CoupledGrowthTypes
open Filter Komorebi.SpecialFunctions.Coupled.Scales
example (f : ℝ → ℝ) (lo : ℝ) (hh : ∀ᶠ R in atTop, lo ≤ f R) :
    lo ≤ Filter.liminf f atTop := by
  exact (real_type_sandwich hh).1
