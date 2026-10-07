/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroMomentCoefficients

namespace Komorebi.PaperIV
noncomputable section

theorem powerSeries_linear_ode_unique {f g H : PowerSeries ℂ}
    (h0 : f.constantCoeff = g.constantCoeff)
    (hf : PowerSeries.derivative ℂ f = f * H)
    (hg : PowerSeries.derivative ℂ g = g * H) : f = g := by
  ext n
  induction n using Nat.strong_induction_on with
  | h n ih =>
      cases n with
      | zero => simpa only [PowerSeries.coeff_zero_eq_constantCoeff] using h0
      | succ n =>
          have he : PowerSeries.coeff n (PowerSeries.derivative ℂ f) =
              PowerSeries.coeff n (PowerSeries.derivative ℂ g) := by
            rw [hf, hg, PowerSeries.coeff_mul, PowerSeries.coeff_mul]
            apply Finset.sum_congr rfl
            intro p hp
            rw [ih p.1 (by have := Finset.mem_antidiagonal.mp hp; omega)]
          simp only [PowerSeries.coeff_derivative] at he
          exact mul_right_cancel₀ (by exact_mod_cast Nat.succ_ne_zero n : (n + 1 : ℂ) ≠ 0) he

def thetaZeroBellInput (N : ℕ) (u : ℂ) : PowerSeries ℂ :=
  bellInput (fun m => ((m - 1).factorial : ℂ) * (-1 : ℂ) ^ m *
    zeroPowerSum (entireReducedDenominator N) m * (u ^ (N * m) + u))

theorem thetaZeroBellInput_derivative {N : ℕ} (hN : 2 ≤ N) (u : ℂ) :
    PowerSeries.derivative ℂ (thetaZeroBellInput N u) = thetaLogDerivativeSeries N u := by
  ext n
  rw [PowerSeries.coeff_derivative, coeff_thetaLogDerivativeSeries,
    kappaCoeff_eq_zeroPowerSum hN (by omega)]
  simp only [thetaZeroBellInput, bellInput, PowerSeries.coeff_mk, Nat.succ_ne_zero, ↓reduceIte, Nat.add_sub_cancel, Nat.factorial_succ,
    Nat.cast_mul, Nat.cast_add, Nat.cast_one]
  have hn : (n.factorial : ℂ) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
  have hn1 : (n + 1 : ℂ) ≠ 0 := by exact_mod_cast Nat.succ_ne_zero n
  field_simp

theorem thetaSeries_eq_zero_bell_exp {N : ℕ} (hN : 2 ≤ N) (u : ℂ) :
    thetaSeries N u = (PowerSeries.exp ℂ).subst (thetaZeroBellInput N u) := by
  have hB0 : (thetaZeroBellInput N u).constantCoeff = 0 := constantCoeff_bellInput _
  have hB : PowerSeries.HasSubst (thetaZeroBellInput N u) := PowerSeries.HasSubst.of_constantCoeff_zero' hB0
  apply powerSeries_linear_ode_unique (H := thetaLogDerivativeSeries N u)
  · have h0 := thetaOrdCoeff_zero (R := ℂ) N u
    rw [thetaOrdCoeff, PowerSeries.coeff_zero_eq_constantCoeff] at h0
    rw [h0]
    change 1 = MvPowerSeries.constantCoeff ((PowerSeries.exp ℂ).subst (thetaZeroBellInput N u))
    rw [PowerSeries.constantCoeff_subst_of_constantCoeff_zero hB0]
    simp
  · exact derivative_thetaSeries N u
  · rw [PowerSeries.derivative_subst hB,
      PowerSeries.derivative_exp, thetaZeroBellInput_derivative hN]

/-- Proposition 12.8, with the signed zero sums in the displayed Bell input. -/
theorem thetaCoeff_zero_sum_bell {N : ℕ} (hN : 2 ≤ N) (n : ℕ) (u : ℂ) :
    thetaCoeff N n u = ((N * n).factorial : ℂ) / (n.factorial : ℂ) *
      completeExponentialBell n (fun m => ((m - 1).factorial : ℂ) * (-1 : ℂ) ^ m *
        zeroPowerSum (entireReducedDenominator N) m * (u ^ (N * m) + u)) := by
  rw [thetaCoeff, blockCoeff, thetaSeries_eq_zero_bell_exp hN, completeExponentialBell]
  have hn : (n.factorial : ℂ) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
  dsimp [thetaZeroBellInput]
  field_simp

end
end Komorebi.PaperIV
