import KomorebiLSM.RotationModel

/- Validity on a curved cone does not make the signed-coordinate matrix
entrywise nonnegative. The actual entry is minus four fifths. -/
example : 0 ≤ Komorebi.LSM.RotationModel.rotationMatrix 1 2 := by
  change 0 ≤ (-4/5:ℝ)
  norm_num
