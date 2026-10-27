import KomorebiLSM.FiniteStochastic
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Tactic.NormNum
open scoped BigOperators
example : (∑ i : Fin 3, if i=2 then (1:ℝ) else 0) = 1 := by
  norm_num [Fin.sum_univ_succ, Fin.reduceEq]
example : (if (0:Fin 3) = 2 then (0:ℝ) else 1/2) = 1/2 := by
  norm_num [Fin.reduceEq]
