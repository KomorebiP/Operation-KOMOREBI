import CoupledScalarReduction
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example : halfScales.IsEntireSolution (fun z : ℂ => (1 : ℂ) * Complex.sinh ((1 : ℂ)⁻¹ * z))
    (fun z : ℂ => (1 : ℂ) * Complex.sinh ((1 : ℂ)⁻¹ * z)) := by
  exact scaled_sinh_half_solution (by norm_num : (1 : ℂ) ^ 2 = 2)
