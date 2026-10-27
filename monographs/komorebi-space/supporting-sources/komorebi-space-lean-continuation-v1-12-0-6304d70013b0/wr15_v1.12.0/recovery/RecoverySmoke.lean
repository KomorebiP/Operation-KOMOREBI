import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

example {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E] (x : E) :
    0 ≤ ‖x‖ := norm_nonneg x

example {n : Type*} [Fintype n] [DecidableEq n] (A : Matrix n n ℝ) :
    A * 1 = A := mul_one A
