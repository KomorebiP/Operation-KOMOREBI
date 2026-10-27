import Mathlib.Analysis.InnerProductSpace.Basic

example {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E] (x : E) :
    0 ≤ ‖x‖ := norm_nonneg x
