import Controls.FallingPositive

open Polynomial
open Komorebi.Polynomial.FallingProduct

-- Deliberately false: the transported product of X with X vanishes at one.
example :
    (fallingProduct (X : ℚ[X]) X).eval 1 = ((X : ℚ[X]) * X).eval 1 := by
  rw [fallingProduct_X_X]
  norm_num
  decide
