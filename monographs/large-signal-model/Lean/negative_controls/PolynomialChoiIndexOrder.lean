import KomorebiLSM.PolynomialGram
set_option autoImplicit false
open Komorebi.LSM.PolynomialGram
private def shift : Matrix (Fin 2) (Fin 2) ℝ := !![0,1;0,0]
/-- Swapping the input and output index convention would falsely erase the
population transferred from input column 1 to output row 0. -/
example : choiAction (fun (s t : Fin 2 × Fin 2) =>
    shift s.1 s.2 * shift t.1 t.2) !![0,0;0,1] 0 0=0 := by
  change (∑ p : Fin 2,∑ q : Fin 2,(shift 0 p * shift 0 q) * (!![0,0;0,1] : Matrix (Fin 2) (Fin 2) ℝ) p q)=0
  norm_num [shift,Fin.sum_univ_succ]
