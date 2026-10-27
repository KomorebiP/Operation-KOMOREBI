import KomorebiLSM.EuclideanMatrixNorms

open Komorebi.LSM.EuclideanMatrixNorms

-- The identity has spectral norm one, but its actual squared Frobenius norm is two.
example : frobenius (1 : Matrix (Fin 2) (Fin 2) ℝ) ^ 2 = 1 := by
  rw [frobenius_sq]
  norm_num [Fin.sum_univ_two, Matrix.one_apply]
