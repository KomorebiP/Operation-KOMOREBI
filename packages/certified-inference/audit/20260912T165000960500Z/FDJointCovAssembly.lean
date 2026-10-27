import Komorebi.FDJointCovQuadrants

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman

open Matrix

variable {ι κ : Type*} [Fintype ι] [Fintype κ]

def forwardJointCov
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) :
    Matrix (κ ⊕ ι) (κ ⊕ ι) ℝ :=
  Matrix.fromBlocks
    (innovationMatrix H P R)
    (H * P)
    (P * H.transpose)
    P

def reverseJointCov [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) :
    Matrix (κ ⊕ ι) (κ ⊕ ι) ℝ :=
  let S := innovationMatrix H P R
  let K := gainMatrix H P R
  let Ppost := posteriorCovMatrix H P R
  Matrix.fromBlocks
    S
    (S * K.transpose)
    (K * S)
    (K * S * K.transpose + Ppost)

theorem reverseJointCov_eq_forwardJointCov [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    reverseJointCov H P R = forwardJointCov H P R := by
  simp only [reverseJointCov, forwardJointCov]
  rw [jointCov_XX H P R hP hR]
  rw [jointCov_YX H P R hP hR]
  rw [jointCov_XY H P R hP hR]

end Komorebi.FiniteDimensionalGaussianKalman
