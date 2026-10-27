import Komorebi.FDPosteriorCovPSD

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- Residual of an approximate solve of the Kalman gain equation. -/
def gainResidual (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (B : Matrix ι κ ℝ) : Matrix ι κ ℝ :=
  P * H.transpose - B * innovationMatrix H P R

/-- Joseph covariance for an arbitrary, not necessarily exact, gain. -/
def gainJoseph (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (B : Matrix ι κ ℝ) : Matrix ι ι ℝ :=
  ((1 : Matrix ι ι ℝ) - B*H) * P * ((1 : Matrix ι ι ℝ) - B*H).transpose +
    B * R * B.transpose

omit [DecidableEq κ] in
/-- Every approximate gain produces a valid semidefinite Joseph covariance. -/
theorem gainJoseph_posSemidef (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosSemidef) : (gainJoseph H P R B).PosSemidef := by
  unfold gainJoseph
  simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using
    (hP.mul_mul_conjTranspose_same (1-B*H)).add (hR.mul_mul_conjTranspose_same B)

theorem gainJoseph_exact (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (R : Matrix κ κ ℝ) (hP : P.PosSemidef) (hR : R.PosDef) :
    gainJoseph H P R (gainMatrix H P R) = posteriorCovMatrix H P R := by
  exact josephCovMatrix_eq_posteriorCovMatrix H P R hP hR

omit [DecidableEq ι] [DecidableEq κ] in
/-- Expanded Joseph identity, independent of gain optimality. -/
theorem gainJoseph_expand (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ) [DecidableEq ι] :
    gainJoseph H P R B =
      P - B*H*P - P*H.transpose*B.transpose + B*innovationMatrix H P R*B.transpose := by
  simp only [gainJoseph, innovationMatrix, Matrix.transpose_sub, Matrix.transpose_one,
    Matrix.transpose_mul, Matrix.sub_mul, Matrix.mul_sub, Matrix.one_mul,
    Matrix.mul_one, Matrix.mul_add, Matrix.add_mul, Matrix.mul_assoc]
  abel

omit [DecidableEq ι] in
/-- The residual is exactly the gain discrepancy times the innovation covariance. -/
theorem gainResidual_eq_gap_mul (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ) (hP : P.PosSemidef) (hR : R.PosDef) :
    gainResidual H P R B = (gainMatrix H P R-B)*innovationMatrix H P R := by
  rw [Matrix.sub_mul, gain_mul_innovation H P R hP hR]
  rfl

omit [DecidableEq ι] in
/-- Exact gain error recovered from the residual, without an inverse prior covariance. -/
theorem gain_gap_eq_residual_mul_inv (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ) (hP : P.PosSemidef) (hR : R.PosDef) :
    gainMatrix H P R-B = gainResidual H P R B * (innovationMatrix H P R)⁻¹ := by
  rw [gainResidual_eq_gap_mul H P R B hP hR, Matrix.mul_assoc,
    innovation_mul_inv H P R hP hR, Matrix.mul_one]

/-- The excess Joseph covariance is a positive quadratic gain error. -/
theorem gainJoseph_sub_posterior_eq_gap (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ) (hP : P.PosSemidef) (hR : R.PosDef) :
    gainJoseph H P R B - posteriorCovMatrix H P R =
      (gainMatrix H P R-B)*innovationMatrix H P R*(gainMatrix H P R-B).transpose := by
  rw [gainJoseph_expand, posteriorCovMatrix]
  simp only [Matrix.transpose_sub, Matrix.sub_mul, Matrix.mul_sub]
  rw [gain_innovation_gain_transpose H P R hP hR,
    gain_mul_innovation H P R hP hR,
    Matrix.mul_assoc B (innovationMatrix H P R) (gainMatrix H P R).transpose,
    innovation_mul_gain_transpose H P R hP hR]
  simp only [Matrix.mul_assoc]
  abel

omit [DecidableEq ι] in
/-- Residual form of the covariance cost. -/
theorem residual_cov_eq_gap_cov (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ) (hP : P.PosSemidef) (hR : R.PosDef) :
    gainResidual H P R B * (innovationMatrix H P R)⁻¹ * (gainResidual H P R B).transpose =
      (gainMatrix H P R-B)*innovationMatrix H P R*(gainMatrix H P R-B).transpose := by
  rw [← gain_gap_eq_residual_mul_inv H P R B hP hR,
    gainResidual_eq_gap_mul H P R B hP hR, Matrix.transpose_mul,
    innovation_symmetric H P R hP hR, Matrix.mul_assoc]

theorem gainJoseph_sub_posterior_eq_residual (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ) (hP : P.PosSemidef) (hR : R.PosDef) :
    gainJoseph H P R B - posteriorCovMatrix H P R =
      gainResidual H P R B * (innovationMatrix H P R)⁻¹ * (gainResidual H P R B).transpose := by
  rw [gainJoseph_sub_posterior_eq_gap H P R B hP hR,
    residual_cov_eq_gap_cov H P R B hP hR]

/-- The approximate Joseph covariance dominates the actual posterior covariance. -/
theorem gainJoseph_excess_posSemidef (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ) (hP : P.PosSemidef) (hR : R.PosDef) :
    (gainJoseph H P R B - posteriorCovMatrix H P R).PosSemidef := by
  rw [gainJoseph_sub_posterior_eq_gap H P R B hP hR]
  simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using
    (innovationMatrix_posDef H P R hP hR).posSemidef.mul_mul_conjTranspose_same
      (gainMatrix H P R-B)

end Komorebi.FiniteDimensionalGaussianKalman
