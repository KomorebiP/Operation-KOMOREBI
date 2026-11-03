import CoupledTypeProportions
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example : (![0, 0] : Fin 2 → ℝ) = ![0, 1] := by
  apply positive_dot_rigidity (l := ![1, 0])
  · intro i
    fin_cases i <;> norm_num
  · intro i
    fin_cases i <;> norm_num
  · norm_num [dotProduct, Fin.sum_univ_two]
