/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroMomentLogarithm

namespace Komorebi.PaperIV
open Set
noncomputable section

theorem canonicalSignedDenominator_one (z : ℂ) :
    canonicalSignedDenominator 1 z = Complex.exp (-z) := by
  have h := entireSigned_independent_roots (N := 1) (j := 0) (by omega) (by omega)
    (canonicalPrimitiveRoot_isPrimitive (by omega)) IsPrimitiveRoot.one
    (canonicalSignedRoot_pow (by omega)) (show (-1 : ℂ) ^ 1 = -1 by simp) z
  change canonicalSignedDenominator 1 z = _ at h
  simpa [entireSigned, entireTransfer] using h

theorem analyticTransferTangent_one : analyticTransferTangent 1 = fun _ => 1 := by
  have he : canonicalSignedDenominator 1 = fun z => Complex.exp (-z) :=
    funext canonicalSignedDenominator_one
  funext z
  rw [analyticTransferTangent, he, logDeriv_apply]
  have hd : HasDerivAt (fun w : ℂ => Complex.exp (-w)) (-Complex.exp (-z)) z := by
    simpa only [id_eq, mul_neg, mul_one] using ((hasDerivAt_id z).fun_neg.cexp)
  rw [hd.deriv]
  simp [Complex.exp_ne_zero]

theorem transferTangentCoeff_one_order (n : ℕ) :
    transferTangentCoeff (R := ℂ) 1 n = if n = 0 then 1 else 0 := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
    by_cases hn : n = 0
    · subst n
      simp [transferTangentCoeff_zero 1 (by omega)]
    · rw [transferTangentCoeff_recurrence 1 n (by omega)]
      rw [Finset.sum_eq_single n]
      · simp [transferTangentCoeff_zero 1 (by omega), hn]
      · intro k hk hkn
        obtain ⟨hk1, hkn1⟩ := Finset.mem_Ico.mp hk
        have hlt : n - k < n := by omega
        have hne : n - k ≠ 0 := by omega
        simp [ih _ hlt, hne]
      · intro hbad
        exact (hbad (Finset.mem_Ico.mpr (by omega))).elim

theorem analyticTransferTangent_one_hasSum (z : ℂ) :
    HasSum (fun n => transferTangentCoeff (R := ℂ) 1 n /
      ((1 * n + 1 - 1).factorial : ℂ) * z ^ (1 * n + 1 - 1))
      (analyticTransferTangent 1 z) := by
  simp only [analyticTransferTangent_one, transferTangentCoeff_one_order]
  have h := hasSum_single (f := fun n : ℕ =>
    (if n = 0 then (1 : ℂ) else 0) / ((1 * n + 1 - 1).factorial : ℂ) *
      z ^ (1 * n + 1 - 1)) 0 (by intro n hn; simp [hn])
  simpa using h

/-- The actual tangent expansion, including the order-one boundary. -/
theorem analyticTransferTangent_hasSum_all_orders {N : ℕ} (hN : 0 < N) {R : ℝ}
    (hn : ∀ w ∈ Metric.ball (0 : ℂ) R, entireReducedDenominator N w ≠ 0)
    {z : ℂ} (hz : z ^ N ∈ Metric.ball (0 : ℂ) R) :
    HasSum (fun n => transferTangentCoeff (R := ℂ) N n /
      ((N * n + N - 1).factorial : ℂ) * z ^ (N * n + N - 1))
      (analyticTransferTangent N z) := by
  by_cases h : N = 1
  · subst N
    exact analyticTransferTangent_one_hasSum z
  · exact analyticTransferTangent_coefficient_hasSum (by omega) hn hz

end
end Komorebi.PaperIV
