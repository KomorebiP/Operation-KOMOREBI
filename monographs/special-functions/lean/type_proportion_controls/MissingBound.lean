import CoupledTypeProportions
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example (f : ℝ → ℝ) (h : ∀ᶠ R in atTop, (1 : ℝ) ≤ f R) :
    (1 : ℝ) ≤ Filter.liminf f atTop := by
  exact lower_comparison_of_tendsto h tendsto_const_nhds h
