import KomorebiLSM.MatrixRotation

/-! Rejected control: 1/4 cannot replace the exact congruence weight 1/5,
even at the declared initial state. -/
open scoped Matrix
open Komorebi.LSM
open MatrixRotation

example : embedding (RotationModel.rotate RotationModel.initial)=
    (1/4:ℝ) • (rotationK*embedding RotationModel.initial*rotationKᵀ) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [rotationK,rotationKQ,RotationModel.initial,Matrix.mul_apply,
      Fin.sum_univ_succ,Matrix.cons_val_two]
