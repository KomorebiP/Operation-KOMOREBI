import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
open Matrix
-- A zero exact answer does not preserve the first coordinate of (2,3).
example : (!![1, 0] : Matrix (Fin 1) (Fin 2) ℚ) *ᵥ ![0, 0] =
    (!![1, 0] : Matrix (Fin 1) (Fin 2) ℚ) *ᵥ ![2, 3] := by
  ext i
  fin_cases i
  norm_num [Matrix.mulVec, dotProduct, Fin.sum_univ_succ]
