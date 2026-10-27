import KomorebiLSM.PolynomialGram
set_option autoImplicit false
open Komorebi.LSM.PolynomialGram
/-- Positive Gram matrices do not certify values outside [-1,1]. -/
example : (intervalGram 1 (0 : Matrix (Fin 2 × Fin 1) (Fin 2 × Fin 1) ℝ)
    (1 : Matrix (Fin 1 × Fin 1) (Fin 1 × Fin 1) ℝ) 2).PosSemidef := by
  have hn : ¬(intervalGram 1 (0 : Matrix (Fin 2 × Fin 1) (Fin 2 × Fin 1) ℝ)
      (1 : Matrix (Fin 1 × Fin 1) (Fin 1 × Fin 1) ℝ) 2).PosSemidef := by
    intro h
    have hd := h.diag_nonneg (i := 0)
    norm_num [intervalGram,powerStack,Matrix.mul_apply,Fintype.sum_prod_type,
      Fin.sum_univ_succ] at hd
  simp only [hn]
