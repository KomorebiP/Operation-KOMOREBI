import KomorebiLSM.RotationApproximation
open Komorebi.LSM Komorebi.LSM.RotationApproximation

/- The exact rotation sends the first diamond vertex outside the diamond. -/
example : operator 1 (false,false) initial ∈ PositiveLift.hull synthesis := by
  rw [diamond_hull]
  norm_num [operator,branchMatrix,rotationMatrix,initial,Matrix.mulVec,dotProduct,
    Fin.sum_univ_succ,Matrix.cons_val_two]
