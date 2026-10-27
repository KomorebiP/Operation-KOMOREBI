import KomorebiLSM.AveragedCongruence

open Komorebi.LSM.AveragedCongruence
open MeasureTheory

/- The scalar affine family K(u)=u on the uniform unit interval has covariance
correction 1/12. Discarding that correction must fail. -/
example :
    matrixMean (ν := uniformInterval 0 1) (fun u =>
      (((0 : Matrix (Fin 1) (Fin 1) ℝ) + u • 1) -
        matrixMean (ν := uniformInterval 0 1) (fun v => (0 : Matrix (Fin 1) (Fin 1) ℝ) + v • 1)) * 1 *
      (((0 : Matrix (Fin 1) (Fin 1) ℝ) + u • 1) -
        matrixMean (ν := uniformInterval 0 1) (fun v => (0 : Matrix (Fin 1) (Fin 1) ℝ) + v • 1)).transpose) = 0 := by
  rw [uniformInterval_affine_correction (by norm_num)]
  norm_num [Matrix.ext_iff, Matrix.one_apply]
