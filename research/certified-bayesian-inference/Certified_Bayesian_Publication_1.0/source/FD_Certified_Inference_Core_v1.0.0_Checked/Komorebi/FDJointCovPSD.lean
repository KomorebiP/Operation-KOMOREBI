import Komorebi.FDPosteriorCovPSD
import Mathlib.Algebra.Order.Star.Real

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman

open Matrix

variable {ι κ : Type*} [Fintype ι] [Fintype κ]

theorem forwardJointCov_posSemidef
    [DecidableEq ι] [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    (forwardJointCov H P R).PosSemidef := by
  have hS : (innovationMatrix H P R).PosDef :=
    innovationMatrix_posDef H P R hP hR
  let _ : Invertible (innovationMatrix H P R) := hS.isUnit.invertible
  have hBstar : (H * P).conjTranspose = P * H.transpose := by
    rw [Matrix.conjTranspose_mul, hP.isHermitian.eq]
    ext i j
    simp
  rw [forwardJointCov, ← hBstar]
  rw [Matrix.PosDef.fromBlocks₁₁ (H * P) P hS]
  have hPt := covariance_symmetric_of_posSemidef P hP
  have hpost := posteriorCovMatrix_posSemidef H P R hP hR
  simpa [posteriorCovMatrix, gainMatrix, Matrix.mul_assoc, hBstar, hPt] using hpost

theorem reverseJointCov_posSemidef
    [DecidableEq ι] [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    (reverseJointCov H P R).PosSemidef := by
  rw [reverseJointCov_eq_forwardJointCov H P R hP hR]
  exact forwardJointCov_posSemidef H P R hP hR

end Komorebi.FiniteDimensionalGaussianKalman
