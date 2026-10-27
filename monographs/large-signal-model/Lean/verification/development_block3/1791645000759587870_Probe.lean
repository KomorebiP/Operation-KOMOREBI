import KomorebiLSM.FiniteStochastic
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Tactic.NormNum
#check Fin.reduceEq
#check Fin.ext_iff
example : (0:Fin 3) ≠ 2 := by norm_num [Fin.ext_iff]
example : (2:Fin 3) ≠ 1 := by decide
