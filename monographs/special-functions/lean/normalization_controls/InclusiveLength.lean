import CoupledNormalization
noncomputable section
open Komorebi.SpecialFunctions.Coupled.Scales

example (p : RationalScales) (N : ℕ) : (p.derivativeArray N).length = N := by
  exact derivative_array_length p N
