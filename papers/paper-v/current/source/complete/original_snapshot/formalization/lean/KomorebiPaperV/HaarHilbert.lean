import KomorebiPaperV.HilbertPackets
import Mathlib.Analysis.Real.Sqrt

/-! Author: Komorebi P. Normalized Haar on entire complex l2 channels. -/

namespace KomorebiPaperV.HaarHilbert
open KomorebiPaperV.HilbertPackets

noncomputable def low (x y : Signal ℤ) : Signal ℤ :=
  (Real.sqrt 2)⁻¹ • (x + y)

noncomputable def high (x y : Signal ℤ) : Signal ℤ :=
  (Real.sqrt 2)⁻¹ • (x - y)

theorem inverse_low (x y : Signal ℤ) : low (low x y) (high x y) = x := by
  have hs : (Real.sqrt 2)⁻¹ * (Real.sqrt 2)⁻¹ * 2 = 1 := by
    rw [← mul_inv, Real.mul_self_sqrt (by norm_num)]
    norm_num
  unfold low high
  rw [← smul_add]
  have hab : x + y + (x - y) = (2 : ℝ) • x := by module
  rw [hab, smul_smul, smul_smul, hs, one_smul]

theorem inverse_high (x y : Signal ℤ) : high (low x y) (high x y) = y := by
  have hs : (Real.sqrt 2)⁻¹ * (Real.sqrt 2)⁻¹ * 2 = 1 := by
    rw [← mul_inv, Real.mul_self_sqrt (by norm_num)]
    norm_num
  unfold low high
  rw [← smul_sub]
  have hab : x + y - (x - y) = (2 : ℝ) • y := by module
  rw [hab, smul_smul, smul_smul, hs, one_smul]

theorem energy (x y : Signal ℤ) :
    ‖low x y‖ ^ 2 + ‖high x y‖ ^ 2 = ‖x‖ ^ 2 + ‖y‖ ^ 2 := by
  have hs : ‖(Real.sqrt 2)⁻¹‖ ^ 2 = (1 / 2 : ℝ) := by
    rw [Real.norm_eq_abs, sq_abs, inv_pow, Real.sq_sqrt (by norm_num)]
    norm_num
  dsimp [low, high]
  rw [norm_smul, norm_smul, mul_pow, mul_pow, hs]
  nlinarith [parallelogram_law_with_norm ℂ x y]

theorem low_apply (x y : Signal ℤ) (n : ℤ) :
    low x y n = ((Real.sqrt 2 : ℝ) : ℂ)⁻¹ * (x n + y n) := by
  change (Real.sqrt 2)⁻¹ • (x n + y n) = _
  rw [Complex.real_smul, Complex.ofReal_inv]

theorem high_apply (x y : Signal ℤ) (n : ℤ) :
    high x y n = ((Real.sqrt 2 : ℝ) : ℂ)⁻¹ * (x n - y n) := by
  change (Real.sqrt 2)⁻¹ • (x n - y n) = _
  rw [Complex.real_smul, Complex.ofReal_inv]

end KomorebiPaperV.HaarHilbert
