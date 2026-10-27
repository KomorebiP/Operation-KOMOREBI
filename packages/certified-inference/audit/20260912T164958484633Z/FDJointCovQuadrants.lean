import Komorebi.FDInnovationIdentities

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman

open Matrix

variable {ι κ : Type*} [Fintype ι] [Fintype κ]

omit [Fintype κ] in
theorem jointCov_YY
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) :
    innovationMatrix H P R = innovationMatrix H P R := rfl

/-- XY block: reverse factorization reproduces the forward cross-covariance `P Hᵀ`. -/
theorem jointCov_XY [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    gainMatrix H P R * innovationMatrix H P R = P * H.transpose :=
  gain_mul_innovation H P R hP hR

/-- YX block: reverse factorization reproduces the forward cross-covariance `H P`. -/
theorem jointCov_YX [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    innovationMatrix H P R * (gainMatrix H P R).transpose = H * P :=
  innovation_mul_gain_transpose H P R hP hR

/-- XX block: posterior residual covariance plus explained covariance reconstructs the prior. -/
theorem jointCov_XX [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    gainMatrix H P R * innovationMatrix H P R * (gainMatrix H P R).transpose +
        posteriorCovMatrix H P R = P := by
  rw [gain_innovation_gain_transpose H P R hP hR]
  simp only [posteriorCovMatrix]
  abel

end Komorebi.FiniteDimensionalGaussianKalman
