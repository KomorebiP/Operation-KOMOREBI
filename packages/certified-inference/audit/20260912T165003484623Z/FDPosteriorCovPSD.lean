import Komorebi.FDJointCovAssembly
import Mathlib.Tactic.NoncommRing

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman

open Matrix

variable {ι κ : Type*} [Fintype ι] [Fintype κ]

def josephCovMatrix [DecidableEq ι] [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) : Matrix ι ι ℝ :=
  let K := gainMatrix H P R
  let A := (1 : Matrix ι ι ℝ) - K * H
  A * P * A.transpose + K * R * K.transpose

theorem josephCovMatrix_eq_posteriorCovMatrix
    [DecidableEq ι] [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    josephCovMatrix H P R = posteriorCovMatrix H P R := by
  let K := gainMatrix H P R
  have hcross : P * H.transpose * K.transpose = K * H * P := by
    calc
      P * H.transpose * K.transpose = (K * innovationMatrix H P R) * K.transpose := by
        rw [jointCov_XY H P R hP hR]
      _ = K * innovationMatrix H P R * K.transpose := by rfl
      _ = K * H * P := by
        exact gain_innovation_gain_transpose H P R hP hR
  have hsum :
      K * H * P * H.transpose * K.transpose + K * R * K.transpose = K * H * P := by
    calc
      K * H * P * H.transpose * K.transpose + K * R * K.transpose =
          K * (H * P * H.transpose + R) * K.transpose := by
        simp only [Matrix.mul_add, Matrix.add_mul, Matrix.mul_assoc]
      _ = K * innovationMatrix H P R * K.transpose := by
        rw [innovationMatrix]
      _ = K * H * P := gain_innovation_gain_transpose H P R hP hR
  calc
    josephCovMatrix H P R =
        P - K * H * P - P * H.transpose * K.transpose +
          (K * H * P * H.transpose * K.transpose + K * R * K.transpose) := by
      simp only [josephCovMatrix, K, Matrix.transpose_sub, Matrix.transpose_mul,
        Matrix.transpose_one, Matrix.sub_mul, Matrix.mul_sub, Matrix.one_mul,
        Matrix.mul_one, Matrix.mul_assoc]
      abel
    _ = P - K * H * P := by
      rw [hcross, hsum]
      noncomm_ring
    _ = posteriorCovMatrix H P R := by
      rfl

theorem posteriorCovMatrix_posSemidef
    [DecidableEq ι] [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    (posteriorCovMatrix H P R).PosSemidef := by
  rw [← josephCovMatrix_eq_posteriorCovMatrix H P R hP hR]
  let K := gainMatrix H P R
  let A := (1 : Matrix ι ι ℝ) - K * H
  have hAstar : A.conjTranspose = A.transpose := by
    ext i j
    simp [Matrix.conjTranspose_apply]
  have hKstar : K.conjTranspose = K.transpose := by
    ext i j
    simp [Matrix.conjTranspose_apply]
  have hAP : (A * P * A.transpose).PosSemidef := by
    rw [← hAstar]
    exact hP.mul_mul_conjTranspose_same A
  have hKR : (K * R * K.transpose).PosSemidef := by
    rw [← hKstar]
    exact hR.posSemidef.mul_mul_conjTranspose_same K
  exact hAP.add hKR

end Komorebi.FiniteDimensionalGaussianKalman
