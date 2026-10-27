import KomorebiLSM.FiniteStochastic
import Mathlib.Algebra.BigOperators.Fin
#check Fin.sum_univ_succ
#check Fin.forall_fin_succ
#check Setoid.ker_def
#check Setoid.ker_apply
#check Setoid.ker_rel
#print Setoid.instCoeFun
example (f : Fin 6 → Fin 3) (i j : Fin 6) : Setoid.ker f i j ↔ f i = f j := by rfl
