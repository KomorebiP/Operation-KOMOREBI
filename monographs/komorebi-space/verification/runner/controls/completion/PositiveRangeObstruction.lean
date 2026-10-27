import KomorebiSpace.DiagonalRangeObstruction

open KomorebiSpace.DiagonalRegularization

example : ¬ IsClosed (Set.range T) := T_not_closed_range
example : w ∈ closure (Set.range T) ∧ w ∉ Set.range T := w_mem_closure_not_range
example (j : ℕ) : ‖unitCoordinate j‖ = 1 := norm_unitCoordinate j
example (j : ℕ) : ‖T (unitCoordinate j)‖ = 1 / ((j : ℝ) + 1) :=
  norm_T_unitCoordinate j

#print axioms T_not_closed_range
#print axioms w_mem_closure_not_range
