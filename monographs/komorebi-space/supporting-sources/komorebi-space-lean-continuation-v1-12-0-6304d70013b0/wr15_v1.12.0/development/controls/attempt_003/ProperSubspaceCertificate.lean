import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.Tactic.NormNum

set_option autoImplicit false
open Matrix

-- With p=0, T=I, a=0, r=e₂, the full normal residual is g=-e₂.
-- A single basis column e₁ records q=0 but does not span ker p=ℝ².
-- Its zero reported certificate cannot bound the actual squared norm.
example : dotProduct (![0, -1] : Fin 2 → ℝ) ![0, -1] ≤ 0 := by
  norm_num [dotProduct, Fin.sum_univ_two]
