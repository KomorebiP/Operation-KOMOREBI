import KomorebiLSM.RegressionGeometry
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Tactic

/-! The logarithmic inversion of the actual Gaussian-mixture crossing bound. -/
set_option autoImplicit false
namespace Komorebi.LSM.RegressionConfidence
open Matrix
open scoped BigOperators
variable {I : Type*} [Fintype I] [DecidableEq I]

/-- The literal determinant-dependent noise radius in Proposition81. -/
noncomputable def noiseRadius (γ σ δ : ℝ) (φ : ℕ → I → ℝ) (n : ℕ) : ℝ :=
  σ * Real.sqrt (Real.log ((ridgeMatrix γ φ n).det/(γ • (1 : Matrix I I ℝ)).det)+
    2*Real.log (1/δ))

/-- Below a Gaussian-mixture crossing threshold, taking actual logarithms
bounds the genuine inverse-matrix score norm. -/
theorem mixture_lt_implies_noise_bound (V W : Matrix I I ℝ) (hV : V.PosDef) (hW : W.PosDef)
    (σ δ : ℝ) (hσ : 0 < σ) (hδ : 0 < δ) (score : I → ℝ)
    (h : Real.sqrt (W.det/V.det)*Real.exp ((weightedNorm V⁻¹ score)^2/(2*σ^2))<1/δ) :
    weightedNorm V⁻¹ score ≤
      σ*Real.sqrt (Real.log (V.det/W.det)+2*Real.log (1/δ)) := by
  have hp : 0 < Real.sqrt (W.det/V.det) := Real.sqrt_pos.2 (div_pos hW.det_pos hV.det_pos)
  have ht := (Real.log_lt_log_iff (mul_pos hp (Real.exp_pos _)) (one_div_pos.2 hδ)).2 h
  rw [Real.log_mul (ne_of_gt hp) (Real.exp_ne_zero _),Real.log_exp,
    Real.log_sqrt (div_nonneg hW.det_pos.le hV.det_pos.le),
    Real.log_div (ne_of_gt hW.det_pos) (ne_of_gt hV.det_pos)] at ht
  have hden : 0 < 2*σ^2 := mul_pos (by norm_num) (sq_pos_of_ne_zero (ne_of_gt hσ))
  have ht' : (weightedNorm V⁻¹ score)^2/(2*σ^2) <
      (Real.log V.det-Real.log W.det)/2+Real.log (1/δ) := by linarith
  have hm := (div_lt_iff₀ hden).mp ht'
  have hs : (weightedNorm V⁻¹ score)^2 <
      σ^2*(Real.log (V.det/W.det)+2*Real.log (1/δ)) := by
    rw [Real.log_div (ne_of_gt hV.det_pos) (ne_of_gt hW.det_pos)]
    nlinarith
  have ha : 0 ≤ Real.log (V.det/W.det)+2*Real.log (1/δ) := by
    by_contra hneg
    have hprod := mul_neg_of_pos_of_neg (sq_pos_of_ne_zero (ne_of_gt hσ)) (lt_of_not_ge hneg)
    nlinarith [sq_nonneg (weightedNorm V⁻¹ score)]
  have he : (σ*Real.sqrt (Real.log (V.det/W.det)+2*Real.log (1/δ)))^2 =
      σ^2*(Real.log (V.det/W.det)+2*Real.log (1/δ)) := by
    rw [mul_pow,Real.sq_sqrt ha]
  rw [← he] at hs
  nlinarith [weightedNorm_nonneg V⁻¹ score,
    mul_nonneg hσ.le (Real.sqrt_nonneg (Real.log (V.det/W.det)+2*Real.log (1/δ)))]

end Komorebi.LSM.RegressionConfidence
