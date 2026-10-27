import Komorebi.FDGainSampler

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open MeasureTheory ProbabilityTheory Matrix Komorebi.QuadraticTransport
open scoped ENNReal NNReal

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- Exact cost of the actual posterior/approximation coupling, expressed in the gain error. -/
theorem inexactGainCoupling_cost_gap (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosDef) :
    quadraticCost (inexactGainCoupling H m P R B y) =
      ENNReal.ofReal (‖matrixCLM (gainMatrix H P R-B) (y-matrixCLM H m)‖^2 +
        ((gainMatrix H P R-B)*innovationMatrix H P R*(gainMatrix H P R-B).transpose).trace) := by
  unfold inexactGainCoupling gainSample
  rw [affineNoiseSample_coupling_cost P R hP hR.posSemidef,
    gainMean_sub, gainNoiseDifferenceCov]

/-- Exact residual-driven mean-square cost. Neither inverse P nor inverse posterior covariance
is used. The displayed right side is not assumed as a bound on a supplied coupling. -/
theorem inexactGainCoupling_cost_residual (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosDef) :
    quadraticCost (inexactGainCoupling H m P R B y) =
      ENNReal.ofReal
        (‖matrixCLM (gainResidual H P R B * (innovationMatrix H P R)⁻¹)
            (y-matrixCLM H m)‖^2 +
          (gainResidual H P R B * (innovationMatrix H P R)⁻¹ *
            (gainResidual H P R B).transpose).trace) := by
  rw [inexactGainCoupling_cost_gap H m P R B y hP hR,
    ← residual_cov_eq_gap_cov H P R B hP hR,
    gain_gap_eq_residual_mul_inv H P R B hP hR]

/-- A gain-equation residual controls the distribution error of the actual Bayesian posterior. -/
theorem posterior_wasserstein2Sq_le_gain_residual
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosDef) :
    wasserstein2Sq (fdPosteriorKernel H m P R y) (gainPosteriorLaw H m P R B y) ≤
      ENNReal.ofReal
        (‖matrixCLM (gainResidual H P R B * (innovationMatrix H P R)⁻¹)
            (y-matrixCLM H m)‖^2 +
          (gainResidual H P R B * (innovationMatrix H P R)⁻¹ *
            (gainResidual H P R B).transpose).trace) := by
  calc
    _ ≤ quadraticCost (inexactGainCoupling H m P R B y) :=
      wasserstein2Sq_le_cost _ _ _ (inexactGainCoupling_isTransportPlan H m P R B y hP hR)
    _ = _ := inexactGainCoupling_cost_residual H m P R B y hP hR

/-- Zero residual gives the exact posterior version, not merely its moments. -/
theorem gainPosteriorLaw_eq_of_residual_zero
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosDef)
    (hF : gainResidual H P R B = 0) :
    gainPosteriorLaw H m P R B y = fdPosteriorKernel H m P R y := by
  have hg := gain_gap_eq_residual_mul_inv H P R B hP hR
  rw [hF, Matrix.zero_mul] at hg
  have heq : gainMatrix H P R = B := sub_eq_zero.mp hg
  rw [← heq]
  exact gainPosteriorLaw_exact H m P R y hP hR

/-- Finiteness is derived from the displayed finite coupling cost. -/
theorem posterior_wasserstein2Sq_ne_top
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosDef) :
    wasserstein2Sq (fdPosteriorKernel H m P R y) (gainPosteriorLaw H m P R B y) ≠ ⊤ := by
  exact ne_top_of_le_ne_top ENNReal.ofReal_ne_top
    (posterior_wasserstein2Sq_le_gain_residual H m P R B y hP hR)

end Komorebi.FiniteDimensionalGaussianKalman
