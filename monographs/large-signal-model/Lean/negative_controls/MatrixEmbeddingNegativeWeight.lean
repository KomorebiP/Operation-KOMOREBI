import KomorebiLSM.MatrixEmbedding

/-! A negative weight destroys the actual PSD congruence certificate. -/
open Komorebi.LSM.MatrixEmbedding.Embedding
example : (weightedCongruence (fun _ : Fin 1 => (-1 : ℝ))
    (fun _ => (1 : Matrix (Fin 1) (Fin 1) ℝ)) 1).PosSemidef := by
  have h : weightedCongruence (fun _ : Fin 1 => (-1 : ℝ))
      (fun _ => (1 : Matrix (Fin 1) (Fin 1) ℝ)) 1 =
      Matrix.diagonal (fun _ : Fin 1 => (-1 : ℝ)) := by
    ext i j
    fin_cases i
    fin_cases j
    norm_num [weightedCongruence, Matrix.mul_apply, Fin.sum_univ_succ]
  rw [h, Matrix.posSemidef_diagonal_iff]
  norm_num
