import Komorebi.FDKalmanDefs

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman

open Matrix

variable {ι κ : Type*} [Fintype ι] [Fintype κ]

theorem innovationMatrix_posDef
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    (innovationMatrix H P R).PosDef := by
  have hHstar : H.conjTranspose = H.transpose := by
    ext i j
    simp [Matrix.conjTranspose_apply]
  have hHPH : (H * P * H.transpose).PosSemidef := by
    rw [← hHstar]
    exact hP.mul_mul_conjTranspose_same H
  exact Matrix.PosDef.posSemidef_add hHPH hR

theorem innovation_inv_mul [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    (innovationMatrix H P R)⁻¹ * innovationMatrix H P R = 1 := by
  apply Matrix.nonsing_inv_mul
  exact (innovationMatrix H P R).isUnit_iff_isUnit_det.mp (innovationMatrix_posDef H P R hP hR).isUnit

theorem innovation_mul_inv [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    innovationMatrix H P R * (innovationMatrix H P R)⁻¹ = 1 := by
  apply Matrix.mul_nonsing_inv
  exact (innovationMatrix H P R).isUnit_iff_isUnit_det.mp (innovationMatrix_posDef H P R hP hR).isUnit

theorem gain_mul_innovation [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    gainMatrix H P R * innovationMatrix H P R = P * H.transpose := by
  rw [gainMatrix, Matrix.mul_assoc]
  rw [innovation_inv_mul H P R hP hR]
  simp

omit [Fintype ι] in
theorem covariance_symmetric_of_posSemidef
    (P : Matrix ι ι ℝ) (hP : P.PosSemidef) : P.transpose = P := by
  have hstar := hP.isHermitian.eq
  simpa [Matrix.conjTranspose_apply] using hstar

omit [Fintype κ] in
theorem innovation_symmetric
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    (innovationMatrix H P R).transpose = innovationMatrix H P R := by
  have hPt := covariance_symmetric_of_posSemidef P hP
  have hRt := covariance_symmetric_of_posSemidef R hR.posSemidef
  simp [innovationMatrix, Matrix.transpose_add, Matrix.transpose_mul, hPt, hRt,
    Matrix.mul_assoc]

theorem innovation_mul_gain_transpose [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    innovationMatrix H P R * (gainMatrix H P R).transpose = H * P := by
  have h := congrArg Matrix.transpose (gain_mul_innovation H P R hP hR)
  have hS := innovation_symmetric H P R hP hR
  have hPt := covariance_symmetric_of_posSemidef P hP
  simpa [Matrix.transpose_mul, hS, hPt] using h

theorem gain_innovation_gain_transpose [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    gainMatrix H P R * innovationMatrix H P R * (gainMatrix H P R).transpose =
      gainMatrix H P R * H * P := by
  rw [Matrix.mul_assoc, innovation_mul_gain_transpose H P R hP hR]
  rw [← Matrix.mul_assoc]

end Komorebi.FiniteDimensionalGaussianKalman
