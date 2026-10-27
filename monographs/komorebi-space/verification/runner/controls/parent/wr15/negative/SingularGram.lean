import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Basic.Real.Basic
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.Tactic.NormNum

set_option autoImplicit false
open Matrix

-- Redundant columns [1,1] have Gram matrix [[1,1],[1,1]].
-- Total matrix inverse notation does not make this matrix invertible.
example : IsUnit (!![1, 1; 1, 1] : Matrix (Fin 2) (Fin 2) ℝ).det := by
  norm_num [Matrix.det_fin_two]
