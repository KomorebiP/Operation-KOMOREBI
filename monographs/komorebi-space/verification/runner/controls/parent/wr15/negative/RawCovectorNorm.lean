import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.NormNum

set_option autoImplicit false
open Matrix

-- B = I, g = e₁ and C = [[2,1],[0,1]] give q' = (2,1).
-- Claiming the raw covector squared norm still equals ‖g‖² = 1 is false.
example : dotProduct (![2, 1] : Fin 2 → ℝ) ![2, 1] = 1 := by
  norm_num [dotProduct, Fin.sum_univ_two]
