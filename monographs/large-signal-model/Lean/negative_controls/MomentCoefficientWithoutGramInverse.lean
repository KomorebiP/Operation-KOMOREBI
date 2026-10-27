import KomorebiLSM.FiniteMomentIdentification
open Komorebi.LSM Komorebi.LSM.FiniteMomentIdentification
open scoped BigOperators

/- For B(u)=u, the first moment is 1/3, whereas its linear coefficient is 1.
Discarding the Gram inverse does not reconstruct the declared polynomial. -/
example : momentOperator (r := 1) (D := 1)
    (fun k => if k = 0 then 0 else 1) 1 = (1 : Operator 1) := by
  apply Matrix.ext
  intro i l
  fin_cases i
  fin_cases l
  rw [momentOperator_eq]
  change (mix (UniformIntervalMoments.gram 1)
    (fun k : Fin 2 => if k = 0 then (0 : Operator 1) else 1) 1) 0 0 = 1
  unfold mix
  rw [Fin.sum_univ_two]
  norm_num [ UniformIntervalMoments.gram, Matrix.sum_apply, Matrix.smul_apply,
    smul_eq_mul, Fin.sum_univ_two]
