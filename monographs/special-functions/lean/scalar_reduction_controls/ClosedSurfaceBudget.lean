import CoupledScalarReduction
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example : surfaceCrossScale (1 / 2) (1 / 4) (1 / 2) 1 < 1 := by
  have h := surface_cross_scale_contract (by norm_num : (0 : ℝ) < 1 / 2)
    (by norm_num : (0 : ℝ) < 1 / 4) (by norm_num : (0 : ℝ) < 1 / 2)
    (by norm_num) (by norm_num) (by norm_num : (0 : ℝ) < 1)
    (by norm_num : (1 - (1 / 2 : ℝ) ^ (1 : ℝ)) * (1 - (1 / 2 : ℝ) ^ (1 : ℝ)) <
      (1 / 4 : ℝ) ^ (1 : ℝ))
  exact h.2.1
