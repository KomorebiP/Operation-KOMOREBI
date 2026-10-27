import KomorebiLSM.RationalTransform

open Komorebi.LSM.RationalTransform

-- A mass-preserving first row does not make a transform invertible.
example : IsUnit (affineMatrix (fun _ _ => (0 : ℚ))).det := by
  rw [Matrix.det_eq_zero_of_row_eq_zero 1 (by intro j; rfl)]
  norm_num
