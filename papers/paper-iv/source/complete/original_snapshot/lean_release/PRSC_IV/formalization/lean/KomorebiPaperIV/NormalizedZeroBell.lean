/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.NormalizedProduct
import KomorebiPaperIV.AnalyticTaylorDifferential

namespace Komorebi.PaperIV
noncomputable section

theorem normalized_zeroMomentSeries {N : ℕ} (hN : 2 ≤ N) (j : ℕ) :
    zeroMomentSeries (entireNormalizedSection N j) =
      PowerSeries.derivative ℂ (normalizedResidueNegativeLog N j) := by
  have hN0 : 0 < N := by omega
  have hs := entireNormalizedSection_zeroPowerSummable hN0 j
    ((div_lt_one (by positivity : (0 : ℝ) < N)).mpr (by exact_mod_cast (show 1 < N by omega)))
  have h := hadamard_taylor_zeroMoment_identity
    (fun z => (analyticAt_entireNormalizedSection hN0 j z).differentiableAt) hs
    (by rw [entireNormalizedSection_zero]; exact one_ne_zero)
    (entireNormalizedSection_hadamard hN j)
  rw [analyticTaylorSeries_entireNormalizedSection hN0,
    ← normalizedResidueSectionAlg_eq_normalizedResidueSection] at h
  have hunit : IsUnit (normalizedResidueSectionAlg (R := ℂ) N j) :=
    PowerSeries.isUnit_iff_constantCoeff.mpr (by simp)
  apply hunit.mul_left_cancel
  rw [h, normalizedResidueNegativeLog, map_neg, mul_neg,
    mul_derivative_logOf (constantCoeff_normalizedResidueSectionAlg N j)]

theorem normalized_zeroPowerSum {N : ℕ} (hN : 2 ≤ N) (j n : ℕ) :
    zeroPowerSum (entireNormalizedSection N j) (n + 1) =
      PowerSeries.coeff (n + 1) (normalizedResidueNegativeLog (R := ℂ) N j) * (n + 1 : ℂ) := by
  have h := congrArg (PowerSeries.coeff n) (normalized_zeroMomentSeries hN j)
  simpa [zeroMomentSeries, PowerSeries.coeff_derivative] using h

theorem bellInput_normalized_zeros {N : ℕ} (hN : 2 ≤ N) (j : ℕ) (r : ℂ) :
    bellInput (fun m => r * ((m - 1).factorial : ℂ) * zeroPowerSum (entireNormalizedSection N j) m) =
      PowerSeries.C r * normalizedResidueNegativeLog N j := by
  ext m
  cases m with
  | zero => simp [bellInput, PowerSeries.coeff_zero_eq_constantCoeff]
  | succ m =>
    simp only [bellInput, PowerSeries.coeff_mk, Nat.succ_ne_zero, ↓reduceIte,
      Nat.succ_sub_one, normalized_zeroPowerSum hN, PowerSeries.coeff_C_mul]
    rw [Nat.factorial_succ, Nat.cast_mul]
    have hm : (m.factorial : ℂ) ≠ 0 := by exact_mod_cast m.factorial_ne_zero
    have hs : (m.succ : ℂ) ≠ 0 := by exact_mod_cast Nat.succ_ne_zero m
    field_simp
    simp

/-- The exact coefficient normalization in Proposition 12.4, in terms of
the actual nonzero zeros with their analytic multiplicities. -/
theorem residuePowerCoeff_zero_sum_bell {N : ℕ} (hN : 2 ≤ N) (j n : ℕ) (r : ℂ) :
    residuePowerCoeff N j n r = ((N * n).factorial : ℂ) / (n.factorial : ℂ) *
      completeExponentialBell n (fun m => r * ((m - 1).factorial : ℂ) *
        zeroPowerSum (entireNormalizedSection N j) m) := by
  rw [completeExponentialBell, bellInput_normalized_zeros hN, residuePowerCoeff, blockCoeff,
    residuePowerSeries, formalExpFamily_eq_exp_subst (constantCoeff_normalizedResidueNegativeLog N j)]
  have hn : (n.factorial : ℂ) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
  field_simp

end
end Komorebi.PaperIV
