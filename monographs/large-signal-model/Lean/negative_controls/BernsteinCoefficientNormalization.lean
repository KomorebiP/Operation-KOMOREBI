import KomorebiLSM.PositivePolynomialApproximation
open Komorebi.LSM.PositivePolynomialApproximation

/- Omitting the n+1 coefficient factor would halve this normalized constant
coefficient at degree1. The actual coefficient is1. -/
example : coefficient 1 (fun _ : ℝ => (1 : ℝ)) 0 = 1/2 := by
  rw [coefficient_constant]
  norm_num
