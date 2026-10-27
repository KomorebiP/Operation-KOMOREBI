import KomorebiLSM.BernsteinCellPositivity

open Komorebi.LSM.TensorBernsteinCertificate Komorebi.LSM.BernsteinCellPositivity

-- The zero polynomial is nonnegative, but its actual zero-width coefficients are not strictly positive.
example : 0 < realCoefficients (0 : Polynomial₂) 0 0 0 0 := by
  rw [realCoefficients_zero_width]
  norm_num [value]
