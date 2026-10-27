import KomorebiLSM.MatrixRotation

/-! Rejected control: the right factor must be W-transpose. Omitting it
already changes the off-diagonal entry at the declared initial state. -/
open Komorebi.LSM
open MatrixRotation

example : embedding (RotationModel.rotate RotationModel.initial)=
    (1/5:ℝ) • (rotationK*embedding RotationModel.initial*rotationK) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [rotationK,rotationKQ,RotationModel.initial,Matrix.mul_apply,
      Fin.sum_univ_succ,Matrix.cons_val_two]
